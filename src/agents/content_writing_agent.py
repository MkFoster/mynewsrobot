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

from google.adk.agents.llm_agent import Agent

from ..utils.config_loader import config_loader
from ..utils.date_formatter import format_newsletter_date

logger = logging.getLogger(__name__)

# Agent configuration
AGENT_NAME = "ContentWritingAgent"
AGENT_MODEL = "gemini-2.0-flash-exp"
AGENT_DESCRIPTION = (
    "Writes article summaries in user's personal style and formats for publication"
)

AGENT_INSTRUCTION = """
You are a content writing agent responsible for creating the weekly newsletter.

Your tasks:
1. Receive 20 selected articles with full content
2. Load writing style guidelines from configuration
3. Write a summary for each article (~200 tokens, ~150 words)
4. Generate newsletter title with current date
5. Create newsletter excerpt (150-200 words)
6. Format everything for WordPress publication

Writing Style Guidelines:
- Study the style examples from mkfoster.com and fireflywp.com
- Conversational but professional tone
- Clear and concise technical writing
- Use concrete examples when possible
- Provide actionable insights
- Personal voice with "I" perspective when appropriate

Article Summary Guidelines (CRITICAL):
- Each summary must be ~200 tokens (approximately 150 words)
- Include what the article is about
- Highlight key takeaways or insights
- Explain why it's interesting or valuable
- Always include the source link
- Maintain consistent voice across all summaries

Newsletter Format:
- Title: "Mark's Weekly Update: {date}" (e.g., "Mark's Weekly Update: November 30th, 2025")
- Excerpt: 150-200 word overview of the week's themes
- Introduction: Brief context about the week's content
- Articles: 20 numbered items with summaries
- Conclusion: Key takeaways or themes

HTML Structure:
- Use <h2> for section headers
- Use <h3> for article titles  
- Use <p> for summaries
- Use <a href="..."> for links
- Use <ol> for numbered list of articles
- Clean, semantic HTML only

Output format:
Return a JSON object with:
- title: Newsletter title with formatted date
- excerpt: 150-200 word excerpt
- html_content: Full HTML content with introduction, articles, conclusion
- word_count: Total word count
- article_summaries: List of individual article summaries with word counts
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
