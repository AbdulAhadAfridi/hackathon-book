# Quickstart: Retrieval Pipeline Validation and Testing

## Overview
This guide provides a quick introduction to using the retrieval pipeline validation and testing system. The system allows you to perform semantic searches against your Qdrant vector store using Cohere embeddings.

## Prerequisites

1. **Environment Setup**
   - Python 3.8+
   - Cohere API key
   - Qdrant Cloud URL and API key
   - Existing vector collection in Qdrant with content from ingestion pipeline

2. **Configuration**
   Ensure your `.env` file contains:
   ```env
   QDRANT_URL="your_qdrant_url"
   QDRANT_API_KEY="your_qdrant_api_key"
   COHERE_API_KEY="your_cohere_api_key"
   QDRANT_COLLECTION_NAME="book_embeddings"
   ```

## Installation

1. **Install Dependencies**
   ```bash
   pip install cohere qdrant-client python-dotenv
   ```

2. **Verify Setup**
   Make sure the following files are available in your backend directory:
   - `retrieve.py` (main implementation)
   - `config.py` (configuration loading)
   - `embedding_client.py` (Cohere integration)
   - `vector_store.py` (Qdrant integration)

## Basic Usage

### 1. Simple Retrieval
Perform a basic semantic search:

```python
from retrieve import retrieve_similar_chunks

# Perform a simple search
response = retrieve_similar_chunks(
    query="How to configure the API settings?",
    top_k=5
)

print(f"Query: {response.query}")
print(f"Execution time: {response.execution_time}s")

for result in response.results:
    print(f"Score: {result.score}")
    print(f"URL: {result.payload['url']}")
    print(f"Content: {result.text[:100]}...")
    print("---")
```

### 2. Filtered Retrieval
Search with metadata filters:

```python
from retrieve import retrieve_similar_chunks

# Search with filters
response = retrieve_similar_chunks(
    query="authentication methods",
    top_k=3,
    filters={"section": "security"}
)

for result in response.results:
    print(f"Section: {result.payload['section']}")
    print(f"Heading: {result.payload['heading']}")
    print(f"Score: {result.score}")
```

### 3. Pipeline Validation
Validate the retrieval pipeline:

```python
from retrieve import validate_pipeline

# Validate with expected URLs
result = validate_pipeline(
    query="authentication process",
    expected_urls=["https://example.com/docs/auth", "https://example.com/docs/security"]
)

print(f"Validation passed: {result['validation_passed']}")
print(f"Precision: {result['precision']}")
print(f"Match count: {result['match_count']}/{result['total_retrieved']}")
```

## Running Test Queries

The system includes a main execution flow to run test queries end-to-end:

```bash
python retrieve.py --test
```

Or with specific query:

```bash
python retrieve.py --query "your search query here"
```

## Common Operations

### 1. Check Vector Store Connection
```python
from retrieve import check_vector_store_connection
is_connected = check_vector_store_connection()
print(f"Qdrant connection: {'OK' if is_connected else 'FAILED'}")
```

### 2. Performance Testing
```python
from retrieve import performance_test
results = performance_test(
    queries=["query 1", "query 2", "query 3"],
    iterations=5
)
print(f"Average response time: {results['avg_time']}s")
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify QDRANT_URL and QDRANT_API_KEY in your environment
   - Check network connectivity to Qdrant Cloud

2. **Authentication Errors**
   - Verify COHERE_API_KEY is valid
   - Check QDRANT_API_KEY is correct

3. **Empty Results**
   - Confirm the Qdrant collection has data from the ingestion pipeline
   - Verify the collection name matches expectations

4. **Performance Issues**
   - Large collections may impact query time
   - Consider adding more specific filters to narrow results

## Next Steps

1. **Integration Testing**: Test the retrieval pipeline with various query types
2. **Performance Optimization**: Fine-tune query parameters based on your data
3. **Monitoring**: Implement logging and monitoring for production use
4. **Error Handling**: Add custom error handling for your specific use case