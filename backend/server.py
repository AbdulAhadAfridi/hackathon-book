"""
Main entry point for the FastAPI server
Runs the FastAPI application locally for development
"""
import uvicorn
import logging
import sys
from api import app  # Import the FastAPI app from api.py


def setup_logging():
    """
    Set up basic logging configuration
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """
    Main function to run the FastAPI server
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting FastAPI server for RAG Chat API...")
    logger.info("Server will be available at http://localhost:8000")

    # Run the FastAPI application with uvicorn
    uvicorn.run(
        "api:app",  # Reference to the FastAPI app in api.py
        host="0.0.0.0",  # Listen on all available interfaces
        port=8000,  # Port for the server
        reload=True,  # Enable auto-reload for development
        log_level="info",  # Logging level
        workers=1,  # Number of worker processes
        timeout_keep_alive=30,  # Keep-alive timeout
    )


if __name__ == "__main__":
    main()