# RAG Ingestion Pipeline

A Python-based pipeline for ingesting Docusaurus-based book content, generating embeddings using Cohere, and storing them in Qdrant vector database for semantic retrieval.

## Features

- Crawls Docusaurus-based websites to extract content
- Processes and chunks content while preserving document structure
- Generates embeddings using Cohere's embedding models
- Stores embeddings with metadata in Qdrant vector database
- Implements idempotent processing to prevent duplicates
- Comprehensive error handling and logging

## Prerequisites

- Python 3.9+
- `uv` package manager (optional, for fast dependency management)
- Cohere API key
- Qdrant Cloud account and API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or using uv:
```bash
uv pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the backend directory with your API keys:

```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cluster_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
```

## Usage

Run the ingestion pipeline:

```bash
python main.py --website-url "https://your-docusaurus-site.com"
```

### Command Line Options

- `--website-url`: URL of the Docusaurus website to crawl (required)
- `--chunk-size`: Size of content chunks in characters (default: 1000)
- `--chunk-overlap`: Overlap between chunks in characters (default: 100)
- `--max-pages`: Maximum number of pages to crawl (default: 1000)

### Example

```bash
python main.py \
  --website-url "https://example-docusaurus.com" \
  --chunk-size 800 \
  --chunk-overlap 100 \
  --max-pages 500
```

## Architecture

The pipeline consists of several components:

- **Crawler**: Discovers and extracts content from Docusaurus sites
- **Extractor**: Processes HTML to extract clean text content
- **Chunker**: Splits content into appropriately sized chunks
- **Embedding Client**: Generates embeddings using Cohere API
- **Vector Store**: Stores embeddings in Qdrant with metadata

## How It Works

1. **Crawling**: Discovers all accessible pages on the target Docusaurus website
2. **Extraction**: Extracts clean text content while preserving document structure
3. **Chunking**: Splits content into appropriately sized chunks with overlap
4. **Embedding**: Generates vector embeddings using Cohere's models
5. **Storage**: Stores embeddings in Qdrant vector database with metadata

## Success Criteria

- 95% URL discovery success rate
- 98% content extraction accuracy
- 99% embedding generation success rate
- 99% storage success rate
- Process 100 pages within 10 minutes
- Idempotent operation (no duplicates on re-run)

## Troubleshooting

### Common Issues

- **API Key Errors**: Verify that your Cohere and Qdrant API keys are correct
- **Connection Errors**: Check that your Qdrant URL is accessible
- **Rate Limiting**: The pipeline includes built-in rate limiting for API calls
- **Memory Issues**: For large sites, consider processing in smaller batches

### Logging

The application logs to stdout with different levels:
- INFO: Progress updates
- WARN: Non-critical issues
- ERROR: Critical failures

## Security

- API keys are loaded from environment variables
- Input validation is performed on URLs
- Rate limiting is implemented to respect target servers

## Development

The project follows a modular architecture with separate modules for each component:

- `crawler.py`: Web crawling functionality
- `extractor.py`: Content extraction
- `chunker.py`: Content chunking
- `embedding_client.py`: Cohere integration
- `vector_store.py`: Qdrant integration
- `models.py`: Data models
- `config.py`: Configuration management