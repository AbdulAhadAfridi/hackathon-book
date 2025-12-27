"""
HTTP client with retry logic for the RAG ingestion pipeline
"""

import time
import requests
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class HTTPClient:
    """
    HTTP client with built-in retry logic and error handling
    """

    def __init__(self, max_retries: int = 3, backoff_factor: float = 0.3,
                 status_forcelist: tuple = (500, 502, 504)):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist

        # Create session with retry strategy
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=status_forcelist,
            backoff_factor=backoff_factor,
            # Handle connection errors as well
            raise_on_status=False
        )

        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update({
            'User-Agent': 'RAG-Ingestion-Pipeline/1.0'
        })

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Make a GET request with retry logic
        """
        try:
            response = self.session.get(url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            # Log the error and potentially re-raise or handle as needed
            print(f"Error making request to {url}: {str(e)}")
            raise

    def post(self, url: str, **kwargs) -> requests.Response:
        """
        Make a POST request with retry logic
        """
        try:
            response = self.session.post(url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error making POST request to {url}: {str(e)}")
            raise


def get_page_content(url: str, timeout: int = 10, max_retries: int = 3) -> Optional[str]:
    """
    Get content from a URL with retry logic
    """
    client = HTTPClient(max_retries=max_retries)

    try:
        response = client.get(url, timeout=timeout)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except Exception as e:
        print(f"Failed to retrieve content from {url}: {str(e)}")
        return None