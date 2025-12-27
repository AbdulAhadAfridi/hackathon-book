# API Contract: RAG Agent

## Endpoints

### POST /query
Process a user query and return a grounded response based on retrieved context.

#### Request
```json
{
  "query": "What does the book say about RAG systems?",
  "top_k": 5,
  "user_provided_text": "Optional text provided by the user for context"
}
```

#### Response
```json
{
  "query": "What does the book say about RAG systems?",
  "answer": "The book explains that RAG (Retrieval-Augmented Generation) systems combine information retrieval with language model generation to provide more accurate and grounded responses...",
  "retrieved_context": {
    "query": "What does the book say about RAG systems?",
    "results": [
      {
        "id": "doc_123",
        "score": 0.85,
        "payload": {
          "url": "https://book.example.com/rag-systems",
          "section": "Chapter 3",
          "heading": "Introduction to RAG",
          "chunk_index": 0
        },
        "text": "RAG systems combine retrieval and generation to provide grounded responses..."
      }
    ],
    "query_embedding": [0.1, 0.2, ...], // 1024-dimensional vector
    "execution_time": 1.234
  },
  "usage": {
    "prompt_tokens": 1200,
    "completion_tokens": 150,
    "total_tokens": 1350
  },
  "model": "gpt-4-turbo"
}
```

#### Error Responses
- `400 Bad Request`: Invalid query format
- `401 Unauthorized`: Invalid or missing API key
- `500 Internal Server Error`: Processing error

## Functional Requirements Mapping

- **FR-001**: Agent instantiated using OpenAI Agents SDK - Implemented in agent initialization
- **FR-002**: Integration with Spec-2 retrieval pipeline - Implemented via retrieve_similar_chunks function
- **FR-003**: Responses based only on retrieved context - Enforced via system prompt
- **FR-004**: Proper citations in responses - Implemented in response formatting
- **FR-005**: Handle user-provided text - Supported via user_provided_text parameter
- **FR-006**: Grounding enforcement - Implemented via system prompt design
- **FR-007**: Coherent, relevant responses - Validated through response quality
- **FR-008**: Error handling - Implemented with comprehensive error responses
- **FR-009**: Multi-step reasoning - Supported through context synthesis