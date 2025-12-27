# Data Model: Retrieval Pipeline Validation and Testing

## Entity: SearchResult
**Description:** Represents a single search result from the Qdrant similarity search

**Fields:**
- `id` (str): Qdrant point ID - unique identifier for the vector in the collection
- `score` (float): Similarity score between 0.0 and 1.0, where higher values indicate greater similarity
- `payload` (dict): Metadata dictionary containing document information
  - `url` (str): URL of the original document
  - `section` (str): Section of the document
  - `heading` (str): Heading/title of the content chunk
  - `chunk_index` (int): Index position of the chunk in the original document
  - `content_chunk_id` (str): Unique identifier for the content chunk
- `text` (str): Original content text of the chunk

**Validation Rules:**
- `score` must be between 0.0 and 1.0 inclusive
- `payload` must contain all required metadata fields
- `text` must not be empty

**Relationships:** None

**State Transitions:** Immutable once created

## Entity: RetrievalRequest
**Description:** Represents a request for content retrieval from the vector store

**Fields:**
- `query` (str): Input text to find similar content for
- `top_k` (int): Number of top results to return (default: 5, minimum: 1, maximum: 100)
- `filters` (dict): Optional metadata filters for targeted search

**Validation Rules:**
- `query` must not be empty or None
- `top_k` must be between 1 and 100 inclusive
- `filters` keys must match supported metadata fields

**Relationships:** None

**State Transitions:** Immutable once created

## Entity: RetrievalResponse
**Description:** Represents the response from a content retrieval request

**Fields:**
- `query` (str): Original query text that was processed
- `results` (List[SearchResult]): List of retrieved content chunks, ordered by similarity score (descending)
- `query_embedding` (List[float]): The 1024-dimensional embedding vector generated from the query
- `execution_time` (float): Time taken for retrieval in seconds

**Validation Rules:**
- `results` must be ordered by score in descending order
- `query_embedding` must be 1024-dimensional (matching Cohere embed-english-v3.0 output)
- `execution_time` must be non-negative

**Relationships:** Contains multiple SearchResult entities

**State Transitions:** Immutable once created

## Entity: EmbeddingRecord (Reference)
**Description:** Existing entity from ingestion pipeline, referenced for compatibility

**Fields:**
- `content_chunk_id` (str): Unique identifier for the content chunk
- `vector` (List[float]): 1024-dimensional embedding vector
- `metadata` (dict): Metadata dictionary with url, section, heading, chunk_index

**Validation Rules:**
- `vector` must be 1024-dimensional
- `metadata` must contain required fields

**Relationships:** Referenced by SearchResult as source of truth for metadata format

## Entity: ContentChunk (Reference)
**Description:** Existing entity from ingestion pipeline, referenced for metadata consistency

**Fields:**
- `content_document_id` (str): ID of the source document
- `text` (str): Content text
- `chunk_index` (int): Index in the document
- `metadata` (dict): Metadata with url, section, heading, chunk_index

**Validation Rules:**
- Used as reference for metadata structure consistency

**Relationships:** Referenced by EmbeddingRecord and SearchResult for metadata format

## Data Flow Relationships

1. **Query Input** → **RetrievalRequest** → **Embedding Generation** → **Qdrant Search** → **SearchResult** → **RetrievalResponse**

2. **Existing EmbeddingRecord** → **Metadata Schema Reference** → **SearchResult Payload Structure**

## Constraints

1. **Vector Dimensionality:** All embeddings must be 1024-dimensional to match Cohere embed-english-v3.0 output and Qdrant collection schema
2. **Similarity Score Range:** Scores must be between 0.0 and 1.0 for cosine similarity
3. **Metadata Consistency:** Metadata fields must match between ingestion and retrieval pipelines
4. **Query Length Limits:** Query text should be within Cohere API limits (typically under 4096 tokens)
5. **Result Count Limits:** Maximum number of results should be reasonable (max 100) to prevent excessive response times