"""
End-to-end test for the RAG ingestion pipeline
"""

import unittest
from unittest.mock import patch, MagicMock
from backend.crawler import Crawler, Page
from backend.extractor import extract_content
from backend.chunker import create_chunks_from_document
from backend.models import ContentDocument


class TestPipeline(unittest.TestCase):
    """
    End-to-end tests for the RAG ingestion pipeline
    """

    def setUp(self):
        """
        Set up test fixtures
        """
        self.sample_html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Main Heading</h1>
                <p>This is a sample content paragraph for testing.</p>
                <h2>Sub Heading</h2>
                <p>Another paragraph with more content.</p>
            </body>
        </html>
        """
        self.sample_url = "https://example.com/test-page"

    def test_content_extraction(self):
        """
        Test that content extraction works correctly
        """
        content_doc = extract_content(self.sample_html, self.sample_url)

        self.assertIsInstance(content_doc, ContentDocument)
        self.assertEqual(content_doc.url, self.sample_url)
        self.assertIn("sample content", content_doc.content.lower())
        self.assertEqual(content_doc.title, "Test Page")
        self.assertIn("Main Heading", content_doc.headings)

    def test_content_chunking(self):
        """
        Test that content chunking works correctly
        """
        content_doc = extract_content(self.sample_html, self.sample_url)
        chunks = create_chunks_from_document(content_doc, chunk_size=100, chunk_overlap=10)

        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertIsNotNone(chunk.text)
            self.assertGreater(len(chunk.text), 0)
            self.assertIn("url", chunk.metadata)
            self.assertIn("section", chunk.metadata)

    def test_crawler_initialization(self):
        """
        Test that the crawler can be initialized
        """
        crawler = Crawler(max_pages=10, delay=0.1)
        self.assertEqual(crawler.max_pages, 10)
        self.assertEqual(crawler.delay, 0.1)

    @patch('backend.http_client.requests.Session.get')
    def test_crawler_with_mock_response(self, mock_get):
        """
        Test crawler with mocked HTTP response
        """
        # Mock a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = self.sample_html
        mock_get.return_value = mock_response

        crawler = Crawler(max_pages=1, delay=0)
        pages = crawler.crawl(self.sample_url)

        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0].url, self.sample_url)
        self.assertEqual(pages[0].status_code, 200)
        self.assertIn("sample content", pages[0].html_content.lower())


def run_tests():
    """
    Run the end-to-end tests
    """
    unittest.main()


if __name__ == "__main__":
    run_tests()