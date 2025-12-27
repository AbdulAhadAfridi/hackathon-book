# Quickstart: RAG Ingestion Pipeline

## Prerequisites

- Python 3.9+
- `uv` package manager
- Cohere API key
- Qdrant Cloud account and API key
- Target Docusaurus website URL

## Setup

### 1. Clone and Navigate to Project
```bash
git clone <repository-url>
cd backend
```

### 2. Install Dependencies with uv
```bash
uv venv  # Create virtual environment
source .venv/bin/activate  # Activate virtual environment (Linux/Mac)
# OR
.venv\Scripts\activate  # Activate virtual environment (Windows)

uv pip install requests beautifulsoup4 cohere qdrant-client python-dotenv
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:

```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cluster_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
```

> **Note**: Never commit the `.env` file to version control. It's already gitignored.

## Usage

### Basic Usage
```bash
python main.py --website-url "https://your-docusaurus-site.com"
```

### With Custom Parameters
```bash
python main.py \
  --website-url "https://your-docusaurus-site.com" \
  --chunk-size 1500 \
  --chunk-overlap 200
```

### Command Line Options
- `--website-url` (required): URL of the Docusaurus website to crawl
- `--chunk-size`: Size of content chunks in characters (default: 1000)
- `--chunk-overlap`: Overlap between chunks in characters (default: 100)
- `--max-pages`: Maximum number of pages to crawl (default: 1000)
- `--help`: Show help message

## Configuration

### Environment Variables
The application uses the following environment variables:

- `COHERE_API_KEY`: Your Cohere API key for embedding generation
- `QDRANT_URL`: URL of your Qdrant Cloud cluster
- `QDRANT_API_KEY`: API key for Qdrant Cloud access

### Default Collection Name
By default, the pipeline will use a collection named `book_embeddings` in Qdrant. This can be modified in the code if needed.

## Example

```bash
# Set up environment
export COHERE_API_KEY=your_cohere_key
export QDRANT_URL=https://your-cluster.region.qdrant.tech:6333
export QDRANT_API_KEY=your_qdrant_key

# Run the pipeline
python main.py --website-url "https://example-docusaurus.com" --chunk-size 800
```

## Expected Output

The pipeline will produce output similar to:

```
Starting crawl of https://example-docusaurus.com
Found 25 URLs to process...
Processing page 1/25: https://example-docusaurus.com/intro
Processing page 2/25: https://example-docusaurus.com/installation
...
Generated 150 content chunks
Creating embeddings for 150 chunks...
Successfully stored 150 embeddings in Qdrant
Crawl completed in 4.2 minutes
Session ID: sess_abc123def456
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Verify that your Cohere and Qdrant API keys are correct
2. **Connection Errors**: Check that your Qdrant URL is accessible
3. **Rate Limiting**: If you encounter rate limiting, consider adding delays between API calls
4. **Memory Issues**: For large sites, consider processing in smaller batches

### Logging
The application logs to stdout with different levels:
- INFO: Progress updates
- WARN: Non-critical issues
- ERROR: Critical failures