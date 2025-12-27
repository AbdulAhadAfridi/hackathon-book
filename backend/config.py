"""
Configuration loading for the RAG ingestion pipeline
"""

import os
from dotenv import load_dotenv
from typing import Optional


# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class to manage application settings
    """
    # API Keys and URLs
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Processing parameters
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    MAX_PAGES: int = int(os.getenv("MAX_PAGES", "1000"))

    # Crawler settings
    CRAWLER_DELAY: float = float(os.getenv("CRAWLER_DELAY", "1.0"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required configuration values are present
        """
        required_fields = [
            cls.COHERE_API_KEY,
            cls.QDRANT_URL,
            cls.QDRANT_API_KEY,
            cls.OPENAI_API_KEY
        ]

        return all(field for field in required_fields)

    @classmethod
    def get_cohere_config(cls) -> dict:
        """
        Get configuration for Cohere API
        """
        return {
            "api_key": cls.COHERE_API_KEY
        }

    @classmethod
    def get_qdrant_config(cls) -> dict:
        """
        Get configuration for Qdrant
        """
        return {
            "url": cls.QDRANT_URL,
            "api_key": cls.QDRANT_API_KEY
        }


def load_config() -> Config:
    """
    Load and return the configuration
    """
    return Config()