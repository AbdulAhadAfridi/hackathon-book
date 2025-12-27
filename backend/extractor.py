"""
Content extractor for the RAG ingestion pipeline
"""

from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from models import ContentDocument
from constants import (
    DOCUSAURUS_CONTENT_SELECTORS,
    DOCUSAURUS_EXCLUDE_SELECTORS,
    DEFAULT_HEADERS
)


def extract_content(html: str, url: str) -> ContentDocument:
    """
    Extract clean text content from HTML using BeautifulSoup
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Remove elements that should be excluded (navigation, footer, etc.)
    for selector in DOCUSAURUS_EXCLUDE_SELECTORS:
        for element in soup.select(selector):
            element.decompose()

    # Try to find content using Docusaurus-specific selectors
    content_element = None
    for selector in DOCUSAURUS_CONTENT_SELECTORS:
        content_element = soup.select_one(selector)
        if content_element:
            break

    # If no specific content element found, use the body
    if not content_element:
        content_element = soup.find('body')

    # Extract text content
    content = ""
    if content_element:
        content = content_element.get_text(separator=' ', strip=True)

    # Extract headings
    headings = extract_headings(soup)

    # Extract title
    title_tag = soup.find('title')
    title = title_tag.get_text().strip() if title_tag else ""

    # Extract section information (could be from URL path or heading structure)
    section = extract_section_info(url, headings)

    # Create and return ContentDocument
    return ContentDocument(
        url=url,
        content=content,
        title=title,
        headings=headings,
        section=section
    )


def extract_headings(soup: BeautifulSoup) -> List[str]:
    """
    Extract headings (h1-h6) from the HTML
    """
    headings = []
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        text = heading.get_text(strip=True)
        if text:
            headings.append(text)
    return headings


def extract_section_info(url: str, headings: List[str]) -> str:
    """
    Extract section information from URL or headings
    """
    # Try to extract from URL path
    parsed_url = urlparse(url)
    path_parts = [part for part in parsed_url.path.split('/') if part]

    if path_parts:
        # Use the last meaningful path part as section
        section = path_parts[-1]
        # Replace hyphens/underscores with spaces and title case
        section = section.replace('-', ' ').replace('_', ' ').title()
        return section

    # If no path info, use the first heading if available
    if headings:
        return headings[0]

    return "General"


def extract_clean_text_from_html(html: str) -> str:
    """
    Extract clean text from HTML, removing extra whitespace
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get text and clean it up
    text = soup.get_text(separator=' ')

    # Break into lines and remove leading/trailing space
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = ' '.join(chunk for chunk in chunks if chunk)

    return text


def extract_content_with_docusaurus_selectors(html: str, url: str) -> ContentDocument:
    """
    Extract content using Docusaurus-specific selectors
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Remove excluded elements
    for selector in DOCUSAURUS_EXCLUDE_SELECTORS:
        for element in soup.select(selector):
            element.decompose()

    # Find content element
    content_element = None
    for selector in DOCUSAURUS_CONTENT_SELECTORS:
        content_element = soup.select_one(selector)
        if content_element:
            break

    if content_element:
        # Extract clean text from the specific content area
        content = extract_clean_text_from_content_element(content_element)
    else:
        # Fallback to extracting from entire body
        content = extract_clean_text_from_html(html)

    # Extract headings from the entire document
    headings = extract_headings(soup)

    # Extract title
    title_tag = soup.find('title')
    title = title_tag.get_text().strip() if title_tag else ""

    # Extract section
    section = extract_section_info(url, headings)

    return ContentDocument(
        url=url,
        content=content,
        title=title,
        headings=headings,
        section=section
    )


def extract_clean_text_from_content_element(element: BeautifulSoup) -> str:
    """
    Extract clean text from a specific content element, preserving structure
    """
    # Remove any remaining excluded elements within the content area
    for selector in DOCUSAURUS_EXCLUDE_SELECTORS:
        for sub_element in element.select(selector):
            sub_element.decompose()

    # Get text content
    text = element.get_text(separator=' ')

    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)

    return text