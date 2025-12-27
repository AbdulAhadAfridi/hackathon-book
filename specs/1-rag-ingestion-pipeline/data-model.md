# Data Model: RAG Ingestion Pipeline

## Entities

### ContentDocument
Represents extracted content from a web page

**Attributes**:
- `url` (string): Source URL of the page
- `title` (string): Page title extracted from HTML
- `content` (string): Clean extracted text content
- `headings` (list of strings): List of headings in document order
- `section` (string): Current section context
- `created_at` (datetime): Timestamp when content was extracted

**Validation**:
- `url` must be a valid URL format
- `content` must not be empty
- `created_at` defaults to current timestamp

### ContentChunk
Represents a chunk of content that will be embedded

**Attributes**:
- `id` (string): Unique identifier for this chunk
- `content_document_id` (string): Reference to parent ContentDocument
- `text` (string): The chunk text content
- `chunk_index` (int): Index of this chunk within the document
- `metadata` (dict): Additional metadata (URL, section, heading, etc.)
- `created_at` (datetime): Timestamp when chunk was created

**Validation**:
- `text` must not exceed Cohere token limits
- `chunk_index` must be non-negative
- `metadata` must contain required fields (url, section, heading, chunk_index)

### EmbeddingRecord
Represents a vector embedding with associated metadata

**Attributes**:
- `id` (string): Unique identifier for this record
- `content_chunk_id` (string): Reference to parent ContentChunk
- `vector` (list of floats): The embedding vector from Cohere
- `metadata` (dict): Metadata to store with the vector
- `created_at` (datetime): Timestamp when embedding was generated

**Validation**:
- `vector` must match expected dimensions from Cohere model
- `metadata` must contain required fields for retrieval

### CrawlSession
Represents a single execution of the crawling process

**Attributes**:
- `id` (string): Unique identifier for the session
- `website_url` (string): Root URL that was crawled
- `start_time` (datetime): When the crawl started
- `end_time` (datetime): When the crawl ended
- `processed_urls` (list of strings): URLs successfully processed
- `failed_urls` (list of strings): URLs that failed processing
- `total_chunks` (int): Total number of chunks created
- `total_embeddings` (int): Total number of embeddings stored
- `status` (string): Current status (running, completed, failed)
- `error_details` (string): Error message if status is failed

**Validation**:
- `start_time` must be before `end_time` if session completed
- `status` must be one of: 'running', 'completed', 'failed'
- `website_url` must be a valid URL

## Relationships

```
CrawlSession (1) → (0..n) ContentDocument
ContentDocument (1) → (0..n) ContentChunk
ContentChunk (1) → (0..1) EmbeddingRecord
```

## State Transitions

### CrawlSession
```
Initial → Running → Completed | Failed
```

## Schema Examples

### ContentDocument Example
```json
{
  "id": "doc_abc123",
  "url": "https://example.com/docs/introduction",
  "title": "Introduction - My Book",
  "content": "This is the introduction to my book...",
  "headings": ["Introduction", "What You'll Learn"],
  "section": "Getting Started",
  "created_at": "2025-12-24T10:00:00Z"
}
```

### ContentChunk Example
```json
{
  "id": "chunk_def456",
  "content_document_id": "doc_abc123",
  "text": "This is the first part of the introduction where we discuss the main concepts...",
  "chunk_index": 0,
  "metadata": {
    "url": "https://example.com/docs/introduction",
    "section": "Getting Started",
    "heading": "Introduction",
    "chunk_index": 0
  },
  "created_at": "2025-12-24T10:01:00Z"
}
```

### EmbeddingRecord Example
```json
{
  "id": "emb_ghi789",
  "content_chunk_id": "chunk_def456",
  "vector": [0.12, -0.45, 0.89, ...],
  "metadata": {
    "url": "https://example.com/docs/introduction",
    "section": "Getting Started",
    "heading": "Introduction",
    "chunk_index": 0
  },
  "created_at": "2025-12-24T10:02:00Z"
}
```

### CrawlSession Example
```json
{
  "id": "session_jkl012",
  "website_url": "https://example.com/docs",
  "start_time": "2025-12-24T10:00:00Z",
  "end_time": "2025-12-24T10:05:00Z",
  "processed_urls": [
    "https://example.com/docs/introduction",
    "https://example.com/docs/chapter1"
  ],
  "failed_urls": [],
  "total_chunks": 25,
  "total_embeddings": 25,
  "status": "completed",
  "error_details": null
}
```