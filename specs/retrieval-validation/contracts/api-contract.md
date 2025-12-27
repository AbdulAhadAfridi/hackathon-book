# API Contract: Retrieval Pipeline Validation and Testing

## Overview
This document defines the API contracts for the retrieval pipeline validation and testing system. The system provides semantic search capabilities against a Qdrant vector store using Cohere embeddings.

## Endpoints

### 1. Retrieve Similar Chunks
**Endpoint:** `retrieve_similar_chunks(query: str, top_k: int = 5, filters: dict = None) -> RetrievalResponse`

**Description:** Performs semantic similarity search against the Qdrant collection using a query string and returns the most similar content chunks.

**Parameters:**
- `query` (str, required): Input text to find similar content for
- `top_k` (int, optional, default: 5): Number of top results to return (1-100)
- `filters` (dict, optional): Optional metadata filters for targeted search

**Returns:**
- `RetrievalResponse`: Object containing search results and metadata

**Example Request:**
```python
response = retrieve_similar_chunks(
    query="How to configure the API settings?",
    top_k=3,
    filters={"section": "configuration"}
)
```

**Example Response:**
```json
{
  "query": "How to configure the API settings?",
  "results": [
    {
      "id": "uuid-123",
      "score": 0.85,
      "payload": {
        "url": "https://example.com/docs/api-config",
        "section": "configuration",
        "heading": "API Configuration Guide",
        "chunk_index": 2,
        "content_chunk_id": "chunk-456"
      },
      "text": "To configure the API settings, you need to set the following environment variables..."
    }
  ],
  "query_embedding": [0.1, 0.2, ...], // 1024-dimensional vector
  "execution_time": 0.25
}
```

**Error Responses:**
- `ValueError`: If query is empty or invalid
- `ConnectionError`: If unable to connect to Qdrant
- `RuntimeError`: If retrieval fails

### 2. Validate Pipeline
**Endpoint:** `validate_pipeline(query: str, expected_urls: List[str] = None) -> dict`

**Description:** Validates the retrieval pipeline with a test query and optionally compares results against expected URLs.

**Parameters:**
- `query` (str, required): Test query to validate retrieval
- `expected_urls` (List[str], optional): List of expected document URLs to be retrieved

**Returns:**
- `dict`: Object containing validation results and metrics

**Example Request:**
```python
result = validate_pipeline(
    query="What is the authentication process?",
    expected_urls=["https://example.com/docs/auth", "https://example.com/docs/security"]
)
```

**Example Response:**
```json
{
  "query": "What is the authentication process?",
  "expected_urls": ["https://example.com/docs/auth", "https://example.com/docs/security"],
  "retrieved_urls": ["https://example.com/docs/auth", "https://example.com/docs/security", "https://example.com/docs/api-config"],
  "match_count": 2,
  "total_retrieved": 3,
  "precision": 0.67,
  "validation_passed": true,
  "details": {
    "retrieved_chunks": [...],
    "execution_time": 0.35
  }
}
```

## Data Models

### SearchResult
**Description:** Represents a single search result from the Qdrant similarity search

**Fields:**
- `id` (str): Qdrant point ID
- `score` (float): Similarity score (0.0 to 1.0)
- `payload` (dict): Metadata dictionary
  - `url` (str): Document URL
  - `section` (str): Document section
  - `heading` (str): Content heading
  - `chunk_index` (int): Chunk index in document
  - `content_chunk_id` (str): Content chunk identifier
- `text` (str): Original content text

### RetrievalRequest
**Description:** Represents a request for content retrieval

**Fields:**
- `query` (str): Input query text
- `top_k` (int): Number of results to return (default: 5)
- `filters` (dict): Metadata filters

### RetrievalResponse
**Description:** Response from a retrieval request

**Fields:**
- `query` (str): Original query text
- `results` (List[SearchResult]): Retrieved content chunks
- `query_embedding` (List[float]): Generated query embedding (1024-dim)
- `execution_time` (float): Time taken for retrieval

## Validation Rules

### Input Validation
1. Query text must not be empty or None
2. top_k must be between 1 and 100 inclusive
3. Filters must contain valid metadata field names
4. Query text must be within Cohere API limits

### Output Validation
1. Results must be ordered by similarity score (descending)
2. Query embedding must be 1024-dimensional
3. Similarity scores must be between 0.0 and 1.0
4. Metadata fields must match ingestion pipeline format

## Error Handling

### Expected Error Conditions
- `ValueError`: Invalid input parameters
- `ConnectionError`: Unable to connect to Qdrant
- `AuthenticationError`: Invalid Qdrant API key
- `RuntimeError`: General retrieval failure

### Error Response Format
```json
{
  "error": {
    "type": "ErrorType",
    "message": "Descriptive error message",
    "details": "Additional error details"
  }
}
```

## Performance Requirements
- Query processing must complete within 5 seconds
- System must support concurrent retrieval requests
- Response time should be consistent regardless of query complexity

## Security Requirements
- API keys must not be exposed in error messages
- No sensitive data in logs or responses
- Proper authentication for Qdrant and Cohere APIs