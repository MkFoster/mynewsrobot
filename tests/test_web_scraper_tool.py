"""
Unit tests for WebScraperTool
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.tools.web_scraper_tool import WebScraperTool


@pytest.fixture
def scraper():
    """Create a WebScraperTool instance for testing."""
    return WebScraperTool()


def test_web_scraper_init(scraper):
    """Test WebScraperTool initialization."""
    assert scraper.name == "web_scraper"
    assert scraper.session is not None
    assert "User-Agent" in scraper.session.headers


def test_detect_rss_from_url(scraper):
    """Test RSS detection from URL patterns."""
    rss_urls = [
        "https://example.com/feed/",
        "https://example.com/rss.xml",
        "https://example.com/atom.xml",
        "https://example.com/feed",
    ]
    
    for url in rss_urls:
        content_type = scraper._detect_content_type(url)
        assert content_type == "rss", f"Failed to detect RSS for {url}"


def test_detect_html_from_url(scraper):
    """Test HTML detection from URL patterns."""
    html_urls = [
        "https://example.com/article",
        "https://example.com/blog/post-title",
        "https://example.com/news/story",
    ]
    
    for url in html_urls:
        content_type = scraper._detect_content_type(url)
        assert content_type == "html", f"Incorrectly detected RSS for {url}"


@patch("src.tools.web_scraper_tool.feedparser")
def test_parse_rss_feed_success(mock_feedparser, scraper):
    """Test successful RSS feed parsing."""
    # Mock feedparser response
    mock_feed = MagicMock()
    mock_feed.bozo = False
    mock_feed.feed = {
        "title": "Test Feed",
        "description": "Test Description"
    }
    mock_feed.entries = [
        {
            "title": "Article 1",
            "link": "https://example.com/article1",
            "summary": "Summary 1",
            "author": "Author 1",
            "published": "2025-11-30",
        }
    ]
    mock_feedparser.parse.return_value = mock_feed
    
    result = scraper._parse_rss_feed("https://example.com/feed")
    
    assert result["success"] is True
    assert result["type"] == "rss"
    assert result["title"] == "Test Feed"
    assert result["entry_count"] == 1
    assert len(result["entries"]) == 1
    assert result["entries"][0]["title"] == "Article 1"


@patch("src.tools.web_scraper_tool.Article")
def test_parse_html_page_success(mock_article_class, scraper):
    """Test successful HTML page parsing."""
    # Mock Article instance
    mock_article = MagicMock()
    mock_article.title = "Test Article"
    mock_article.text = "Article content here"
    mock_article.meta_description = "Test description"
    mock_article.authors = ["Author Name"]
    mock_article.publish_date = None
    mock_article.top_image = "https://example.com/image.jpg"
    mock_article.images = ["https://example.com/image.jpg"]
    mock_article.html = "<html><body>Test</body></html>"
    
    mock_article_class.return_value = mock_article
    
    result = scraper._parse_html_page("https://example.com/article", False, 30)
    
    assert result["success"] is True
    assert result["type"] == "html"
    assert result["title"] == "Test Article"
    assert result["content"] == "Article content here"
    assert result["author"] == "Author Name"


def test_run_auto_mode_rss(scraper):
    """Test run() with auto mode detecting RSS."""
    with patch.object(scraper, "_detect_content_type", return_value="rss"):
        with patch.object(scraper, "_parse_rss_feed") as mock_parse:
            mock_parse.return_value = {"success": True, "type": "rss"}
            
            result = scraper.run("https://example.com/feed", mode="auto")
            
            mock_parse.assert_called_once_with("https://example.com/feed")
            assert result["success"] is True


def test_run_handles_errors(scraper):
    """Test run() error handling."""
    with patch.object(scraper, "_detect_content_type", side_effect=Exception("Test error")):
        result = scraper.run("https://example.com/test")
        
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]


def test_extract_article_links(scraper):
    """Test article link extraction from HTML."""
    html = """
    <html>
        <body>
            <a href="https://example.com/article1">Article 1</a>
            <a href="/relative/article2">Article 2</a>
            <a href="#anchor">Skip this</a>
            <a href="javascript:void(0)">Skip this</a>
        </body>
    </html>
    """
    
    links = scraper._extract_article_links("https://example.com", html)
    
    # Should extract absolute and relative URLs, skip anchor/javascript
    assert len(links) >= 1
    assert any(link["url"] == "https://example.com/article1" for link in links)


def test_close(scraper):
    """Test session cleanup."""
    scraper.close()
    # Just ensure no errors occur
