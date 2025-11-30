"""
WebScraperTool - Fetch and extract article content from URLs

Supports both RSS feeds and HTML pages. For RSS feeds, uses content tags
when available to avoid fetching full HTML. For HTML pages, extracts
article content using newspaper3k and BeautifulSoup4.
"""

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from newspaper import Article

logger = logging.getLogger(__name__)


class WebScraperTool(BaseTool):
    """Custom tool to fetch and parse content from web pages and RSS feeds."""

    def __init__(self):
        super().__init__(
            name="web_scraper",
            description=(
                "Fetches content from web pages and RSS feeds. "
                "Supports RSS/Atom feeds and HTML article pages. "
                "Returns article metadata, content, and discovered links."
            ),
        )
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (compatible; MyNewsRobot/1.0; "
                    "+https://mkfoster.com)"
                )
            }
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Run the tool asynchronously (required by ADK)."""
        return self.run(
            url=args["url"],
            mode=args.get("mode", "auto"),
            extract_links=args.get("extract_links", False),
            timeout=args.get("timeout", 30),
        )

    def run(
        self,
        url: str,
        mode: str = "auto",
        extract_links: bool = False,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        Fetch and parse content from a URL.

        Args:
            url: URL to fetch
            mode: 'auto', 'rss', or 'html' (auto-detects if 'auto')
            extract_links: Whether to extract article links from the page
            timeout: Request timeout in seconds

        Returns:
            Dictionary containing:
            - success: bool
            - url: str
            - type: 'rss' or 'html'
            - title: Optional[str]
            - content: Optional[str]
            - summary: Optional[str]
            - author: Optional[str]
            - published_date: Optional[str]
            - links: List[Dict] (if extract_links=True)
            - error: Optional[str]
        """
        logger.info(f"Fetching URL: {url} (mode={mode})")

        try:
            # Auto-detect content type if needed
            if mode == "auto":
                mode = self._detect_content_type(url)
                logger.info(f"Auto-detected content type: {mode}")

            if mode == "rss":
                return self._parse_rss_feed(url)
            else:
                return self._parse_html_page(url, extract_links, timeout)

        except Exception as e:
            logger.error(f"Error fetching {url}: {e}", exc_info=True)
            return {
                "success": False,
                "url": url,
                "error": str(e),
            }

    def _detect_content_type(self, url: str) -> str:
        """
        Detect if URL is an RSS feed or HTML page.

        Args:
            url: URL to check

        Returns:
            'rss' or 'html'
        """
        # Common RSS patterns
        rss_indicators = [
            "/feed",
            "/rss",
            "/atom",
            ".xml",
            "feed.xml",
            "rss.xml",
        ]

        url_lower = url.lower()
        if any(indicator in url_lower for indicator in rss_indicators):
            return "rss"

        # Try a HEAD request to check Content-Type
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            content_type = response.headers.get("Content-Type", "").lower()
            if any(
                rss_type in content_type
                for rss_type in ["xml", "rss", "atom", "feed"]
            ):
                return "rss"
        except Exception:
            pass

        return "html"

    def _parse_rss_feed(self, url: str) -> Dict[str, Any]:
        """
        Parse an RSS/Atom feed.

        Args:
            url: RSS feed URL

        Returns:
            Feed data with entries
        """
        logger.info(f"Parsing RSS feed: {url}")

        feed = feedparser.parse(url)

        if feed.bozo:
            logger.warning(f"RSS feed has parsing errors: {feed.bozo_exception}")

        # Extract feed metadata
        feed_title = feed.feed.get("title", "")
        feed_description = feed.feed.get("description", "")

        # Extract entries
        entries = []
        for entry in feed.entries:
            # Get content from various possible fields
            content = None
            summary = None

            # Try content field first (often has full text)
            if hasattr(entry, "content"):
                content = entry.content[0].value
            elif hasattr(entry, "description"):
                content = entry.description

            # Get summary
            if hasattr(entry, "summary"):
                summary = entry.summary

            # Get published date
            published = None
            if hasattr(entry, "published"):
                published = entry.published
            elif hasattr(entry, "updated"):
                published = entry.updated

            entries.append(
                {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "content": content,
                    "summary": summary,
                    "author": entry.get("author", ""),
                    "published_date": published,
                }
            )

        return {
            "success": True,
            "url": url,
            "type": "rss",
            "title": feed_title,
            "description": feed_description,
            "entries": entries,
            "entry_count": len(entries),
        }

    def _parse_html_page(
        self, url: str, extract_links: bool, timeout: int
    ) -> Dict[str, Any]:
        """
        Parse an HTML article page.

        Args:
            url: HTML page URL
            extract_links: Whether to extract article links
            timeout: Request timeout

        Returns:
            Article data
        """
        logger.info(f"Parsing HTML page: {url}")

        # Use newspaper3k for article extraction
        article = Article(url)
        article.download()
        article.parse()

        result = {
            "success": True,
            "url": url,
            "type": "html",
            "title": article.title,
            "content": article.text,
            "summary": article.meta_description or article.text[:500],
            "author": ", ".join(article.authors) if article.authors else None,
            "published_date": (
                article.publish_date.isoformat() if article.publish_date else None
            ),
            "top_image": article.top_image,
            "images": list(article.images),
        }

        # Extract links if requested
        if extract_links:
            result["links"] = self._extract_article_links(url, article.html)

        return result

    def _extract_article_links(self, base_url: str, html: str) -> List[Dict[str, str]]:
        """
        Extract article links from HTML.

        Args:
            base_url: Base URL for resolving relative links
            html: HTML content

        Returns:
            List of link dictionaries
        """
        soup = BeautifulSoup(html, "html.parser")
        links = []

        # Find all article-like links
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            absolute_url = urljoin(base_url, href)

            # Filter out non-article links
            parsed = urlparse(absolute_url)
            if not parsed.scheme or parsed.scheme not in ["http", "https"]:
                continue

            # Skip common non-article patterns
            skip_patterns = [
                "#",
                "javascript:",
                "mailto:",
                "/tag/",
                "/category/",
                "/author/",
                "/page/",
            ]
            if any(pattern in href for pattern in skip_patterns):
                continue

            links.append(
                {
                    "url": absolute_url,
                    "text": a_tag.get_text(strip=True),
                    "title": a_tag.get("title", ""),
                }
            )

        logger.info(f"Extracted {len(links)} links from {base_url}")
        return links

    def close(self):
        """Clean up resources."""
        if self.session:
            self.session.close()
