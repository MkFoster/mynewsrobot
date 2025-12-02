"""
PublishingAgent - Publishes newsletter to WordPress

This agent:
1. Receives formatted newsletter content
2. Loads WordPress configuration
3. Uses WordPressTool to create a post
4. Sets post status to "private"
5. Adds "WeeklySummary" category
6. Returns publication confirmation with URLs
"""

import logging
from typing import Any, Dict

from google.adk import Agent

from ..tools import publish_to_wordpress
from ..utils.config_loader import config_loader

logger = logging.getLogger(__name__)

# Agent configuration
AGENT_NAME = "PublishingAgent"
AGENT_MODEL = "gemini-2.5-flash"  # Updated to higher quota model
AGENT_DESCRIPTION = "Publishes newsletter content to WordPress as a private post"
AGENT_OUTPUT_KEY = "publication_result"  # Final result with post URL

AGENT_INSTRUCTION = """
You are a publishing agent. Your ONLY job is to call the publish_to_wordpress tool.

When you receive a request:
1. Extract the title, content, status, categories, and excerpt from the user's message
2. IMMEDIATELY call the publish_to_wordpress tool with those parameters
3. Do NOT provide any text response until AFTER you've called the tool
4. After the tool returns results, share the post_url and edit_url from the response

CRITICAL: You MUST call publish_to_wordpress. Do not explain, do not summarize - just call the tool first.
"""


class PublishingAgent:
    """Factory class for creating the PublishingAgent."""

    @staticmethod
    def create_agent() -> Agent:
        """
        Create and configure the PublishingAgent.

        Returns:
            Configured Agent instance with WordPress tool
        """
        # Create the agent with function-based tool
        agent = Agent(
            name=AGENT_NAME,
            model=AGENT_MODEL,
            description=AGENT_DESCRIPTION,
            instruction=AGENT_INSTRUCTION,
            tools=[publish_to_wordpress],
            output_key=AGENT_OUTPUT_KEY,  # Final output
        )

        logger.info(f"Created {AGENT_NAME} with model {AGENT_MODEL}")
        return agent

    @staticmethod
    def get_wordpress_config() -> Dict[str, Any]:
        """
        Get WordPress configuration.

        Returns:
            WordPress settings
        """
        return config_loader.get_wordpress_config()
