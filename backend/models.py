"""
Data models for the RAG ingestion pipeline
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlparse


@dataclass
class ContentDocument:
    """
    Represents extracted content from a web page
    """
    url: str
    content: str
    title: str = ""
    headings: List[str] = field(default_factory=list)
    section: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate the ContentDocument after initialization"""
        if not self.url or not self.content:
            raise ValueError("URL and content are required for ContentDocument")
        if not self.title:
            # Extract title from URL if not provided
            self.title = urlparse(self.url).path.split('/')[-1] or "Untitled"


@dataclass
class ContentChunk:
    """
    Represents a chunk of content that will be embedded
    """
    content_document_id: str
    text: str
    chunk_index: int
    metadata: Dict[str, any] = field(default_factory=dict)
    id: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate the ContentChunk after initialization"""
        if not self.content_document_id or not self.text:
            raise ValueError("content_document_id and text are required for ContentChunk")
        if self.chunk_index < 0:
            raise ValueError("chunk_index must be non-negative")

        # Generate ID if not provided
        if not self.id:
            self.id = f"chunk_{self.content_document_id}_{self.chunk_index}"


@dataclass
class EmbeddingRecord:
    """
    Represents a vector embedding with associated metadata
    """
    content_chunk_id: str
    vector: List[float]
    metadata: Dict[str, any] = field(default_factory=dict)
    id: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate the EmbeddingRecord after initialization"""
        if not self.content_chunk_id or not self.vector:
            raise ValueError("content_chunk_id and vector are required for EmbeddingRecord")

        # Generate ID if not provided
        if not self.id:
            self.id = f"emb_{self.content_chunk_id}"


@dataclass
class CrawlSession:
    """
    Represents a single execution of the crawling process
    """
    website_url: str
    id: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    processed_urls: List[str] = field(default_factory=list)
    failed_urls: List[str] = field(default_factory=list)
    total_chunks: int = 0
    total_embeddings: int = 0
    status: str = "running"  # running, completed, failed
    error_details: Optional[str] = None

    def __post_init__(self):
        """Validate the CrawlSession after initialization"""
        if not self.website_url:
            raise ValueError("website_url is required for CrawlSession")

        # Generate ID if not provided
        if not self.id:
            self.id = f"sess_{int(self.start_time.timestamp())}"

    def complete(self, status: str = "completed", error_details: Optional[str] = None):
        """Mark the session as completed"""
        self.end_time = datetime.now()
        self.status = status
        self.error_details = error_details