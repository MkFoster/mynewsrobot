"""
NewsResearchAgent - Discovers articles from configured news sources and user bookmarks

This agent:
1. Loads news sources from configuration (RSS feeds and HTML pages)
2. Loads user bookmarks from weekly_bookmarks.yaml
3. Uses WebScraperTool to fetch and parse content
4. Returns a list of discovered article URLs with metadata
5. Uses memory service to avoid duplicate articles
"""

import logging
from typing import Any, Dict, List

from google.adk.agents.llm_agent import Agent

from ..tools import BookmarkLoaderTool, WebScraperTool
from ..utils.config_loader import config_loader
from ..utils.memory_manager import memory_manager

logger = logging.getLogger(__name__)

# Agent configuration
AGENT_NAME = "NewsResearchAgent"
AGENT_MODEL = "gemini-2.0-flash-exp"
AGENT_DESCRIPTION = (
    "Discovers articles from configured news sources and user bookmarks"
)

AGENT_INSTRUCTION = """
You are a news research agent responsible for discovering articles from configured sources.

Your tasks:
1. Load news sources from the configuration (RSS feeds and HTML pages)
2. Load user bookmarks from the weekly bookmarks file
3. Use the WebScraperTool to fetch content from each source
4. Extract article URLs, titles, summaries, and metadata
5. Check each article URL against the memory to avoid duplicates
6. Return a comprehensive list of all discovered articles

Guidelines:
- For RSS feeds: Extract all entries with their metadata
- For HTML pages: Extract article links found on the page
- User bookmarks should be included even if already in memory (they're manually selected)
- Each article should include: url, title, summary (if available), source, published_date
- Filter out any URLs that are already in the processed memory (except bookmarks)
- Return articles in a structured format for the next agent

Output format:
Return a JSON object with:
- discovered_articles: List of article dictionaries with url, title, summary, source, published_date, is_bookmark
- total_count: Total number of articles discovered
- new_count: Number of new articles (not in memory)
- bookmark_count: Number of user bookmarks
"""


class NewsResearchAgent:
    """Factory class for creating the NewsResearchAgent."""

    @staticmethod
    def create_agent() -> Agent:
        """
        Create and configure the NewsResearchAgent.

        Returns:
            Configured Agent instance with tools and instructions
        """
        # Initialize tools
        web_scraper = WebScraperTool()
        bookmark_loader = BookmarkLoaderTool()

        # Create the agent with ADK
        agent = Agent(
            name=AGENT_NAME,
            model=AGENT_MODEL,
            description=AGENT_DESCRIPTION,
            instruction=AGENT_INSTRUCTION,
            tools=[web_scraper, bookmark_loader],
        )

        logger.info(f"Created {AGENT_NAME} with model {AGENT_MODEL}")
        return agent

    @staticmethod
    def get_news_sources() -> List[Dict[str, Any]]:
        """
        Get configured news sources from config.

        Returns:
            List of news source pages with URLs and metadata
        """
        news_config = config_loader.get_news_sources()
        sources = []

        for category, category_data in (news_config.get("news_sources") or {}).items():
            pages = category_data.get("pages") or []
            for page in pages:
                sources.append(
                    {
                        "url": page["url"],
                        "name": page["name"],
                        "type": page.get("type", "auto"),
                        "category": category,
                    }
                )

        logger.info(f"Loaded {len(sources)} news sources from configuration")
        return sources

    @staticmethod
    def is_processed(url: str) -> bool:
        """
        Check if a URL has already been processed.

        Args:
            url: Article URL to check

        Returns:
            True if URL was previously processed
        """
        return memory_manager.is_processed(url)

    @staticmethod
    def mark_as_processed(urls: List[str]) -> None:
        """
        Mark URLs as processed in memory.

        Args:
            urls: List of article URLs to mark as processed
        """
        for url in urls:
            memory_manager.add_processed_url(url)
        logger.info(f"Marked {len(urls)} URLs as processed")
