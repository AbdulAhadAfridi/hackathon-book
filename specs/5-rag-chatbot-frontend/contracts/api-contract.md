# API Contract: RAG Chatbot Frontend-Backend Communication

## Overview
This document defines the API contract between the RAGChatbot React component and the FastAPI backend service.

## Base URL
`http://localhost:8000` (or production equivalent)

## Endpoints

### POST /api/chat
Submit a user query to the RAG system and receive a response.

#### Request
```json
{
  "query": "string (required) - The user's question",
  "selected_text": "string | null (optional) - Context from the current page"
}
```

#### Response (Success)
**Status: 200 OK**
```json
{
  "response": "string - The answer from the RAG system",
  "sources": [
    {
      "url": "string - Source URL",
      "section": "string - Section name",
      "heading": "string - Heading text",
      "relevance_score": "number - Similarity score (0.0-1.0)"
    }
  ],
  "processing_time": "number - Time taken in seconds",
  "timestamp": "string - ISO timestamp",
  "query_id": "string - Unique query identifier"
}
```

#### Response (Error)
**Status: 400 Bad Request**
```json
{
  "error_code": "string - Error identifier",
  "message": "string - Human-readable error message",
  "details": "object | null - Additional error details",
  "timestamp": "string - ISO timestamp"
}
```

**Status: 500 Internal Server Error**
```json
{
  "error_code": "string - Error identifier",
  "message": "string - Human-readable error message",
  "details": "object | null - Additional error details",
  "timestamp": "string - ISO timestamp"
}
```

### GET /health
Check the health status of the API.

#### Response
**Status: 200 OK**
```json
{
  "status": "string - Health status ('healthy' or 'degraded')",
  "timestamp": "string - ISO timestamp",
  "service": "string - Service name",
  "version": "string - Service version",
  "components": {
    "rag_agent": "string - RAG agent status"
  }
}
```

## Error Codes
- `INVALID_QUERY`: Query is empty or invalid
- `AGENT_UNINITIALIZED`: RAG agent is not ready
- `PROCESSING_ERROR`: General processing error

## CORS Policy
The backend must be configured to allow requests from the Docusaurus frontend domain.

## Content Types
- Requests: `application/json`
- Responses: `application/json`