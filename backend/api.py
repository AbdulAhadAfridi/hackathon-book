"""
FastAPI Integration for RAG Agent
Main implementation file for creating a FastAPI backend that exposes the RAG agent to the frontend
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import time
import logging
from datetime import datetime

# Import the RAG agent from the existing implementation
from agent import RAGAgent
import asyncio


# Request/Response models
class ChatRequest(BaseModel):
    """
    Request model for chat queries
    """
    query: str
    selected_text: Optional[str] = None


class Source(BaseModel):
    """
    Model for source citations
    """
    url: str
    section: str
    heading: str
    relevance_score: float


class ChatResponse(BaseModel):
    """
    Response model for chat responses
    """
    response: str
    sources: List[Source]
    processing_time: float
    timestamp: str
    query_id: str


class ErrorResponse(BaseModel):
    """
    Error response model
    """
    error_code: str
    message: str
    details: Optional[Dict[str, Any]]
    timestamp: str


# Initialize FastAPI app
app = FastAPI(
    title="RAG Chat API",
    description="API for RAG agent integration with frontend",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize the RAG agent
rag_agent = None

@app.on_event("startup")
async def startup_event():
    """
    Initialize the RAG agent on startup
    """
    global rag_agent
    try:
        # Initialize the RAG agent with appropriate configuration
        rag_agent = RAGAgent(model="gpt-4-turbo")  # Using the same model as in the original agent
        logging.info("RAG Agent initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize RAG Agent: {str(e)}")
        raise


@app.post("/api/chat",
          response_model=ChatResponse,
          responses={
              400: {"model": ErrorResponse, "description": "Bad request - invalid input"},
              503: {"model": ErrorResponse, "description": "Service unavailable - RAG agent unavailable"},
              500: {"model": ErrorResponse, "description": "Internal server error"}
          })
async def chat(request: ChatRequest):
    """
    Chat endpoint that processes user queries and returns responses from the RAG agent

    Args:
        request: ChatRequest containing the user query and optional selected text

    Returns:
        ChatResponse containing the agent's response and metadata
    """
    start_time = time.time()
    query_id = str(uuid.uuid4())

    try:
        # Validate input
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "INVALID_QUERY",
                    "message": "Query cannot be empty",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        # Process the query with the RAG agent
        global rag_agent
        if rag_agent is None:
            raise HTTPException(
                status_code=503,
                detail={
                    "error_code": "AGENT_UNINITIALIZED",
                    "message": "RAG agent is not initialized. Please restart the service.",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        # Call the RAG agent with the query and selected text
        # Since the agent methods are async, we need to run them in the current event loop
        if request.selected_text:
            result = await rag_agent.answer_query(
                query=request.query,
                user_provided_text=request.selected_text
            )
        else:
            result = await rag_agent.answer_query(
                query=request.query
            )

        # Calculate processing time
        processing_time = time.time() - start_time

        # Extract sources from the result
        sources = []
        if result.get('retrieved_context'):
            for item in result['retrieved_context']:
                if isinstance(item, dict):
                    sources.append(Source(
                        url=item.get('payload', {}).get('url', ''),
                        section=item.get('payload', {}).get('section', ''),
                        heading=item.get('payload', {}).get('heading', ''),
                        relevance_score=item.get('score', 0.0)
                    ))

        # Create and return the response
        response = ChatResponse(
            response=result['answer'],
            sources=sources,
            processing_time=processing_time,
            timestamp=datetime.utcnow().isoformat(),
            query_id=query_id
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the error
        logging.error(f"Error processing chat request {query_id}: {str(e)}")

        # Calculate processing time even for errors
        processing_time = time.time() - start_time

        # Return error response
        error_response = ErrorResponse(
            error_code="PROCESSING_ERROR",
            message="An error occurred while processing your request",
            details={
                "error": str(e),
                "query_id": query_id,
                "processing_time": processing_time
            },
            timestamp=datetime.utcnow().isoformat()
        )

        # Raise HTTP exception with error details
        raise HTTPException(
            status_code=500,
            detail=error_response.dict()
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running

    Returns:
        Health status information
    """
    global rag_agent
    return {
        "status": "healthy" if rag_agent is not None else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "FastAPI Chat API",
        "version": "1.0.0",
        "components": {
            "rag_agent": "initialized" if rag_agent is not None else "not_initialized"
        }
    }


# Additional utility endpoints can be added here
@app.get("/")
async def root():
    """
    Root endpoint for basic API information
    """
    return {
        "message": "RAG Chat API",
        "version": "1.0.0",
        "endpoints": [
            {"method": "POST", "path": "/api/chat", "description": "Chat with the RAG agent"},
            {"method": "GET", "path": "/health", "description": "Health check"},
            {"method": "GET", "path": "/docs", "description": "API Documentation (Swagger)"},
            {"method": "GET", "path": "/redoc", "description": "API Documentation (ReDoc)"}
        ]
    }