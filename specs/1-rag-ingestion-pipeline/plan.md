# Implementation Plan: RAG Ingestion Pipeline

**Feature**: 1-rag-ingestion-pipeline
**Created**: 2025-12-24
**Status**: Draft
**Branch**: 1-rag-ingestion-pipeline

## Technical Context

- **Runtime Environment**: Python 3.9+
- **Project Structure**: Single `main.py` file with supporting modules
- **Package Manager**: uv (for fast Python package management)
- **Target System**: RAG backend ingestion pipeline for Docusaurus-based book
- **Primary Users**: RAG chatbot retrieval layer and downstream AI agents
- **Integration Points**:
  - Cohere API for embeddings
  - Qdrant Cloud for vector storage
  - Docusaurus website (public URLs) for content
- **Technology Stack**:
  - Web crawling: requests/BeautifulSoup or scrapy
  - Text extraction: BeautifulSoup/html2text
  - Content chunking: custom logic with document structure awareness
  - Embeddings: Cohere Python SDK
  - Vector database: Qdrant Python client

### Dependencies

- **Cohere API Key**: Required for embedding generation [NEEDS CLARIFICATION: How will this be configured?]
- **Qdrant Cloud Credentials**: Required for vector storage [NEEDS CLARIFICATION: How will these be configured?]
- **Target Website URL**: URL of the Docusaurus book to crawl [NEEDS CLARIFICATION: How will this be specified?]
- **Python packages**: requests, beautifulsoup4, cohere, qdrant-client, python-dotenv

### Unknowns

- **Configuration approach**: How will API keys and URLs be configured? [NEEDS CLARIFICATION]
- **Chunking strategy**: What are the optimal chunk sizes and overlap? [NEEDS CLARIFICATION]
- **Error handling**: How should the system handle different failure modes? [NEEDS CLARIFICATION]
- **Progress tracking**: How will the system report progress during long runs? [NEEDS CLARIFICATION]

## Constitution Check

### Library-First Principle
- This feature will be implemented as a standalone Python script that can function independently
- The ingestion logic will be organized into clear functions that could be extracted into a library later
- The script will have clear inputs and outputs

### CLI Interface
- The main.py file will accept command-line arguments for configuration
- Will support text-based output for progress and status
- Will follow stdin/args → stdout pattern with proper error handling

### Test-First (NON-NEGOTIABLE)
- Individual functions will be unit testable
- Integration tests will verify API interactions
- Test data will be included for validation

### Integration Testing
- Focus on testing the full pipeline: URL → Content → Chunks → Embeddings → Storage
- Contract tests for API interactions with Cohere and Qdrant
- Validation of stored vector data integrity

### Observability & Versioning
- Structured logging for debugging and monitoring
- Clear error messages and status reporting
- MAJOR.MINOR.BUILD versioning approach

## Gates

### Pre-Implementation Gates

- [ ] All [NEEDS CLARIFICATION] items resolved
- [ ] API access confirmed (Cohere, Qdrant Cloud)
- [ ] Target website accessibility confirmed
- [ ] Security review for credential handling
- [ ] Performance requirements validated

### Quality Gates

- [ ] All unit tests pass (min 80% coverage)
- [ ] Integration tests pass with mock APIs
- [ ] End-to-end test with real APIs passes
- [ ] Performance meets requirements (100 pages in 10 minutes)
- [ ] Security scan passes

## Phase 0: Outline & Research

### Research Tasks

1. **Cohere Embedding Models**: Research optimal models for text content
2. **Qdrant Cloud Integration**: Understand vector storage requirements
3. **Docusaurus Content Extraction**: Best practices for extracting clean text
4. **Content Chunking Strategies**: Optimal approaches for document chunking
5. **Web Crawling Techniques**: Best practices for crawling Docusaurus sites

### Expected Outcomes

- Decision on Cohere embedding model to use
- Understanding of Qdrant Cloud setup and usage
- Content extraction methodology
- Chunking algorithm and parameters
- Web crawling approach and error handling

## Phase 1: Design & Contracts

### Data Model

#### Content Document
- `url`: Source URL of the page
- `content`: Extracted text content
- `title`: Page title
- `headings`: List of headings in the document
- `section`: Current section/heading context
- `chunk_index`: Index of this chunk within the document

#### Embedding Record
- `vector`: Embedding vector from Cohere
- `content_id`: Unique identifier for the content chunk
- `metadata`: Dictionary containing URL, section, heading, chunk index
- `created_at`: Timestamp of creation

#### Crawl Session
- `session_id`: Unique identifier for the crawl session
- `start_time`: When the crawl started
- `end_time`: When the crawl ended
- `processed_urls`: List of successfully processed URLs
- `failed_urls`: List of URLs that failed processing
- `total_chunks`: Total number of chunks processed
- `status`: Current status of the session

### API Contracts

#### Main Function Interface
```
def main(
    website_url: str,
    cohere_api_key: str,
    qdrant_url: str,
    qdrant_api_key: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 100
) -> CrawlSession
```

#### Core Processing Pipeline
1. `crawl_website(url: str) -> List[Page]`
2. `extract_content(html: str, url: str) -> ContentDocument`
3. `chunk_content(document: ContentDocument, size: int, overlap: int) -> List[ContentChunk]`
4. `generate_embeddings(chunks: List[ContentChunk], api_key: str) -> List[EmbeddingRecord]`
5. `store_embeddings(records: List[EmbeddingRecord], qdrant_config: dict) -> StorageResult`

## Phase 2: Implementation Plan

### File Structure
```
backend/
├── pyproject.toml          # Project configuration for uv
├── main.py                 # Main ingestion pipeline
├── .env                    # Environment variables (gitignored)
├── .env.example            # Example environment file
├── requirements.txt        # Dependencies
└── tests/
    ├── test_crawler.py     # Crawler unit tests
    ├── test_extractor.py   # Content extractor tests
    ├── test_chunker.py     # Chunking logic tests
    └── test_embeddings.py  # Embedding integration tests
```

### Implementation Steps

1. **Project Setup**
   - Create backend directory
   - Initialize Python project with uv
   - Set up basic project structure

2. **Web Crawling Module**
   - Implement URL discovery for Docusaurus sites
   - Add HTTP error handling and retry logic
   - Create page data structure

3. **Content Extraction Module**
   - Extract clean text from HTML
   - Preserve document structure (headings, sections)
   - Handle different content types

4. **Content Chunking Module**
   - Implement intelligent chunking with context preservation
   - Handle overlapping chunks appropriately
   - Maintain metadata through the process

5. **Embedding Generation Module**
   - Integrate with Cohere API
   - Handle rate limiting and errors
   - Cache embeddings for efficiency

6. **Vector Storage Module**
   - Connect to Qdrant Cloud
   - Store embeddings with metadata
   - Implement idempotent storage

7. **Main Pipeline Orchestration**
   - Implement main() function
   - Add progress reporting
   - Handle configuration and error cases

8. **Testing and Validation**
   - Write unit tests for each module
   - Create integration tests
   - Validate end-to-end functionality

## Phase 3: Deployment & Operations

### Configuration Management
- Environment variables for API keys
- Configuration file for URLs and parameters
- Default values for optional settings

### Monitoring & Observability
- Progress logging during execution
- Error reporting and diagnostics
- Performance metrics collection

### Security Considerations
- Secure handling of API keys
- Input validation for URLs
- Rate limiting to respect target servers

## Success Criteria Validation

Each success criterion from the spec will be validated:

- **URL Discovery**: Test with sample Docusaurus site
- **Content Extraction**: Verify clean text extraction
- **Embedding Generation**: Confirm Cohere integration works
- **Storage**: Verify Qdrant storage with metadata
- **Idempotency**: Test re-run without duplicates
- **Performance**: Validate 100 pages in 10 minutes