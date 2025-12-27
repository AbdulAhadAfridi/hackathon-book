"""
Web crawler for the RAG ingestion pipeline
"""

import time
import requests
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from typing import List, Set, Optional, Dict, Any
from dataclasses import dataclass

from http_client import HTTPClient
from utils import is_same_domain, normalize_url
from constants import DEFAULT_HEADERS


@dataclass
class Page:
    """
    Represents a web page discovered during crawling
    """
    url: str
    title: str = ""
    html_content: str = ""
    status_code: int = 0
    headings: List[str] = None

    def __post_init__(self):
        if self.headings is None:
            self.headings = []


class Crawler:
    """
    Web crawler for discovering and extracting content from Docusaurus sites
    """

    def __init__(self, max_pages: int = 1000, delay: float = 1.0):
        self.max_pages = max_pages
        self.delay = delay
        self.http_client = HTTPClient()
        self.visited_urls: Set[str] = set()
        self.discovered_urls: Set[str] = set()

    def _is_valid_url(self, url: str, base_domain: str) -> bool:
        """
        Check if URL is valid and belongs to the same domain
        """
        try:
            parsed = urlparse(url)
            # Only process http/https URLs from the same domain
            if parsed.scheme not in ['http', 'https']:
                return False
            if not is_same_domain(f"{parsed.scheme}://{parsed.netloc}", base_domain):
                return False
            # Skip URLs with fragments that might be anchors
            if parsed.fragment:
                return False
            return True
        except Exception:
            return False

    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """
        Extract all links from HTML content
        """
        soup = BeautifulSoup(html, 'html.parser')
        links = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            # Normalize the URL
            normalized_url = normalize_url(absolute_url)
            links.append(normalized_url)

        return links

    def _extract_title(self, html: str) -> str:
        """
        Extract title from HTML
        """
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        return ""

    def crawl(self, start_url: str) -> List[Page]:
        """
        Crawl the website starting from the given URL using breadth-first search
        """
        # Normalize the start URL
        start_url = normalize_url(start_url)
        base_domain = f"{urlparse(start_url).scheme}://{urlparse(start_url).netloc}"

        # Initialize the queue with the start URL
        queue = [start_url]
        pages: List[Page] = []

        while queue and len(pages) < self.max_pages:
            current_url = queue.pop(0)

            # Skip if already visited
            if current_url in self.visited_urls:
                continue

            try:
                # Add delay between requests to be respectful to the server
                if self.visited_urls:  # Skip delay for first request
                    time.sleep(self.delay)

                print(f"Processing: {current_url}")

                # Fetch the page content
                response = self.http_client.get(current_url, timeout=30)
                status_code = response.status_code

                if status_code == 200:
                    html_content = response.text
                    title = self._extract_title(html_content)

                    # Create page object
                    page = Page(
                        url=current_url,
                        title=title,
                        html_content=html_content,
                        status_code=status_code
                    )
                    pages.append(page)

                    # Extract links from the page
                    links = self._extract_links(html_content, current_url)

                    # Add valid links to the queue
                    for link in links:
                        if (link not in self.visited_urls and
                            link not in queue and
                            self._is_valid_url(link, base_domain)):
                            queue.append(link)

                else:
                    print(f"Failed to fetch {current_url}: Status {status_code}")

                # Mark as visited
                self.visited_urls.add(current_url)

            except Exception as e:
                print(f"Error processing {current_url}: {str(e)}")
                continue

        return pages


def crawl_website(url: str, max_pages: int = 1000) -> List[Page]:
    """
    Crawl a website starting from the given URL and discover all accessible pages
    """
    crawler = Crawler(max_pages=max_pages, delay=1.0)
    return crawler.crawl(url)