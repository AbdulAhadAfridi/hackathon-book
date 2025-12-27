# Quickstart: FastAPI Integration

## Prerequisites

- Python 3.11+
- FastAPI dependencies
- Access to RAG agent (from Spec-3)
- API keys for OpenAI and other services

## Setup

### 1. Environment Configuration

Install the required dependencies:

```bash
cd backend
pip install fastapi uvicorn pydantic python-dotenv
```

### 2. Start the API Server

Start the FastAPI server locally:

```bash
cd backend
python main.py
```

Alternatively, run directly with uvicorn:

```bash
cd backend
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### 3. API Documentation

Access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage

### Chat Endpoint

Send a chat query to the backend:

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main concept of the book?",
    "selected_text": "Optional text selected by user for additional context"
  }'
```

#### Response Format:
```json
{
  "response": "The main concept of the book is...",
  "sources": [
    {
      "url": "https://book.example.com/page",
      "section": "Chapter 1",
      "heading": "Introduction"
    }
  ],
  "processing_time": 1.234,
  "timestamp": "2025-12-26T10:30:00Z",
  "query_id": "abc123"
}
```

### Error Handling

The API returns structured error responses:

```json
{
  "error_code": "AGENT_UNAVAILABLE",
  "message": "The RAG agent is temporarily unavailable. Please try again later.",
  "details": {
    "type": "ServiceUnavailable",
    "retry_after": 30
  },
  "timestamp": "2025-12-26T10:30:00Z"
}
```

## Examples

### Basic Query
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the key principles explained in the book?"}'
```

### Query with Selected Text
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the implications of this?",
    "selected_text": "This is the specific text I am referring to in my question..."
  }'
```

## Local Development

### Running with Auto-reload
```bash
cd backend
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Environment Variables
Set the following environment variables in your `.env` file:
- `OPENAI_API_KEY`: API key for OpenAI
- `COHERE_API_KEY`: API key for Cohere
- `QDRANT_URL`: URL for Qdrant vector database
- `QDRANT_API_KEY`: API key for Qdrant

## Troubleshooting

### Common Issues:

1. **Port Already in Use**: Change port with `--port 8001`
2. **API Keys Missing**: Ensure all required API keys are set in environment
3. **RAG Agent Unreachable**: Verify RAG agent is running and accessible
4. **CORS Errors**: Check that CORS is properly configured for frontend domain
5. **Slow Responses**: Check network connectivity to external services

### Health Check
Verify the API is running:
```bash
curl http://localhost:8000/health
```