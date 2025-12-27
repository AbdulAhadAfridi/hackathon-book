# Research: RAG Ingestion Pipeline

## Decision Log

### Cohere Embedding Model Selection

**Decision**: Use Cohere's `embed-english-v3.0` model for text embeddings

**Rationale**:
- Specifically designed for text content like book chapters
- High performance for semantic search applications
- Good balance of quality and cost
- Well-documented and stable API

**Alternatives considered**:
- `multilingual-22-12`: For multilingual content (not needed for this use case)
- OpenAI embeddings: Would require different API integration
- Sentence Transformers: Self-hosted option but adds complexity

### Qdrant Cloud Setup

**Decision**: Use Qdrant Cloud with API key authentication

**Rationale**:
- Managed service reduces operational overhead
- Good performance for vector search
- Supports metadata storage required by spec
- Free tier sufficient for initial development

**Configuration**:
- URL format: `https://<cluster-id>.<region>.qdrant.tech:6333`
- API key for authentication
- Collection will be created with metadata schema

### Docusaurus Content Extraction

**Decision**: Use BeautifulSoup with custom selectors for Docusaurus sites

**Rationale**:
- Docusaurus follows predictable HTML structure
- Can target specific content containers while avoiding navigation
- Robust and well-maintained library

**Approach**:
- Target `main[class*="main"]` or `article` elements
- Extract text while preserving heading hierarchy
- Ignore navigation, headers, footers, and sidebars

### Content Chunking Strategy

**Decision**: Recursive character splitting with overlap, targeting 1000 characters with 100 character overlap

**Rationale**:
- Cohere models handle up to 4096 tokens, ~1000 chars is safe
- Overlap preserves context across chunk boundaries
- Simple and effective for book content

**Parameters**:
- Chunk size: 1000 characters
- Overlap: 100 characters
- Preserve document structure in metadata

### Web Crawling Approach

**Decision**: Use requests with robots.txt respect and rate limiting

**Rationale**:
- Simple and effective for Docusaurus sites
- Can handle various HTTP status codes appropriately
- Allows for custom retry logic

**Implementation**:
- Use breadth-first search from root URL
- Respect robots.txt and crawl delays
- Handle common HTTP errors with retries

## Configuration Approach

**Decision**: Support both environment variables and command-line arguments

**Rationale**:
- Environment variables for sensitive data (API keys)
- CLI args for configuration parameters
- .env file for local development

**Configuration parameters**:
- `COHERE_API_KEY`: Cohere API key (required, env var)
- `QDRANT_URL`: Qdrant Cloud URL (required, env var)
- `QDRANT_API_KEY`: Qdrant API key (required, env var)
- `WEBSITE_URL`: Target website URL (required, CLI arg or env var)
- `CHUNK_SIZE`: Chunk size in characters (optional, default 1000)
- `CHUNK_OVERLAP`: Chunk overlap in characters (optional, default 100)

## Error Handling Strategy

**Decision**: Comprehensive error handling with retry logic and graceful degradation

**Rationale**:
- Web crawling inherently has network failures
- API calls may fail due to rate limits or service issues
- Need to continue processing when individual items fail

**Approach**:
- Retry failed URLs with exponential backoff
- Skip failed pages but continue processing others
- Log errors with sufficient detail for debugging
- Report summary of failures at completion

## Progress Tracking

**Decision**: Use logging with configurable levels and summary reports

**Rationale**:
- Need visibility into long-running processes
- Should be able to monitor progress without overwhelming output
- Summary information useful for monitoring and debugging

**Implementation**:
- Log level configuration (DEBUG, INFO, WARN, ERROR)
- Progress updates every N URLs processed
- Summary report at completion with counts and statistics