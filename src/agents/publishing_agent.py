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

from google.adk.agents.llm_agent import Agent

from ..tools import WordPressTool
from ..utils.config_loader import config_loader

logger = logging.getLogger(__name__)

# Agent configuration
AGENT_NAME = "PublishingAgent"
AGENT_MODEL = "gemini-2.0-flash-exp"
AGENT_DESCRIPTION = "Publishes newsletter content to WordPress as a private post"

AGENT_INSTRUCTION = """
You are a publishing agent responsible for posting the newsletter to WordPress.

Your tasks:
1. Receive formatted newsletter with title, excerpt, and HTML content
2. Load WordPress configuration (site URL, credentials)
3. Use WordPressTool to create a new post with:
   - Title from the newsletter
   - Content (full HTML)
   - Excerpt
   - Status: "private" (not published publicly)
   - Categories: ["WeeklySummary"]
4. Return publication confirmation with URLs

Publishing Guidelines:
- Always set status to "private" - posts should not be publicly visible
- Always add "WeeklySummary" category
- Include both the excerpt and full content
- Preserve HTML formatting exactly as provided
- Handle errors gracefully and report them

Success Criteria:
- Post created successfully in WordPress
- Post is marked as private
- WeeklySummary category is assigned
- Both post URL and edit URL are returned

Output format:
Return a JSON object with:
- success: boolean
- post_id: WordPress post ID
- post_url: Public URL (will show 404 if private)
- edit_url: WordPress admin edit URL
- status: Post status ("private")
- categories: List of assigned categories
- error: Error message if failed
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
        # Load WordPress configuration
        wp_config = config_loader.get_wordpress_config()
        wp_settings = wp_config.get("wordpress", {})

        # Initialize WordPress tool
        wordpress_tool = WordPressTool(
            site_url=wp_settings.get("site_url", "https://mkfoster.com"),
            username=config_loader.get_env("WORDPRESS_USERNAME", ""),
            app_password=config_loader.get_env("WORDPRESS_APP_PASSWORD", ""),
            api_endpoint=wp_settings.get("api_endpoint", "/wp-json/wp/v2"),
        )

        # Create the agent with ADK
        agent = Agent(
            name=AGENT_NAME,
            model=AGENT_MODEL,
            description=AGENT_DESCRIPTION,
            instruction=AGENT_INSTRUCTION,
            tools=[wordpress_tool],
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
