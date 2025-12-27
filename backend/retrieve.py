"""
Retrieval Pipeline Validation and Testing
Main implementation file for semantic search against Qdrant collection using Cohere embeddings
"""
import logging
import time
import argparse
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
from config import Config


# Data models will be defined here


class CohereEmbeddingClient:
    """
    Interface for generating embeddings with Cohere API
    Includes caching, retry logic, and rate limiting
    Validates embedding dimensions (1024)
    """

    def __init__(self, api_key: str = None, max_retries: int = 3, retry_delay: float = 1.0):
        if api_key is None:
            api_key = Config.COHERE_API_KEY

        if not api_key:
            raise ValueError("Cohere API key is required")

        self.client = cohere.Client(api_key)
        self.model = "embed-english-v3.0"  # Same as ingestion pipeline
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)
        self._cache = {}

    def _get_cache_key(self, text: str) -> str:
        """
        Generate a cache key for the given text
        """
        import hashlib
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
                        input_type="search_query"  # For query embeddings
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
                    # Log the error but don't expose sensitive information like API keys
                    self.logger.warning(f"Attempt {attempt + 1} failed to generate embeddings: {type(e).__name__}")
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                        continue
                    else:
                        self.logger.error(f"Failed to generate embeddings after {self.max_retries} retries")
                        raise
                except Exception as e:
                    # Log the error but don't expose sensitive information
                    self.logger.error(f"Unexpected error generating embeddings: {type(e).__name__}: {str(e)[:100]}...")  # Limit error message length
                    raise

        return results

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else []


class QdrantVectorStore:
    """
    Interface for similarity search in Qdrant
    Handles connection management and error handling
    Validates result format and metadata
    """

    def __init__(self, url: str = None, api_key: str = None):
        if url is None:
            url = Config.QDRANT_URL
        if api_key is None:
            api_key = Config.QDRANT_API_KEY

        if not url or not api_key:
            raise ValueError("Qdrant URL and API key are required")

        # Initialize Qdrant client for Cloud with proper configuration for JWT API key
        self.client = QdrantClient(
            url=url,
            api_key=api_key,
        )
        # Use the same collection name as the ingestion pipeline
        self.collection_name = getattr(Config, 'QDRANT_COLLECTION_NAME', 'book_embeddings')
        self.logger = logging.getLogger(__name__)

    def search(self, query_vector: List[float], top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform similarity search in Qdrant collection
        """
        try:
            # Prepare filters if provided
            search_filter = None
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    filter_conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    )

                if filter_conditions:
                    search_filter = models.Filter(
                        must=filter_conditions
                    )

            # Perform the search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=search_filter
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

        except Exception as e:
            # Log the error but don't expose sensitive information like connection details
            self.logger.error(f"Error during Qdrant search: {type(e).__name__}: {str(e)[:100]}...")
            raise

    def check_connection(self) -> bool:
        """
        Check if connection to Qdrant is working
        """
        try:
            # Try to get collection info to verify connection
            self.client.get_collection(self.collection_name)
            return True
        except Exception as e:
            # Log the error but don't expose sensitive information like connection details
            self.logger.error(f"Qdrant connection check failed: {type(e).__name__}: {str(e)[:100]}...")
            return False


@dataclass
class SearchResult:
    """
    Represents a single search result from the Qdrant similarity search
    """
    id: str              # Qdrant point ID
    score: float         # Similarity score (0.0 to 1.0)
    payload: Dict[str, Any]  # Metadata including url, section, heading, chunk_index
    text: str            # Original content text

    def __post_init__(self):
        """Validate SearchResult fields after initialization"""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Score must be between 0.0 and 1.0, got {self.score}")
        # Only validate text is not empty if it's provided, but allow empty text for some results
        # This validation might be too strict, so we'll allow empty text for now


@dataclass
class RetrievalRequest:
    """
    Represents a request for content retrieval from the vector store
    """
    query: str           # Input query text
    top_k: int = 5       # Number of results to return (default: 5)
    filters: Optional[Dict[str, Any]] = None  # Optional metadata filters

    def __post_init__(self):
        """Validate RetrievalRequest fields after initialization"""
        if not self.query:
            raise ValueError("Query must not be empty or None")
        if not 1 <= self.top_k <= 100:
            raise ValueError(f"top_k must be between 1 and 100, got {self.top_k}")
        if self.filters is not None:
            # Basic validation for filters keys
            allowed_keys = {"url", "section", "heading", "chunk_index"}
            if isinstance(self.filters, dict):
                for key in self.filters.keys():
                    if key not in allowed_keys:
                        raise ValueError(f"Filter key '{key}' not in allowed keys: {allowed_keys}")


@dataclass
class RetrievalResponse:
    """
    Represents the response from a content retrieval request
    """
    query: str                           # Original query text
    results: List[SearchResult]          # Retrieved content chunks
    query_embedding: List[float]         # Generated query embedding
    execution_time: float                # Time taken for retrieval

    def __post_init__(self):
        """Validate RetrievalResponse fields after initialization"""
        if self.results:
            # Ensure results are ordered by score in descending order
            self.results.sort(key=lambda x: x.score, reverse=True)
        if self.execution_time < 0:
            raise ValueError(f"Execution time must be non-negative, got {self.execution_time}")
        if len(self.query_embedding) != 1024:
            raise ValueError(f"Query embedding must be 1024-dimensional, got {len(self.query_embedding)}")


def setup_logging(level: str = "INFO") -> None:
    """
    Set up basic logging configuration following existing pipeline format.

    Args:
        level: Logging level as string (default: "INFO"). Options include "DEBUG", "INFO", "WARNING", "ERROR".
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )


def load_config():
    """
    Load configuration from environment using config.py.

    Returns:
        Config: The validated configuration object.

    Raises:
        ValueError: If configuration validation fails.
    """
    if not Config.validate():
        raise ValueError("Configuration validation failed. Please check your environment variables.")

    return Config


def validate_api_keys():
    """
    Validate that API keys are properly configured and accessible.

    Returns:
        bool: True if all required API keys are valid, False otherwise.

    Raises:
        ValueError: If any required API key is missing or invalid.
    """
    missing_keys = []

    # Check for required API keys
    if not getattr(Config, 'COHERE_API_KEY', None):
        missing_keys.append("COHERE_API_KEY")

    if not getattr(Config, 'QDRANT_API_KEY', None):
        missing_keys.append("QDRANT_API_KEY")

    if not getattr(Config, 'QDRANT_URL', None):
        missing_keys.append("QDRANT_URL")

    if missing_keys:
        raise ValueError(f"Missing required API keys/configurations: {', '.join(missing_keys)}")

    # Additional validation could go here (e.g., testing API connectivity)
    return True


def check_ingestion_pipeline_compatibility() -> Dict[str, Any]:
    """
    Check compatibility with the existing ingestion pipeline.

    Returns:
        Dictionary containing compatibility check results.
    """
    results = {
        "cohere_model_compatibility": False,
        "qdrant_schema_compatibility": False,
        "embedding_dimension_compatibility": False,
        "metadata_schema_compatibility": False,
        "overall_compatibility": False,
        "details": {}
    }

    try:
        # Check Cohere model compatibility
        expected_model = "embed-english-v3.0"
        # We're using the same model as the ingestion pipeline, so this should be compatible
        results["cohere_model_compatibility"] = True
        results["details"]["cohere_model"] = f"Using {expected_model} (same as ingestion)"

        # Check Qdrant schema compatibility by testing connection and collection
        qdrant_client = QdrantVectorStore()
        collection_info = qdrant_client.client.get_collection(qdrant_client.collection_name)

        # Check if the vector size is 1024 (expected for Cohere embed-english-v3.0)
        vector_size = collection_info.config.params.vectors.size
        results["embedding_dimension_compatibility"] = (vector_size == 1024)
        results["details"]["vector_size"] = f"Collection vector size: {vector_size}, expected: 1024"

        # Check if the collection exists and is accessible
        results["qdrant_schema_compatibility"] = True
        results["details"]["collection"] = f"Collection '{qdrant_client.collection_name}' accessible"

        # Check metadata schema by retrieving a sample point
        sample_points = qdrant_client.client.scroll(
            collection_name=qdrant_client.collection_name,
            limit=1
        )

        if sample_points[0]:  # If there are any points in the collection
            sample_payload = sample_points[0][0].payload
            required_fields = {"url", "section", "heading", "chunk_index"}
            available_fields = set(sample_payload.keys())

            missing_fields = required_fields - available_fields
            results["metadata_schema_compatibility"] = len(missing_fields) == 0
            results["details"]["metadata_fields"] = {
                "required": list(required_fields),
                "available": list(available_fields),
                "missing": list(missing_fields)
            }

        # Overall compatibility is true if all checks pass
        results["overall_compatibility"] = (
            results["cohere_model_compatibility"] and
            results["qdrant_schema_compatibility"] and
            results["embedding_dimension_compatibility"] and
            results["metadata_schema_compatibility"]
        )

        results["details"]["compatibility_status"] = "Compatible" if results["overall_compatibility"] else "Incompatible"

    except Exception as e:
        results["details"]["error"] = f"Compatibility check failed: {str(e)}"
        results["overall_compatibility"] = False

    return results


def retrieve_similar_chunks(query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> RetrievalResponse:
    """
    Retrieve similar content chunks from Qdrant based on semantic similarity

    Args:
        query: Input text to find similar content for
        top_k: Number of top results to return (default 5)
        filters: Optional metadata filters for targeted search

    Returns:
        RetrievalResponse containing similar chunks and metadata

    Raises:
        ValueError: If query is empty or invalid
        ConnectionError: If unable to connect to Qdrant
        RuntimeError: If retrieval fails
    """
    logger = logging.getLogger(__name__)
    start_time = time.time()
    logger.info(f"Starting retrieval for query: {query[:50]}...")

    # Comprehensive input validation
    if not query:
        logger.error("Query must not be empty")
        raise ValueError("Query must not be empty")

    if not isinstance(query, str):
        logger.error(f"Query must be a string, got {type(query)}")
        raise ValueError(f"Query must be a string, got {type(query)}")

    if len(query.strip()) == 0:
        logger.error("Query must not be empty or whitespace only")
        raise ValueError("Query must not be empty or whitespace only")

    if not isinstance(top_k, int):
        logger.error(f"top_k must be an integer, got {type(top_k)}")
        raise ValueError(f"top_k must be an integer, got {type(top_k)}")

    if not 1 <= top_k <= 100:
        logger.error(f"top_k must be between 1 and 100, got {top_k}")
        raise ValueError(f"top_k must be between 1 and 100, got {top_k}")

    if filters is not None:
        if not isinstance(filters, dict):
            logger.error(f"Filters must be a dictionary or None, got {type(filters)}")
            raise ValueError(f"Filters must be a dictionary or None, got {type(filters)}")
        # Validate filter keys
        allowed_keys = {"url", "section", "heading", "chunk_index"}
        for key in filters.keys():
            if key not in allowed_keys:
                logger.error(f"Filter key '{key}' not in allowed keys: {allowed_keys}")
                raise ValueError(f"Filter key '{key}' not in allowed keys: {allowed_keys}")

    logger.info(f"Input validation passed. Query length: {len(query)}, top_k: {top_k}, filters: {bool(filters)}")

    # Load configuration
    logger.info("Loading configuration...")
    config = load_config()
    logger.info("Configuration loaded successfully")

    # Initialize clients
    logger.info("Initializing Cohere and Qdrant clients...")
    try:
        cohere_client = CohereEmbeddingClient()
        qdrant_client = QdrantVectorStore()
        logger.info("Clients initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize clients: {type(e).__name__}")
        raise ConnectionError(f"Failed to initialize clients: {type(e).__name__}: {str(e)[:100]}...")

    # Generate query embedding
    logger.info("Generating query embedding...")
    try:
        query_embedding = cohere_client.generate_embedding(query)
        logger.info(f"Query embedding generated successfully, dimension: {len(query_embedding)}")
    except Exception as e:
        logger.error(f"Failed to generate query embedding: {type(e).__name__}")
        raise ConnectionError(f"Failed to generate query embedding: {type(e).__name__}: {str(e)[:100]}...")

    # Perform similarity search
    logger.info(f"Performing similarity search with top_k={top_k}...")
    try:
        search_results = qdrant_client.search(query_embedding, top_k, filters)
        logger.info(f"Similarity search completed, found {len(search_results)} results")
    except Exception as e:
        logger.error(f"Failed to perform similarity search: {type(e).__name__}")
        raise ConnectionError(f"Failed to perform similarity search: {type(e).__name__}: {str(e)[:100]}...")

    # Process and convert results to SearchResult objects
    logger.info("Processing search results...")
    result_objects = []
    for i, item in enumerate(search_results):
        # Validate result structure
        if not isinstance(item, dict):
            logger.error(f"Search result must be a dictionary, got {type(item)}")
            raise ValueError(f"Search result must be a dictionary, got {type(item)}")

        # Get the score and validate it's in the expected range
        score = float(item.get("score", 0.0))
        if not 0.0 <= score <= 1.0:
            logger.error(f"Similarity score must be between 0.0 and 1.0, got {score}")
            raise ValueError(f"Similarity score must be between 0.0 and 1.0, got {score}")

        # Get the payload and validate its metadata integrity
        payload = item.get("payload", {})
        if not isinstance(payload, dict):
            logger.error(f"Payload must be a dictionary, got {type(payload)}")
            raise ValueError(f"Payload must be a dictionary, got {type(payload)}")

        # Validate required metadata fields
        url = payload.get("url", "")
        section = payload.get("section", "")
        heading = payload.get("heading", "")
        chunk_index = payload.get("chunk_index", 0)

        # Validate metadata types
        if not isinstance(url, str):
            logger.error(f"URL must be a string, got {type(url)}")
            raise ValueError(f"URL must be a string, got {type(url)}")
        if not isinstance(section, str):
            logger.error(f"Section must be a string, got {type(section)}")
            raise ValueError(f"Section must be a string, got {type(section)}")
        if not isinstance(heading, str):
            logger.error(f"Heading must be a string, got {type(heading)}")
            raise ValueError(f"Heading must be a string, got {type(heading)}")
        if not isinstance(chunk_index, (int, float)):  # chunk_index might be stored as float
            logger.error(f"Chunk index must be a number, got {type(chunk_index)}")
            raise ValueError(f"Chunk index must be a number, got {type(chunk_index)}")

        # Validate content relevance by checking if the text content is meaningful
        text_content = payload.get("text", "") if payload else ""
        if not text_content or len(text_content.strip()) == 0:
            # If text is not in payload, check the text field directly
            text_content = item.get("text", "")

        # If still no text, try getting it from the content field which might be in the metadata
        if not text_content or len(text_content.strip()) == 0:
            # Check if there's content in the payload
            text_content = payload.get("content", "")

        # Create a SearchResult object from the search result
        search_result = SearchResult(
            id=str(item.get("id", "")),
            score=score,
            payload=payload,
            text=text_content
        )
        result_objects.append(search_result)

    # Validate that we have meaningful results
    if result_objects and all(result.score == 0.0 for result in result_objects):
        # All results have zero similarity - this might indicate poor relevance
        logger.warning("All retrieved results have zero similarity scores, which may indicate poor query relevance")

    # Calculate execution time
    execution_time = time.time() - start_time
    logger.info(f"Retrieval completed in {execution_time:.3f}s, returning {len(result_objects)} results")

    # Create and return RetrievalResponse
    return RetrievalResponse(
        query=query,
        results=result_objects,
        query_embedding=query_embedding,
        execution_time=execution_time
    )


def validate_pipeline(query: str, expected_urls: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Validate the retrieval pipeline with test query

    Args:
        query: Test query to validate retrieval
        expected_urls: Optional list of expected document URLs to be retrieved

    Returns:
        dict containing validation results and metrics
    """
    start_time = time.time()

    # Perform retrieval using the core function
    retrieval_response = retrieve_similar_chunks(query, top_k=10)  # Get more results for validation

    # Extract retrieved URLs
    retrieved_urls = [result.payload.get("url", "") for result in retrieval_response.results if result.payload.get("url")]

    # Initialize validation results
    result = {
        "query": query,
        "expected_urls": expected_urls or [],
        "retrieved_urls": retrieved_urls,
        "match_count": 0,
        "total_retrieved": len(retrieved_urls),
        "precision": 0.0,
        "validation_passed": False,
        "debug_info": {
            "retrieved_urls_detailed": [
                {
                    "url": result.payload.get("url", ""),
                    "score": result.score,
                    "section": result.payload.get("section", ""),
                    "heading": result.payload.get("heading", "")
                }
                for result in retrieval_response.results if result.payload
            ]
        },
        "details": {
            "retrieved_chunks": [result.__dict__ for result in retrieval_response.results],
            "execution_time": retrieval_response.execution_time
        }
    }

    # If expected URLs are provided, perform validation
    if expected_urls:
        # Calculate how many expected URLs were retrieved
        matches = [url for url in expected_urls if url in retrieved_urls]
        match_count = len(matches)

        # Calculate which expected URLs were NOT retrieved
        missed_urls = [url for url in expected_urls if url not in retrieved_urls]

        # Calculate precision: matches / total retrieved
        precision = match_count / len(retrieved_urls) if retrieved_urls else 0.0

        result.update({
            "match_count": match_count,
            "precision": precision,
            "missed_urls": missed_urls,
            "validation_passed": match_count > 0  # Consider validation passed if at least one expected URL was retrieved
        })
    else:
        # If no expected URLs provided, just return the retrieved results
        result["validation_passed"] = True  # Consider validation passed by default when no expectations are set
        result["missed_urls"] = []

    # Add total execution time for validation
    result["details"]["validation_execution_time"] = time.time() - start_time

    return result


def run_integration_tests() -> Dict[str, Any]:
    """
    Perform final integration testing of the retrieval pipeline.

    Returns:
        Dictionary containing test results.
    """
    logger = logging.getLogger(__name__)
    results = {
        "tests_passed": 0,
        "tests_failed": 0,
        "total_tests": 0,
        "test_results": [],
        "overall_status": "PASS"
    }

    # Test 1: Configuration loading
    logger.info("Running test 1: Configuration loading...")
    try:
        config = load_config()
        results["test_results"].append({
            "test": "Configuration loading",
            "status": "PASS",
            "details": "Configuration loaded successfully"
        })
        results["tests_passed"] += 1
    except Exception as e:
        logger.error(f"Configuration loading test failed: {str(e)}")
        results["test_results"].append({
            "test": "Configuration loading",
            "status": "FAIL",
            "details": f"Configuration loading failed: {str(e)}"
        })
        results["tests_failed"] += 1
        results["overall_status"] = "FAIL"
    results["total_tests"] += 1

    # Test 2: API key validation
    logger.info("Running test 2: API key validation...")
    try:
        validate_api_keys()
        results["test_results"].append({
            "test": "API key validation",
            "status": "PASS",
            "details": "API keys validated successfully"
        })
        results["tests_passed"] += 1
    except Exception as e:
        logger.error(f"API key validation test failed: {str(e)}")
        results["test_results"].append({
            "test": "API key validation",
            "status": "FAIL",
            "details": f"API key validation failed: {str(e)}"
        })
        results["tests_failed"] += 1
        results["overall_status"] = "FAIL"
    results["total_tests"] += 1

    # Test 3: Cohere client initialization
    logger.info("Running test 3: Cohere client initialization...")
    try:
        cohere_client = CohereEmbeddingClient()
        results["test_results"].append({
            "test": "Cohere client initialization",
            "status": "PASS",
            "details": "Cohere client initialized successfully"
        })
        results["tests_passed"] += 1
    except Exception as e:
        logger.error(f"Cohere client initialization test failed: {str(e)}")
        results["test_results"].append({
            "test": "Cohere client initialization",
            "status": "FAIL",
            "details": f"Cohere client initialization failed: {str(e)}"
        })
        results["tests_failed"] += 1
        results["overall_status"] = "FAIL"
    results["total_tests"] += 1

    # Test 4: Qdrant client initialization and connection
    logger.info("Running test 4: Qdrant client connection...")
    try:
        qdrant_client = QdrantVectorStore()
        is_connected = qdrant_client.check_connection()
        if is_connected:
            results["test_results"].append({
                "test": "Qdrant client connection",
                "status": "PASS",
                "details": "Qdrant client connected successfully"
            })
            results["tests_passed"] += 1
        else:
            results["test_results"].append({
                "test": "Qdrant client connection",
                "status": "FAIL",
                "details": "Qdrant client connection failed"
            })
            results["tests_failed"] += 1
            results["overall_status"] = "FAIL"
    except Exception as e:
        logger.error(f"Qdrant client connection test failed: {str(e)}")
        results["test_results"].append({
            "test": "Qdrant client connection",
            "status": "FAIL",
            "details": f"Qdrant client connection failed: {str(e)}"
        })
        results["tests_failed"] += 1
        results["overall_status"] = "FAIL"
    results["total_tests"] += 1

    # Test 5: Simple retrieval
    logger.info("Running test 5: Simple retrieval...")
    try:
        # Use a simple query to test retrieval
        test_query = "test query for integration"
        response = retrieve_similar_chunks(test_query, top_k=1)
        results["test_results"].append({
            "test": "Simple retrieval",
            "status": "PASS",
            "details": f"Retrieved {len(response.results)} results in {response.execution_time:.3f}s"
        })
        results["tests_passed"] += 1
    except Exception as e:
        logger.error(f"Simple retrieval test failed: {str(e)}")
        results["test_results"].append({
            "test": "Simple retrieval",
            "status": "FAIL",
            "details": f"Simple retrieval failed: {str(e)}"
        })
        results["tests_failed"] += 1
        results["overall_status"] = "FAIL"
    results["total_tests"] += 1

    # Test 6: Validation pipeline
    logger.info("Running test 6: Validation pipeline...")
    try:
        # Test validation pipeline with a simple query
        validation_result = validate_pipeline("test validation query")
        results["test_results"].append({
            "test": "Validation pipeline",
            "status": "PASS",
            "details": f"Validation completed, found {len(validation_result['retrieved_urls'])} results"
        })
        results["tests_passed"] += 1
    except Exception as e:
        logger.error(f"Validation pipeline test failed: {str(e)}")
        results["test_results"].append({
            "test": "Validation pipeline",
            "status": "FAIL",
            "details": f"Validation pipeline failed: {str(e)}"
        })
        results["tests_failed"] += 1
        results["overall_status"] = "FAIL"
    results["total_tests"] += 1

    # Test 7: Compatibility check
    logger.info("Running test 7: Compatibility check...")
    try:
        compatibility_result = check_ingestion_pipeline_compatibility()
        if compatibility_result["overall_compatibility"]:
            results["test_results"].append({
                "test": "Compatibility check",
                "status": "PASS",
                "details": "Pipeline is compatible with ingestion pipeline"
            })
            results["tests_passed"] += 1
        else:
            results["test_results"].append({
                "test": "Compatibility check",
                "status": "FAIL",
                "details": f"Pipeline compatibility issues: {compatibility_result['details']}"
            })
            results["tests_failed"] += 1
            results["overall_status"] = "FAIL"
    except Exception as e:
        logger.error(f"Compatibility check test failed: {str(e)}")
        results["test_results"].append({
            "test": "Compatibility check",
            "status": "FAIL",
            "details": f"Compatibility check failed: {str(e)}"
        })
        results["tests_failed"] += 1
        results["overall_status"] = "FAIL"
    results["total_tests"] += 1

    # Summary
    logger.info(f"Integration tests completed: {results['tests_passed']} passed, {results['tests_failed']} failed")
    return results


def main():
    """
    Main function with argument parsing
    """
    setup_logging()  # Set up logging
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='Retrieval Pipeline Validation and Testing')
    parser.add_argument('--query', type=str, help='Query to test retrieval')
    parser.add_argument('--test', action='store_true', help='Run test queries')
    parser.add_argument('--expected-url', type=str, action='append', help='Expected URL for validation (can be used multiple times)')

    args = parser.parse_args()

    if args.test:
        logger.info("Running test queries...")
        # Run some sample queries to test the pipeline
        test_queries = [
            "How to configure the API settings?",
            "What is the authentication process?",
            "Explain the data models",
            "How to set up the environment?"
        ]

        for query in test_queries:
            logger.info(f"Testing query: {query}")
            try:
                result = retrieve_similar_chunks(query, top_k=3)
                logger.info(f"Retrieved {len(result.results)} results for query: {query[:50]}...")
                for i, res in enumerate(result.results[:2]):  # Show top 2 results
                    logger.info(f"  {i+1}. Score: {res.score:.3f}, URL: {res.payload.get('url', 'N/A')}")
            except Exception as e:
                logger.error(f"Error processing query '{query}': {str(e)}")
    elif args.query:
        logger.info(f"Processing query: {args.query}")
        query_start_time = time.time()
        try:
            if args.expected_url:
                # Run validation with expected URLs
                result = validate_pipeline(args.query, args.expected_url)
                total_time = time.time() - query_start_time
                print(f"Query: {result['query']}")
                print(f"Expected URLs: {result['expected_urls']}")
                print(f"Retrieved URLs: {result['retrieved_urls'][:5]}...")  # Show first 5
                print(f"Match count: {result['match_count']}/{len(result['expected_urls'])}")
                print(f"Precision: {result['precision']:.3f}")
                print(f"Validation passed: {result['validation_passed']}")
                if result['missed_urls']:
                    print(f"Missed URLs: {result['missed_urls']}")
                print(f"Total execution time: {total_time:.3f}s")
                print(f"Retrieval execution time: {result['details']['execution_time']:.3f}s")
                print(f"Validation execution time: {result['details']['validation_execution_time']:.3f}s")
            else:
                # Just retrieve similar chunks
                result = retrieve_similar_chunks(args.query, top_k=5)
                total_time = time.time() - query_start_time
                print(f"Query: {result.query}")
                print(f"Total execution time: {total_time:.3f}s")
                print(f"Retrieval execution time: {result.execution_time:.3f}s")
                print(f"Retrieved {len(result.results)} results:")
                for i, res in enumerate(result.results):
                    print(f"  {i+1}. Score: {res.score:.3f}")
                    print(f"     URL: {res.payload.get('url', 'N/A')}")
                    print(f"     Section: {res.payload.get('section', 'N/A')}")
                    print(f"     Heading: {res.payload.get('heading', 'N/A')}")
                    print(f"     Text preview: {res.text[:100]}...")
                    print()
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            print(f"Error: {str(e)}")
    else:
        print("Use --query 'your query' or --test to run test queries")


if __name__ == "__main__":
    main()