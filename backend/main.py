#!/usr/bin/env python3
"""
RAG Ingestion Pipeline
Main entry point for the RAG backend ingestion pipeline for Docusaurus-based book
"""

import logging
import sys
import argparse
import time
from typing import Optional, List

from crawler import crawl_website
from extractor import extract_content
from models import ContentDocument, ContentChunk, EmbeddingRecord, CrawlSession
from chunker import create_chunks_from_document
from embedding_client import generate_embeddings
from vector_store import store_embeddings_in_qdrant
from config import Config
from utils import validate_url_input


def setup_logging(level: str = "INFO") -> None:
    """
    Set up basic logging configuration
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """
    Main function for the RAG ingestion pipeline
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='RAG Ingestion Pipeline')
    parser.add_argument('--website-url', required=True, help='URL of the website to crawl')
    parser.add_argument('--chunk-size', type=int, default=25000, help='Size of content chunks')
    parser.add_argument('--chunk-overlap', type=int, default=500, help='Overlap between chunks')
    parser.add_argument('--max-pages', type=int, default=1000, help='Maximum number of pages to crawl')

    args = parser.parse_args()

    # Validate URL input
    is_valid, error_msg = validate_url_input(args.website_url)
    if not is_valid:
        logger.error(f"Invalid URL provided: {error_msg}")
        sys.exit(1)

    start_time = time.time()
    logger.info(f"RAG Ingestion Pipeline starting for {args.website_url}...")

    # Create and initialize CrawlSession
    crawl_session = CrawlSession(website_url=args.website_url)
    logger.info(f"Started crawl session: {crawl_session.id}")

    try:
        # Validate configuration
        if not Config.validate():
            logger.error("Configuration validation failed. Please check your environment variables.")
            crawl_session.complete(status="failed", error_details="Configuration validation failed")
            sys.exit(1)

        # Crawl the website
        logger.info("Starting website crawl...")
        pages = crawl_website(args.website_url, max_pages=args.max_pages)
        logger.info(f"Crawled {len(pages)} pages successfully")

        # Extract content from each page
        content_documents: List[ContentDocument] = []
        for i, page in enumerate(pages):
            logger.info(f"Processing page {i+1}/{len(pages)}: {page.url}")

            try:
                content_doc = extract_content(page.html_content, page.url)
                content_documents.append(content_doc)
                crawl_session.processed_urls.append(page.url)
            except Exception as e:
                logger.warning(f"Failed to extract content from {page.url}: {str(e)}")
                crawl_session.failed_urls.append(page.url)
                continue

        logger.info(f"Extracted content from {len(content_documents)} pages")

        # Chunk the content
        logger.info("Starting content chunking...")
        all_chunks = []

        for i, doc in enumerate(content_documents):
            logger.debug(f"Chunking document {i+1}/{len(content_documents)}: {doc.url}")
            chunks = create_chunks_from_document(doc, args.chunk_size, args.chunk_overlap)
            all_chunks.extend(chunks)

        logger.info(f"Created {len(all_chunks)} content chunks")
        crawl_session.total_chunks = len(all_chunks)

        # Generate embeddings for all chunks
        logger.info("Starting embedding generation...")
        texts_to_embed = [chunk.text for chunk in all_chunks]

        # Process in batches to avoid API limits
        batch_size = 96  # Cohere has limits on batch sizes
        all_embeddings = []

        for i in range(0, len(texts_to_embed), batch_size):
            batch = texts_to_embed[i:i+batch_size]
            logger.info(f"Processing embedding batch {i//batch_size + 1}/{(len(texts_to_embed)-1)//batch_size + 1}")

            try:
                batch_embeddings = generate_embeddings(batch)
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Failed to generate embeddings for batch {i//batch_size + 1}: {str(e)}")
                # Continue with the next batch instead of failing the entire process
                continue

        # Create embedding records
        logger.info("Creating embedding records...")
        embedding_records = []
        for chunk, embedding in zip(all_chunks, all_embeddings):
            record = EmbeddingRecord(
                content_chunk_id=chunk.id,
                vector=embedding,
                metadata=chunk.metadata
            )
            embedding_records.append(record)

        logger.info(f"Created {len(embedding_records)} embedding records")

        # Store embeddings in vector store
        logger.info("Starting vector storage...")
        storage_result = store_embeddings_in_qdrant(
            embedding_records,
            url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY
        )

        logger.info(f"Storage completed: {storage_result['success_count']} successful, "
                   f"{storage_result['failed_count']} failed")

        crawl_session.total_embeddings = storage_result['success_count']

        logger.info("RAG Ingestion Pipeline completed successfully")
        crawl_session.complete(status="completed")

    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        crawl_session.complete(status="failed", error_details="Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"RAG Ingestion Pipeline failed: {str(e)}")
        crawl_session.complete(status="failed", error_details=str(e))
        sys.exit(1)

    # Calculate performance metrics
    end_time = time.time()
    total_duration = end_time - start_time
    pages_processed = len(crawl_session.processed_urls)
    pages_per_minute = (pages_processed / total_duration) * 60 if total_duration > 0 else 0

    # Print session summary with performance metrics
    logger.info(f"Session Summary - Processed: {len(crawl_session.processed_urls)}, "
                f"Failed: {len(crawl_session.failed_urls)}, "
                f"Chunks: {crawl_session.total_chunks}, "
                f"Embeddings: {crawl_session.total_embeddings}")
    logger.info(f"Performance - Duration: {total_duration:.2f}s, "
                f"Pages/minute: {pages_per_minute:.2f}")


if __name__ == "__main__":
    main()