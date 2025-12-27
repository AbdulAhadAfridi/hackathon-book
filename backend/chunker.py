"""
Content chunker for the RAG ingestion pipeline
"""

import re
from typing import List
from models import ContentDocument, ContentChunk


def chunk_content(document: ContentDocument, size: int = 1000, overlap: int = 100) -> List[ContentChunk]:
    """
    Split content into appropriately sized chunks with overlap
    """
    text = document.content
    chunks = []

    # Use recursive character splitting with overlap
    start_idx = 0
    chunk_idx = 0

    while start_idx < len(text):
        # Determine the end index for this chunk
        end_idx = start_idx + size

        # If this is not the last chunk, try to break at a sentence or word boundary
        if end_idx < len(text):
            # Look for a good breaking point (sentence or word boundary)
            search_start = end_idx - overlap
            break_point = end_idx

            # Try to find a sentence boundary
            sentence_boundary_found = False
            for i in range(end_idx, search_start, -1):
                if text[i] in '.!?':
                    break_point = i + 1
                    sentence_boundary_found = True
                    break

            if not sentence_boundary_found:
                # If no sentence boundary found, try word boundary
                word_boundary_found = False
                for i in range(end_idx, search_start, -1):
                    if text[i] in ' \t\n':
                        break_point = i
                        word_boundary_found = True
                        break

                if not word_boundary_found:
                    # If no good break point found, just break at the size limit
                    break_point = end_idx
        else:
            # This is the last chunk
            break_point = len(text)

        # Extract the chunk text
        chunk_text = text[start_idx:break_point]

        # Create metadata for this chunk
        chunk_metadata = {
            "url": document.url,
            "section": document.section,
            "heading": document.headings[0] if document.headings else "",
            "chunk_index": chunk_idx
        }

        # Create ContentChunk object
        chunk = ContentChunk(
            content_document_id=document.url,  # Using URL as document ID
            text=chunk_text,
            chunk_index=chunk_idx,
            metadata=chunk_metadata
        )

        chunks.append(chunk)

        # Move to the next chunk position
        start_idx = break_point - overlap if break_point - overlap > start_idx else break_point
        chunk_idx += 1

    return chunks


def create_chunks_from_document(document: ContentDocument, chunk_size: int = 1000, chunk_overlap: int = 100) -> List[ContentChunk]:
    """
    Create content chunks from a ContentDocument with preserved document structure in metadata
    """
    # Create exactly 6 chunks by dividing the content evenly
    text = document.content
    total_length = len(text)
    chunk_size = max(1, total_length // 6)  # Ensure at least 1 character per chunk
    overlap = min(chunk_overlap, chunk_size // 4)  # Limit overlap to 25% of chunk size

    return chunk_content(document, size=chunk_size, overlap=overlap)


def recursive_character_splitting(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into chunks using recursive character splitting with overlap
    """
    chunks = []
    start_idx = 0

    while start_idx < len(text):
        # Determine the end index for this chunk
        end_idx = start_idx + chunk_size

        # If we're near the end, take the remaining text
        if end_idx >= len(text):
            chunks.append(text[start_idx:])
            break

        # Try to find a good breaking point
        break_point = end_idx
        search_start = max(start_idx, end_idx - overlap - 50)  # Look back a bit more than overlap

        # Look for a good breaking point (sentence or word boundary)
        for i in range(end_idx, search_start, -1):
            if text[i] in '.!?':
                break_point = i + 1
                break
        else:
            # If no sentence boundary found, try word boundary
            for i in range(end_idx, search_start, -1):
                if text[i] in ' \t\n':
                    break_point = i
                    break
            else:
                # If no good break point found, just break at the size limit
                break_point = end_idx

        # Extract the chunk
        chunk = text[start_idx:break_point]
        chunks.append(chunk)

        # Move to the next chunk position
        start_idx = break_point - overlap if break_point - overlap > start_idx else break_point

    return chunks