"""
Constants for the RAG ingestion pipeline
"""

# Default values
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 100
DEFAULT_MAX_PAGES = 1000
DEFAULT_CRAWLER_DELAY = 1.0
DEFAULT_REQUEST_TIMEOUT = 30

# Cohere settings
COHERE_MODEL = "embed-english-v3.0"
COHERE_INPUT_TYPE = "search_document"  # for embedding documents
COHERE_EMBEDDING_DIMENSION = 1024  # Default dimension for the embed-english-v3.0 model

# Qdrant settings
QDRANT_COLLECTION_NAME = "book_embeddings"
QDRANT_VECTOR_SIZE = COHERE_EMBEDDING_DIMENSION
QDRANT_DISTANCE = "Cosine"

# HTTP settings
USER_AGENT = "RAG-Ingestion-Pipeline/1.0"
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT
}

# Content extraction selectors for Docusaurus
DOCUSAURUS_CONTENT_SELECTORS = [
    "main article",
    "[class*='main']",
    ".markdown",
    ".theme-doc-markdown",
    ".container.padding-top--md",
    ".docItemContainer",
    "article"
]

# Content filtering selectors (to exclude from extraction)
DOCUSAURUS_EXCLUDE_SELECTORS = [
    "nav",
    ".navbar",
    ".footer",
    ".toc",
    ".theme-edit-this-page",
    ".pagination-nav",
    ".theme-admonition"
]

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Status values
CRAWL_SESSION_STATUS = {
    "RUNNING": "running",
    "COMPLETED": "completed",
    "FAILED": "failed"
}

# Error messages
ERROR_MESSAGES = {
    "MISSING_API_KEY": "API key is missing or invalid",
    "INVALID_URL": "URL is invalid or malformed",
    "CONNECTION_ERROR": "Failed to connect to the target URL",
    "CONTENT_EXTRACTION_ERROR": "Failed to extract content from the page",
    "EMBEDDING_ERROR": "Failed to generate embeddings for content",
    "STORAGE_ERROR": "Failed to store embeddings in vector database"
}