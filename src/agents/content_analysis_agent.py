"""
ContentAnalysisAgent - Analyzes and selects top 20 articles based on topic priorities

This agent:
1. Receives enriched articles with full content
2. Loads topic priorities from configuration
3. Analyzes each article against topic keywords and priorities
4. Ensures user bookmarks (priority 11) are always included
5. Selects the top 20 articles based on priority and relevance
"""

import logging
from typing import Any, Dict

from google.adk.agents.llm_agent import Agent

from ..utils.config_loader import config_loader

logger = logging.getLogger(__name__)

# Agent configuration
AGENT_NAME = "ContentAnalysisAgent"
AGENT_MODEL = "gemini-2.0-flash-exp"
AGENT_DESCRIPTION = (
    "Analyzes articles and selects top 20 based on topic priorities and relevance"
)

AGENT_INSTRUCTION = """
You are a content analysis agent responsible for selecting the top 20 articles.

Your tasks:
1. Receive a list of enriched articles with full content
2. Load topic priorities from configuration
3. Analyze each article for topic relevance:
   - Match article content against topic keywords
   - Assign priority score based on matching topics (7-10)
   - User bookmarks always get priority 11 (highest)
4. Score articles based on:
   - Topic priority (11 for bookmarks, 7-10 for topics)
   - Keyword match density
   - Content quality and depth
   - Recency (newer articles preferred)
5. Select exactly 20 articles with highest scores

Topic Priority Scale:
- 11 = User bookmarks (MUST be included if available)
- 10 = Must-have topics (highest configured priority)
- 9 = Very interested
- 8 = Interested
- 7 = Nice to have

Selection Rules:
- ALL user bookmarks must be included (priority 11)
- If bookmarks < 20, fill remaining slots with highest priority articles
- If bookmarks >= 20, include all bookmarks and select 0 other articles
- Prefer articles with multiple topic matches
- Balance across different topics when possible
- Prefer recent articles (within last 7 days) over older ones

Output format:
Return a JSON object with:
- selected_articles: List of exactly 20 articles (or all if < 20 total)
- bookmark_count: Number of user bookmarks included
- priority_distribution: Count of articles by priority level (11, 10, 9, 8, 7)
- topic_distribution: Count of articles by topic name
- analysis_summary: Brief explanation of selection criteria
"""


class ContentAnalysisAgent:
    """Factory class for creating the ContentAnalysisAgent."""

    @staticmethod
    def create_agent() -> Agent:
        """
        Create and configure the ContentAnalysisAgent.

        Returns:
            Configured Agent instance with instructions
        """
        # Create the agent with ADK (no tools needed - pure analysis)
        agent = Agent(
            name=AGENT_NAME,
            model=AGENT_MODEL,
            description=AGENT_DESCRIPTION,
            instruction=AGENT_INSTRUCTION,
            tools=[],  # No tools - uses LLM analysis only
        )

        logger.info(f"Created {AGENT_NAME} with model {AGENT_MODEL}")
        return agent

    @staticmethod
    def get_topic_priorities() -> Dict[str, Any]:
        """
        Get configured topic priorities.

        Returns:
            Topic priorities configuration
        """
        return config_loader.get_topic_priorities()
