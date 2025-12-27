"""
Cohere embedding client for the RAG ingestion pipeline
"""

import cohere
import time
import hashlib
import logging
from typing import List, Dict, Any
from config import Config
from constants import COHERE_MODEL, COHERE_INPUT_TYPE


class CohereEmbeddingClient:
    """
    Client for generating embeddings using Cohere API with rate limiting, retry logic, and caching
    """

    def __init__(self, api_key: str = None, max_retries: int = 3, retry_delay: float = 1.0):
        if api_key is None:
            api_key = Config.COHERE_API_KEY

        if not api_key:
            raise ValueError("Cohere API key is required")

        self.client = cohere.Client(api_key)
        self.model = COHERE_MODEL
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)
        self._cache: Dict[str, List[float]] = {}

    def _get_cache_key(self, text: str) -> str:
        """
        Generate a cache key for the given text
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts with retry logic and caching
        """
        results = []
        texts_to_process = []
        text_indices = []  # Track which original indices need to be filled

        # Check cache for each text
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            if cache_key in self._cache:
                results.append(self._cache[cache_key])
            else:
                results.append(None)  # Placeholder
                texts_to_process.append(text)
                text_indices.append(i)

        # Process texts not in cache
        if texts_to_process:
            for attempt in range(self.max_retries + 1):
                try:
                    response = self.client.embed(
                        texts=texts_to_process,
                        model=self.model,
                        input_type=COHERE_INPUT_TYPE
                    )

                    # Update cache and results
                    for j, (orig_idx, embedding) in enumerate(zip(text_indices, response.embeddings)):
                        # Verify that the embedding has the correct dimension for Qdrant
                        if len(embedding) != 1024:  # Cohere embed-english-v3.0 returns 1024-dim vectors
                            raise ValueError(f"Unexpected embedding dimension: {len(embedding)}, expected 1024 for Cohere model {self.model}")

                        results[orig_idx] = embedding
                        # Cache the result
                        cache_key = self._get_cache_key(texts_to_process[j])
                        self._cache[cache_key] = embedding

                    break
                except cohere.CohereAPIError as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed to generate embeddings: {str(e)}")
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                        continue
                    else:
                        self.logger.error(f"Failed to generate embeddings after {self.max_retries} retries")
                        raise
                except Exception as e:
                    self.logger.error(f"Unexpected error generating embeddings: {str(e)}")
                    raise

        return results

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else []

    def clear_cache(self):
        """
        Clear the embedding cache
        """
        self._cache.clear()

    def cache_size(self) -> int:
        """
        Get the current size of the cache
        """
        return len(self._cache)


def create_embedding_client(api_key: str = None) -> CohereEmbeddingClient:
    """
    Create and return a Cohere embedding client
    """
    return CohereEmbeddingClient(api_key)


def generate_embeddings(texts: List[str], api_key: str = None) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using Cohere API
    """
    client = create_embedding_client(api_key)
    return client.generate_embeddings(texts)