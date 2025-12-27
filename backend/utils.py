"""
Utility functions for the RAG ingestion pipeline
"""

import re
from urllib.parse import urljoin, urlparse
from typing import Optional


def is_valid_url(url: str) -> bool:
    """
    Validate if a string is a properly formatted URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_url_input(url: str) -> tuple[bool, str]:
    """
    Validate URL input with detailed error message
    Returns (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "URL must be a non-empty string"

    if len(url) > 2048:  # Common URL length limit
        return False, "URL exceeds maximum length of 2048 characters"

    if not url.startswith(('http://', 'https://')):
        return False, "URL must start with http:// or https://"

    if not is_valid_url(url):
        return False, "URL is not properly formatted"

    return True, ""


def sanitize_url(url: str) -> str:
    """
    Sanitize and normalize a URL
    """
    # Remove trailing slashes
    url = url.rstrip('/')
    # Ensure proper scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url


def is_same_domain(base_url: str, test_url: str) -> bool:
    """
    Check if two URLs are from the same domain
    """
    try:
        base_domain = urlparse(base_url).netloc
        test_domain = urlparse(test_url).netloc
        return base_domain == test_domain
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """
    Normalize URL by removing fragments and standardizing format
    """
    parsed = urlparse(url)
    # Reconstruct URL without fragment
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    return normalized