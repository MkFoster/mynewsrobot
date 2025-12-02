"""
ContentWritingAgent - Writes summaries in user's personal style

This agent:
1. Receives the top 20 selected articles
2. Loads writing style guidelines from configuration
3. Writes summaries for each article (~200 tokens each)
4. Generates newsletter title and excerpt
5. Formats content for WordPress publication
"""

import logging
from typing import Any, Dict

from google.adk import Agent

from ..utils.config_loader import config_loader
from ..utils.date_formatter import format_newsletter_date

logger = logging.getLogger(__name__)

# Agent configuration
AGENT_NAME = "ContentWritingAgent"
AGENT_MODEL = "gemini-2.5-flash"  # Updated to higher quota model
AGENT_DESCRIPTION = (
    "Writes article summaries in user's personal style and formats for publication"
)
AGENT_OUTPUT_KEY = "newsletter_content"  # Only pass newsletter HTML to next agent

AGENT_INSTRUCTION = """
You are a content writing agent responsible for creating the weekly newsletter from RSS feed data.

Your tasks:
1. Receive 20 selected articles with RSS metadata (URL, title, excerpt, published_date)
2. Load writing style guidelines from configuration
3. Write a summary for each article (~200 tokens, ~150 words)
4. Generate newsletter title with current date
5. Create newsletter excerpt (150-200 words)
6. Format everything for WordPress publication

Content Sources:
- All articles come from RSS feeds with metadata: title, excerpt, URL, and date
- RSS excerpts provide the article summary - use this as your primary source
- No full article content is extracted - this is a smart RSS reader
- Expand and personalize the RSS excerpt in your writing style

Writing Style Guidelines:
- Study the style examples from mkfoster.com and fireflywp.com
- Conversational but professional tone
- Clear and concise technical writing
- Use concrete examples when possible
- Provide actionable insights
- IMPORTANT: Do NOT use personal pronouns ("I", "I've", "my", etc.) in intro/conclusion paragraphs
- This is AI-generated content - readers should know it's from the bot, not personally written
- In article summaries, maintain third-person perspective or neutral voice

Article Summary Guidelines (CRITICAL):
- Each summary must be ~200 tokens (approximately 150 words)
- Use the RSS excerpt as your foundation - it's already a good summary
- Expand on the excerpt with your perspective and context
- Highlight key takeaways or insights
- Explain why it's interesting or valuable
- Always include the source link
- Maintain consistent voice across all summaries
- Personalize the content - make it sound like you're recommending these articles to a friend

Newsletter Format:
- Do NOT include the main newsletter title in the HTML (WordPress displays it separately)
- Start with a brief introduction paragraph (150-200 words)
- Then present all 20 articles as numbered items
HTML Structure:
- Do NOT include <h1> or the main title - WordPress adds this automatically
- Start with an <h2> header that says "From MyNewsRobot:" to identify AI-generated content
- Follow with an introductory <p> paragraph (150-200 words, no personal pronouns)
- Use <ol> for the numbered list of articles
- Use <h3> for individual article titles within the list
- Use <p> for article summaries
- Use <a href="..."> for links
- End with a conclusion paragraph (no personal pronouns)
- Clean, semantic HTML only - no wrapper divs or containers
- Use <a href="..."> for links
- Clean, semantic HTML only - no wrapper divs or containers

✍️ After writing the newsletter, provide ONLY the HTML content (no title, just intro + articles + conclusion).
"""


class ContentWritingAgent:
    """Factory class for creating the ContentWritingAgent."""

    @staticmethod
    def create_agent() -> Agent:
        """
        Create and configure the ContentWritingAgent.

        Returns:
            Configured Agent instance with instructions
        """
        # Create the agent with ADK (no tools needed - pure writing)
        agent = Agent(
            name=AGENT_NAME,
            model=AGENT_MODEL,
            description=AGENT_DESCRIPTION,
            instruction=AGENT_INSTRUCTION,
            tools=[],  # No tools - uses LLM generation only
            output_key=AGENT_OUTPUT_KEY,  # Limit context passed to next agent
        )

        logger.info(f"Created {AGENT_NAME} with model {AGENT_MODEL}")
        return agent

    @staticmethod
    def get_writing_style() -> Dict[str, Any]:
        """
        Get writing style configuration.

        Returns:
            Writing style guidelines
        """
        return config_loader.get_writing_style()

    @staticmethod
    def get_newsletter_date() -> str:
        """
        Get formatted newsletter date.

        Returns:
            Formatted date string (e.g., "November 30th, 2025")
        """
        return format_newsletter_date()
