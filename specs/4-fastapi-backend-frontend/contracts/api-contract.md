# API Contract: FastAPI Integration

## Endpoints

### POST /api/chat
Process a user chat query and return a response from the RAG agent.

#### Request
```json
{
  "query": "What are the main concepts in the book?",
  "selected_text": "Optional text selected by user for additional context"
}
```

#### Response (200 OK)
```json
{
  "response": "The main concepts in the book include...",
  "sources": [
    {
      "url": "https://book.example.com/chapter1",
      "section": "Chapter 1",
      "heading": "Introduction",
      "relevance_score": 0.85
    }
  ],
  "processing_time": 2.345,
  "timestamp": "2025-12-26T10:30:00Z",
  "query_id": "req_abc123"
}
```

#### Error Responses
- `400 Bad Request`: Invalid request format
- `503 Service Unavailable`: RAG agent unavailable
- `500 Internal Server Error`: Processing error

### GET /health
Check the health status of the API.

#### Response (200 OK)
```json
{
  "status": "healthy",
  "timestamp": "2025-12-26T10:30:00Z",
  "service": "FastAPI Chat API",
  "version": "1.0.0"
}
```

### GET /docs
Interactive API documentation (Swagger UI)

### GET /redoc
Alternative API documentation (ReDoc)

## Functional Requirements Mapping

- **FR-001**: API exposes chat endpoints at `/api/chat` - Implemented in chat router
- **FR-002**: Queries routed to RAG agent - Implemented in chat endpoint handler
- **FR-003**: Structured JSON responses - Implemented in response models
- **FR-004**: Handles selected text context - Implemented with optional selected_text field
- **FR-005**: Error responses when RAG agent unavailable - Implemented in error handlers
- **FR-006**: Input validation - Implemented with Pydantic models
- **FR-007**: Asynchronous processing - Implemented with async/await patterns
- **FR-008**: Response metadata included - Implemented with processing_time and sources
- **FR-009**: Concurrent request handling - Implemented with FastAPI async support

## Data Models

### ChatRequest
- **Purpose**: Input model for chat queries
- **Schema**:
  - `query`: string (required) - User's question
  - `selected_text`: string (optional) - Additional context from user selection

### ChatResponse
- **Purpose**: Output model for chat responses
- **Schema**:
  - `response`: string - Answer from RAG agent
  - `sources`: array of objects - Citations to source materials
  - `processing_time`: number - Time taken in seconds
  - `timestamp`: string - ISO 8601 timestamp
  - `query_id`: string - Unique request identifier

### ErrorResponse
- **Purpose**: Error response model
- **Schema**:
  - `error_code`: string - Machine-readable error code
  - `message`: string - Human-readable message
  - `details`: object (optional) - Additional error details
  - `timestamp`: string - ISO 8601 timestamp

## Performance Specifications

- **Response Time**: <5 seconds for 95% of requests (local development)
- **Concurrency**: Support for 10+ concurrent requests
- **Error Rate**: <1% during normal operation
- **Availability**: 100% during local development sessions

## Security Considerations

- Input validation prevents injection attacks
- No sensitive data exposed in responses
- Rate limiting available through middleware (not implemented in scope)
- API authentication available through dependencies (not implemented in scope)