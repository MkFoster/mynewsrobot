"""
ContentExtractionAgent - Extracts full article content from URLs

This agent:
1. Receives a list of article URLs from NewsResearchAgent
2. Uses WebScraperTool to extract full content from each URL
3. Optimizes by using RSS content tags when available
4. Returns enriched article data with full content for analysis
"""

import logging
from typing import Any, Dict

from google.adk.agents.llm_agent import Agent

from ..tools import WebScraperTool

logger = logging.getLogger(__name__)

# Agent configuration
AGENT_NAME = "ContentExtractionAgent"
AGENT_MODEL = "gemini-2.0-flash-exp"
AGENT_DESCRIPTION = "Extracts full article content from URLs using RSS or HTML parsing"

AGENT_INSTRUCTION = """
You are a content extraction agent responsible for fetching full article content.

Your tasks:
1. Receive a list of article URLs from the previous agent
2. For each URL, use the WebScraperTool to fetch content
3. Optimize extraction:
   - For RSS feeds: Use the content/summary from RSS tags (already provided)
   - For HTML pages: Fetch and extract the full article content
4. Extract and preserve all relevant metadata:
   - Title, author, published date, summary, full content
   - Images and media references
5. Return enriched articles with complete content

Guidelines:
- RSS content is often sufficient - avoid re-fetching if content is already complete
- For HTML articles, extract the main content body
- Preserve structure and formatting when possible
- Handle errors gracefully - mark failed extractions but continue processing
- Extract at least 100 words of content for each article
- If content extraction fails, use the summary as fallback

Output format:
Return a JSON object with:
- enriched_articles: List of articles with full content
- successful_extractions: Count of successfully extracted articles
- failed_extractions: Count of failed extractions
- total_processed: Total number of articles processed
"""


class ContentExtractionAgent:
    """Factory class for creating the ContentExtractionAgent."""

    @staticmethod
    def create_agent() -> Agent:
        """
        Create and configure the ContentExtractionAgent.

        Returns:
            Configured Agent instance with tools and instructions
        """
        # Initialize tool
        web_scraper = WebScraperTool()

        # Create the agent with ADK
        agent = Agent(
            name=AGENT_NAME,
            model=AGENT_MODEL,
            description=AGENT_DESCRIPTION,
            instruction=AGENT_INSTRUCTION,
            tools=[web_scraper],
        )

        logger.info(f"Created {AGENT_NAME} with model {AGENT_MODEL}")
        return agent
