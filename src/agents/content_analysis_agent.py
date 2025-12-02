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

from google.adk import Agent

from ..tools import get_topic_priorities

logger = logging.getLogger(__name__)

# Agent configuration
AGENT_NAME = "ContentAnalysisAgent"
AGENT_MODEL = "gemini-2.5-flash"  # Updated to higher quota model
AGENT_DESCRIPTION = (
    "Analyzes articles and selects top 20 based on topic priorities and relevance"
)
AGENT_OUTPUT_KEY = "selected_articles"

AGENT_INSTRUCTION = """
You analyze articles and select the top 20 for a newsletter based on topic priorities.

STEP 1: Call get_topic_priorities() tool
This returns topics with priority scores (7-11) and keywords. You MUST call this tool first.

STEP 2: Match each article to topics
For each article:
- Read the title and excerpt
- Match against topic keywords from get_topic_priorities()
- Assign the topic's priority score (7-11)
- Bookmarks (is_bookmark=true) automatically get priority 11

STEP 3: Select top 20 articles
Rules:
- Maximum 10 articles per topic (ensures diversity)
- Rank by priority score (highest first)
- Prefer recent articles if priorities are equal
- Include bookmarks first (priority 11)

STEP 4: Return JSON array
Return ONLY a JSON array with these fields for each article:
- All original fields (url, title, excerpt, source, category, published_date, is_bookmark)
- priority: number (7-11) - the score you assigned
- matched_topic: string - which topic it matched

Example:
[{"url": "...", "title": "...", "excerpt": "...", "source": "...", "category": "...", "published_date": "...", "is_bookmark": false, "priority": 10, "matched_topic": "AI/ML"}]

CRITICAL: Return ONLY valid JSON. No explanations. Call get_topic_priorities() first.
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
        # Create the agent with the get_topic_priorities tool
        agent = Agent(
            name=AGENT_NAME,
            model=AGENT_MODEL,
            description=AGENT_DESCRIPTION,
            instruction=AGENT_INSTRUCTION,
            tools=[get_topic_priorities],  # Add the function-based tool
            output_key=AGENT_OUTPUT_KEY,  # Limit context passed to next agent
        )

        logger.info(f"Created {AGENT_NAME} with model {AGENT_MODEL}")
        return agent
