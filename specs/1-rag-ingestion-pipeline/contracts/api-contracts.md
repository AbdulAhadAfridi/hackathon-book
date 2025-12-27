# API Contracts: RAG Ingestion Pipeline

## Overview

This document defines the API contracts for the RAG ingestion pipeline, including function interfaces and data contracts between components.

## Core Pipeline Functions

### `crawl_website(url: str, max_pages: int = 1000) -> List[Page]`

Crawls a website starting from the given URL and discovers all accessible pages.

**Parameters**:
- `url` (string): Root URL to start crawling from
- `max_pages` (int, optional): Maximum number of pages to crawl (default 1000)

**Returns**:
- `List[Page]`: List of discovered pages with URL and HTML content

**Page Object**:
```json
{
  "url": "string",
  "title": "string",
  "html_content": "string",
  "status_code": "int"
}
```

**Errors**:
- `InvalidURLError`: If the provided URL is malformed
- `CrawlError`: If the website cannot be accessed or crawled

---

### `extract_content(page: Page) -> ContentDocument`

Extracts clean text content from a web page.

**Parameters**:
- `page` (Page): The page object containing HTML content

**Returns**:
- `ContentDocument`: Extracted content with metadata

**Errors**:
- `ContentExtractionError`: If content cannot be extracted from the page

---

### `chunk_content(document: ContentDocument, chunk_size: int = 1000, chunk_overlap: int = 100) -> List[ContentChunk]`

Splits content into appropriately sized chunks for embedding.

**Parameters**:
- `document` (ContentDocument): The content document to chunk
- `chunk_size` (int, optional): Size of each chunk in characters (default 1000)
- `chunk_overlap` (int, optional): Overlap between chunks in characters (default 100)

**Returns**:
- `List[ContentChunk]`: List of content chunks

**Errors**:
- `ChunkingError`: If content cannot be properly chunked

---

### `generate_embeddings(chunks: List[ContentChunk], cohere_api_key: str) -> List[EmbeddingRecord]`

Generates embeddings for content chunks using Cohere API.

**Parameters**:
- `chunks` (List[ContentChunk]): List of content chunks to embed
- `cohere_api_key` (string): Cohere API key for authentication

**Returns**:
- `List[EmbeddingRecord]`: List of embedding records with vectors and metadata

**Errors**:
- `EmbeddingAPIError`: If Cohere API call fails
- `RateLimitError`: If rate limits are exceeded

---

### `store_embeddings(embeddings: List[EmbeddingRecord], qdrant_config: QdrantConfig) -> StorageResult`

Stores embeddings in Qdrant vector database.

**Parameters**:
- `embeddings` (List[EmbeddingRecord]): List of embeddings to store
- `qdrant_config` (QdrantConfig): Configuration for Qdrant connection

**Returns**:
- `StorageResult`: Result of the storage operation

**QdrantConfig Object**:
```json
{
  "url": "string",
  "api_key": "string",
  "collection_name": "string"
}
```

**StorageResult Object**:
```json
{
  "success_count": "int",
  "failed_count": "int",
  "total_count": "int",
  "errors": "List[StorageError]"
}
```

**Errors**:
- `StorageError`: If storage operation fails

---

### `main(website_url: str, cohere_api_key: str, qdrant_config: QdrantConfig, chunk_size: int = 1000, chunk_overlap: int = 100) -> CrawlSession`

Main orchestration function that runs the complete pipeline.

**Parameters**:
- `website_url` (string): URL of the website to process
- `cohere_api_key` (string): Cohere API key
- `qdrant_config` (QdrantConfig): Qdrant configuration
- `chunk_size` (int, optional): Size of content chunks (default 1000)
- `chunk_overlap` (int, optional): Overlap between chunks (default 100)

**Returns**:
- `CrawlSession`: Session object with processing results

## Data Contracts

### ContentDocument Contract
```json
{
  "url": "string (required)",
  "title": "string (required)",
  "content": "string (required)",
  "headings": "List[string] (optional)",
  "section": "string (optional)",
  "created_at": "datetime (required)"
}
```

### ContentChunk Contract
```json
{
  "id": "string (required)",
  "content_document_id": "string (required)",
  "text": "string (required)",
  "chunk_index": "int (required)",
  "metadata": "dict (required)",
  "created_at": "datetime (required)"
}
```

### EmbeddingRecord Contract
```json
{
  "id": "string (required)",
  "content_chunk_id": "string (required)",
  "vector": "List[float] (required)",
  "metadata": "dict (required)",
  "created_at": "datetime (required)"
}
```

### CrawlSession Contract
```json
{
  "id": "string (required)",
  "website_url": "string (required)",
  "start_time": "datetime (required)",
  "end_time": "datetime (optional)",
  "processed_urls": "List[string] (optional)",
  "failed_urls": "List[string] (optional)",
  "total_chunks": "int (optional)",
  "total_embeddings": "int (optional)",
  "status": "string (required)",
  "error_details": "string (optional)"
}
```

## Error Contracts

### Standard Error Format
```json
{
  "error_code": "string",
  "message": "string",
  "details": "object (optional)"
}
```

### Specific Error Types
- `InvalidURLError`: Raised when a URL is malformed
- `CrawlError`: Raised when crawling fails
- `ContentExtractionError`: Raised when content extraction fails
- `ChunkingError`: Raised when chunking fails
- `EmbeddingAPIError`: Raised when embedding API call fails
- `RateLimitError`: Raised when API rate limits are exceeded
- `StorageError`: Raised when storage operation fails