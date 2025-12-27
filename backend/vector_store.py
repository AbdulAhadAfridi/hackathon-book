"""
Qdrant vector store for the RAG ingestion pipeline
"""

import uuid
import logging
import time
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
from models import EmbeddingRecord
from config import Config
from constants import QDRANT_COLLECTION_NAME, QDRANT_VECTOR_SIZE, QDRANT_DISTANCE


class QdrantVectorStore:
    """
    Vector store implementation using Qdrant Cloud
    """

    def __init__(self, url: str = None, api_key: str = None):
        if url is None:
            url = Config.QDRANT_URL
        if api_key is None:
            api_key = Config.QDRANT_API_KEY

        if not url or not api_key:
            raise ValueError("Qdrant URL and API key are required")

        # Initialize Qdrant client for Cloud with proper configuration for JWT API key
        # For Qdrant Cloud, extract the host and use proper HTTPS configuration
        parsed_url = urlparse(url)
        host = parsed_url.netloc  # This includes host and port if present

        # For Qdrant Cloud, we need to handle the connection properly
        # The URL from .env doesn't include the port, so Qdrant client will use defaults
        self.client = QdrantClient(
            url=url,
            api_key=api_key,
        )
        self.collection_name = QDRANT_COLLECTION_NAME
        self.logger = logging.getLogger(__name__)

        # Create collection if it doesn't exist with correct vector size
        self._ensure_collection_exists(vector_size=QDRANT_VECTOR_SIZE)

    def _ensure_collection_exists(self, vector_size=None):
        """
        Ensure the collection exists with proper configuration
        """
        # If vector_size is not provided, use the default
        size = vector_size or QDRANT_VECTOR_SIZE

        try:
            # Try to get collection info to see if it exists
            collection_info = self.client.get_collection(self.collection_name)

            # Check if the vector size matches what we expect
            existing_size = collection_info.config.params.vectors.size
            if existing_size != size:
                raise ValueError(f"Collection vector size mismatch: expected {size}, got {existing_size}. Cannot proceed with mismatched dimensions.")

        except ValueError:
            raise  # Re-raise dimension mismatch error
        except Exception as e:
            # Collection doesn't exist, create it
            self.logger.info(f"Creating new collection '{self.collection_name}' with vector size {size}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=size,
                    distance=QDRANT_DISTANCE
                )
            )

            # Create payload index for metadata fields
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="url",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="section",
                field_schema=models.PayloadSchemaType.KEYWORD
            )

    def _validate_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate metadata before storage
        """
        required_fields = ["url", "section", "heading", "chunk_index"]
        for field in required_fields:
            if field not in metadata:
                return False
        return True

    def store_embeddings(self, records: List[EmbeddingRecord]) -> Dict[str, Any]:
        """
        Store embeddings with metadata in Qdrant
        """
        points = []
        errors = []

        for record in records:
            # Check vector dimension
            if len(record.vector) != QDRANT_VECTOR_SIZE:
                errors.append(f"Vector dimension mismatch for record {record.id}: expected {QDRANT_VECTOR_SIZE}, got {len(record.vector)}")
                continue

            # Validate metadata before creating point
            if not self._validate_metadata(record.metadata):
                errors.append(f"Invalid metadata for record {record.id}: missing required fields")
                continue

            sanitized_metadata = record.metadata.copy()
            # Sanitize payload: convert None to empty strings and ensure types
            for key, value in sanitized_metadata.items():
                if value is None:
                    sanitized_metadata[key] = ""
                elif not isinstance(value, (str, int, float)):
                    sanitized_metadata[key] = str(value)

            # Create a PointStruct for each embedding record
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=record.vector,
                payload={
                    "url": sanitized_metadata.get("url", ""),
                    "section": sanitized_metadata.get("section", ""),
                    "heading": sanitized_metadata.get("heading", ""),
                    "chunk_index": sanitized_metadata.get("chunk_index", 0),
                    "content_chunk_id": record.content_chunk_id
                }
            )
            points.append(point)

        # Upload points to Qdrant in small batches with retries and logging
        success_count = 0
        if points:
            batch_size = 6  # Small batches for reliability
            max_retries = 3
            retry_delay = 1.0

            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                batch_num = i // batch_size + 1

                # Log batch details before upload
                self.logger.info(f"Uploading batch {batch_num}: {len(batch)} points")
                for j, point in enumerate(batch):
                    self.logger.debug(f"Point {j+1}: ID={point.id}, Vector length={len(point.vector)}, Payload={point.payload}")

                for attempt in range(max_retries + 1):
                    try:
                        self.client.upload_points(
                            collection_name=self.collection_name,
                            points=batch,
                            wait=True
                        )
                        success_count += len(batch)
                        self.logger.info(f"Batch {batch_num} uploaded successfully")
                        break
                    except Exception as e:
                        self.logger.warning(f"Attempt {attempt + 1} failed for batch {batch_num}: {str(e)}")
                        if attempt < max_retries:
                            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                        else:
                            errors.append(f"Failed to store batch {batch_num} after {max_retries} retries: {str(e)}")
                            # Continue with the next batch instead of failing completely

        return {
            "success_count": success_count,
            "failed_count": len(errors),
            "total_count": len(records),
            "errors": errors
        }

    def store_embedding_record(self, record: EmbeddingRecord) -> bool:
        """
        Store a single embedding record
        """
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=record.vector,
                        payload={
                            "url": record.metadata.get("url", ""),
                            "section": record.metadata.get("section", ""),
                            "heading": record.metadata.get("heading", ""),
                            "chunk_index": record.metadata.get("chunk_index", 0),
                            "content_chunk_id": record.content_chunk_id
                        }
                    )
                ]
            )
            return True
        except Exception as e:
            print(f"Error storing embedding record: {str(e)}")
            return False

    def search(self, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings
        """
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "score": result.score,
                "payload": result.payload,
                "vector": result.vector if hasattr(result, 'vector') else None
            })

        return formatted_results

    def check_idempotency(self, content_chunk_id: str) -> bool:
        """
        Check if an embedding with the given content_chunk_id already exists
        """
        try:
            hits = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="content_chunk_id",
                            match=models.MatchValue(value=content_chunk_id)
                        )
                    ]
                ),
                limit=1
            )
            return len(hits[0]) > 0  # If any hits found, it already exists
        except Exception:
            return False

    def get_embedding_record(self, content_chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an embedding record by content_chunk_id
        """
        try:
            hits = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="content_chunk_id",
                            match=models.MatchValue(value=content_chunk_id)
                        )
                    ]
                ),
                limit=1
            )
            if hits[0]:
                hit = hits[0][0]
                return {
                    "id": hit.id,
                    "payload": hit.payload,
                    "vector": hit.vector if hasattr(hit, 'vector') else None
                }
            return None
        except Exception:
            return None


def create_vector_store(url: str = None, api_key: str = None) -> QdrantVectorStore:
    """
    Create and return a Qdrant vector store instance
    """
    return QdrantVectorStore(url, api_key)


def store_embeddings_in_qdrant(records: List[EmbeddingRecord], url: str = None, api_key: str = None) -> Dict[str, Any]:
    """
    Store embedding records in Qdrant vector store
    """
    store = create_vector_store(url, api_key)
    return store.store_embeddings(records)