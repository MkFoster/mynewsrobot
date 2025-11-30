"""
Integration tests for MyNewsRobot agents

Tests verify that agents are correctly configured with:
- Proper Agent instances from ADK
- Correct model assignments
- Appropriate tools attached
- Valid instruction prompts
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from google.adk.agents.llm_agent import Agent

from src.agents import (
    NewsResearchAgent,
    ContentExtractionAgent,
    ContentAnalysisAgent,
    ContentWritingAgent,
    PublishingAgent,
)
from src.tools import WebScraperTool, BookmarkLoaderTool, WordPressTool


class TestNewsResearchAgent:
    """Tests for NewsResearchAgent configuration and functionality."""

    def test_create_agent_returns_agent_instance(self):
        """Test that create_agent returns an ADK Agent instance."""
        agent = NewsResearchAgent.create_agent()
        assert isinstance(agent, Agent)

    def test_agent_has_correct_name(self):
        """Test agent has the correct name."""
        agent = NewsResearchAgent.create_agent()
        assert agent.name == "NewsResearchAgent"

    def test_agent_has_correct_model(self):
        """Test agent uses gemini-2.0-flash-exp model."""
        agent = NewsResearchAgent.create_agent()
        assert agent.model == "gemini-2.0-flash-exp"

    def test_agent_has_description(self):
        """Test agent has a description."""
        agent = NewsResearchAgent.create_agent()
        assert agent.description is not None
        assert len(agent.description) > 0

    def test_agent_has_instruction(self):
        """Test agent has instruction prompt."""
        agent = NewsResearchAgent.create_agent()
        assert agent.instruction is not None
        assert len(agent.instruction) > 0
        assert "news research agent" in agent.instruction.lower()

    def test_agent_has_web_scraper_tool(self):
        """Test agent has WebScraperTool attached."""
        agent = NewsResearchAgent.create_agent()
        assert agent.tools is not None
        tool_types = [type(tool).__name__ for tool in agent.tools]
        assert "WebScraperTool" in tool_types

    def test_agent_has_bookmark_loader_tool(self):
        """Test agent has BookmarkLoaderTool attached."""
        agent = NewsResearchAgent.create_agent()
        assert agent.tools is not None
        tool_types = [type(tool).__name__ for tool in agent.tools]
        assert "BookmarkLoaderTool" in tool_types

    def test_get_news_sources_returns_list(self):
        """Test get_news_sources returns a list."""
        sources = NewsResearchAgent.get_news_sources()
        assert isinstance(sources, list)

    def test_is_processed_returns_boolean(self):
        """Test is_processed returns a boolean."""
        result = NewsResearchAgent.is_processed("https://example.com/article")
        assert isinstance(result, bool)

    def test_mark_as_processed_accepts_list(self):
        """Test mark_as_processed accepts a list of URLs."""
        urls = ["https://example.com/article1", "https://example.com/article2"]
        # Should not raise an exception
        NewsResearchAgent.mark_as_processed(urls)


class TestContentExtractionAgent:
    """Tests for ContentExtractionAgent configuration and functionality."""

    def test_create_agent_returns_agent_instance(self):
        """Test that create_agent returns an ADK Agent instance."""
        agent = ContentExtractionAgent.create_agent()
        assert isinstance(agent, Agent)

    def test_agent_has_correct_name(self):
        """Test agent has the correct name."""
        agent = ContentExtractionAgent.create_agent()
        assert agent.name == "ContentExtractionAgent"

    def test_agent_has_correct_model(self):
        """Test agent uses gemini-2.0-flash-exp model."""
        agent = ContentExtractionAgent.create_agent()
        assert agent.model == "gemini-2.0-flash-exp"

    def test_agent_has_description(self):
        """Test agent has a description."""
        agent = ContentExtractionAgent.create_agent()
        assert agent.description is not None
        assert len(agent.description) > 0

    def test_agent_has_instruction(self):
        """Test agent has instruction prompt."""
        agent = ContentExtractionAgent.create_agent()
        assert agent.instruction is not None
        assert len(agent.instruction) > 0
        assert "content extraction" in agent.instruction.lower()

    def test_agent_has_web_scraper_tool(self):
        """Test agent has WebScraperTool attached."""
        agent = ContentExtractionAgent.create_agent()
        assert agent.tools is not None
        tool_types = [type(tool).__name__ for tool in agent.tools]
        assert "WebScraperTool" in tool_types

    def test_agent_has_one_tool(self):
        """Test agent has exactly one tool (WebScraperTool)."""
        agent = ContentExtractionAgent.create_agent()
        assert agent.tools is not None
        assert len(agent.tools) == 1


class TestContentAnalysisAgent:
    """Tests for ContentAnalysisAgent configuration and functionality."""

    def test_create_agent_returns_agent_instance(self):
        """Test that create_agent returns an ADK Agent instance."""
        agent = ContentAnalysisAgent.create_agent()
        assert isinstance(agent, Agent)

    def test_agent_has_correct_name(self):
        """Test agent has the correct name."""
        agent = ContentAnalysisAgent.create_agent()
        assert agent.name == "ContentAnalysisAgent"

    def test_agent_has_correct_model(self):
        """Test agent uses gemini-2.0-flash-exp model."""
        agent = ContentAnalysisAgent.create_agent()
        assert agent.model == "gemini-2.0-flash-exp"

    def test_agent_has_description(self):
        """Test agent has a description."""
        agent = ContentAnalysisAgent.create_agent()
        assert agent.description is not None
        assert len(agent.description) > 0

    def test_agent_has_instruction(self):
        """Test agent has instruction prompt."""
        agent = ContentAnalysisAgent.create_agent()
        assert agent.instruction is not None
        assert len(agent.instruction) > 0
        assert "content analysis" in agent.instruction.lower()

    def test_agent_has_no_tools(self):
        """Test agent has no tools (pure LLM analysis)."""
        agent = ContentAnalysisAgent.create_agent()
        # ADK agents may have empty list or None for no tools
        assert agent.tools is None or len(agent.tools) == 0

    def test_get_topic_priorities_returns_dict(self):
        """Test get_topic_priorities returns a dictionary."""
        priorities = ContentAnalysisAgent.get_topic_priorities()
        assert isinstance(priorities, dict)

    def test_instruction_mentions_priority_scale(self):
        """Test instruction mentions the 7-11 priority scale."""
        agent = ContentAnalysisAgent.create_agent()
        instruction = agent.instruction.lower()
        assert "priority" in instruction
        # Should mention the scale or range
        assert "7" in agent.instruction or "11" in agent.instruction


class TestContentWritingAgent:
    """Tests for ContentWritingAgent configuration and functionality."""

    def test_create_agent_returns_agent_instance(self):
        """Test that create_agent returns an ADK Agent instance."""
        agent = ContentWritingAgent.create_agent()
        assert isinstance(agent, Agent)

    def test_agent_has_correct_name(self):
        """Test agent has the correct name."""
        agent = ContentWritingAgent.create_agent()
        assert agent.name == "ContentWritingAgent"

    def test_agent_has_correct_model(self):
        """Test agent uses gemini-2.0-flash-exp model."""
        agent = ContentWritingAgent.create_agent()
        assert agent.model == "gemini-2.0-flash-exp"

    def test_agent_has_description(self):
        """Test agent has a description."""
        agent = ContentWritingAgent.create_agent()
        assert agent.description is not None
        assert len(agent.description) > 0

    def test_agent_has_instruction(self):
        """Test agent has instruction prompt."""
        agent = ContentWritingAgent.create_agent()
        assert agent.instruction is not None
        assert len(agent.instruction) > 0
        assert "content writing" in agent.instruction.lower()

    def test_agent_has_no_tools(self):
        """Test agent has no tools (pure generation)."""
        agent = ContentWritingAgent.create_agent()
        # ADK agents may have empty list or None for no tools
        assert agent.tools is None or len(agent.tools) == 0

    def test_get_writing_style_returns_dict(self):
        """Test get_writing_style returns a dictionary."""
        style = ContentWritingAgent.get_writing_style()
        assert isinstance(style, dict)

    def test_get_newsletter_date_returns_string(self):
        """Test get_newsletter_date returns a string."""
        date = ContentWritingAgent.get_newsletter_date()
        assert isinstance(date, str)
        assert len(date) > 0

    def test_instruction_mentions_token_limit(self):
        """Test instruction mentions ~200 token limit."""
        agent = ContentWritingAgent.create_agent()
        instruction = agent.instruction.lower()
        assert "200" in agent.instruction or "token" in instruction


class TestPublishingAgent:
    """Tests for PublishingAgent configuration and functionality."""

    @patch("src.agents.publishing_agent.config_loader")
    def test_create_agent_returns_agent_instance(self, mock_config):
        """Test that create_agent returns an ADK Agent instance."""
        # Mock configuration
        mock_config.get_wordpress_config.return_value = {
            "wordpress": {
                "site_url": "https://example.com",
                "api_endpoint": "/wp-json/wp/v2",
            }
        }
        mock_config.get_env.return_value = "test_value"

        agent = PublishingAgent.create_agent()
        assert isinstance(agent, Agent)

    @patch("src.agents.publishing_agent.config_loader")
    def test_agent_has_correct_name(self, mock_config):
        """Test agent has the correct name."""
        mock_config.get_wordpress_config.return_value = {
            "wordpress": {
                "site_url": "https://example.com",
                "api_endpoint": "/wp-json/wp/v2",
            }
        }
        mock_config.get_env.return_value = "test_value"

        agent = PublishingAgent.create_agent()
        assert agent.name == "PublishingAgent"

    @patch("src.agents.publishing_agent.config_loader")
    def test_agent_has_correct_model(self, mock_config):
        """Test agent uses gemini-2.0-flash-exp model."""
        mock_config.get_wordpress_config.return_value = {
            "wordpress": {
                "site_url": "https://example.com",
                "api_endpoint": "/wp-json/wp/v2",
            }
        }
        mock_config.get_env.return_value = "test_value"

        agent = PublishingAgent.create_agent()
        assert agent.model == "gemini-2.0-flash-exp"

    @patch("src.agents.publishing_agent.config_loader")
    def test_agent_has_description(self, mock_config):
        """Test agent has a description."""
        mock_config.get_wordpress_config.return_value = {
            "wordpress": {
                "site_url": "https://example.com",
                "api_endpoint": "/wp-json/wp/v2",
            }
        }
        mock_config.get_env.return_value = "test_value"

        agent = PublishingAgent.create_agent()
        assert agent.description is not None
        assert len(agent.description) > 0

    @patch("src.agents.publishing_agent.config_loader")
    def test_agent_has_instruction(self, mock_config):
        """Test agent has instruction prompt."""
        mock_config.get_wordpress_config.return_value = {
            "wordpress": {
                "site_url": "https://example.com",
                "api_endpoint": "/wp-json/wp/v2",
            }
        }
        mock_config.get_env.return_value = "test_value"

        agent = PublishingAgent.create_agent()
        assert agent.instruction is not None
        assert len(agent.instruction) > 0
        assert "publishing" in agent.instruction.lower()

    @patch("src.agents.publishing_agent.config_loader")
    def test_agent_has_wordpress_tool(self, mock_config):
        """Test agent has WordPressTool attached."""
        mock_config.get_wordpress_config.return_value = {
            "wordpress": {
                "site_url": "https://example.com",
                "api_endpoint": "/wp-json/wp/v2",
            }
        }
        mock_config.get_env.return_value = "test_value"

        agent = PublishingAgent.create_agent()
        assert agent.tools is not None
        tool_types = [type(tool).__name__ for tool in agent.tools]
        assert "WordPressTool" in tool_types

    @patch("src.agents.publishing_agent.config_loader")
    def test_agent_has_one_tool(self, mock_config):
        """Test agent has exactly one tool (WordPressTool)."""
        mock_config.get_wordpress_config.return_value = {
            "wordpress": {
                "site_url": "https://example.com",
                "api_endpoint": "/wp-json/wp/v2",
            }
        }
        mock_config.get_env.return_value = "test_value"

        agent = PublishingAgent.create_agent()
        assert agent.tools is not None
        assert len(agent.tools) == 1

    def test_get_wordpress_config_returns_dict(self):
        """Test get_wordpress_config returns a dictionary."""
        config = PublishingAgent.get_wordpress_config()
        assert isinstance(config, dict)

    @patch("src.agents.publishing_agent.config_loader")
    def test_instruction_mentions_private_status(self, mock_config):
        """Test instruction mentions private post status."""
        mock_config.get_wordpress_config.return_value = {
            "wordpress": {
                "site_url": "https://example.com",
                "api_endpoint": "/wp-json/wp/v2",
            }
        }
        mock_config.get_env.return_value = "test_value"

        agent = PublishingAgent.create_agent()
        instruction = agent.instruction.lower()
        assert "private" in instruction

    @patch("src.agents.publishing_agent.config_loader")
    def test_instruction_mentions_weekly_summary_category(self, mock_config):
        """Test instruction mentions WeeklySummary category."""
        mock_config.get_wordpress_config.return_value = {
            "wordpress": {
                "site_url": "https://example.com",
                "api_endpoint": "/wp-json/wp/v2",
            }
        }
        mock_config.get_env.return_value = "test_value"

        agent = PublishingAgent.create_agent()
        assert "WeeklySummary" in agent.instruction or "weekly" in agent.instruction.lower()


class TestAgentIntegration:
    """Integration tests across all agents."""

    @patch("src.agents.publishing_agent.config_loader")
    def test_all_agents_use_same_model(self, mock_config):
        """Test all agents use the same model."""
        mock_config.get_wordpress_config.return_value = {
            "wordpress": {
                "site_url": "https://example.com",
                "api_endpoint": "/wp-json/wp/v2",
            }
        }
        mock_config.get_env.return_value = "test_value"

        agents = [
            NewsResearchAgent.create_agent(),
            ContentExtractionAgent.create_agent(),
            ContentAnalysisAgent.create_agent(),
            ContentWritingAgent.create_agent(),
            PublishingAgent.create_agent(),
        ]

        models = [agent.model for agent in agents]
        assert all(model == "gemini-2.0-flash-exp" for model in models)

    @patch("src.agents.publishing_agent.config_loader")
    def test_all_agents_have_unique_names(self, mock_config):
        """Test all agents have unique names."""
        mock_config.get_wordpress_config.return_value = {
            "wordpress": {
                "site_url": "https://example.com",
                "api_endpoint": "/wp-json/wp/v2",
            }
        }
        mock_config.get_env.return_value = "test_value"

        agents = [
            NewsResearchAgent.create_agent(),
            ContentExtractionAgent.create_agent(),
            ContentAnalysisAgent.create_agent(),
            ContentWritingAgent.create_agent(),
            PublishingAgent.create_agent(),
        ]

        names = [agent.name for agent in agents]
        assert len(names) == len(set(names))  # All names are unique

    @patch("src.agents.publishing_agent.config_loader")
    def test_all_agents_have_descriptions(self, mock_config):
        """Test all agents have non-empty descriptions."""
        mock_config.get_wordpress_config.return_value = {
            "wordpress": {
                "site_url": "https://example.com",
                "api_endpoint": "/wp-json/wp/v2",
            }
        }
        mock_config.get_env.return_value = "test_value"

        agents = [
            NewsResearchAgent.create_agent(),
            ContentExtractionAgent.create_agent(),
            ContentAnalysisAgent.create_agent(),
            ContentWritingAgent.create_agent(),
            PublishingAgent.create_agent(),
        ]

        for agent in agents:
            assert agent.description is not None
            assert len(agent.description) > 0

    @patch("src.agents.publishing_agent.config_loader")
    def test_all_agents_have_instructions(self, mock_config):
        """Test all agents have non-empty instructions."""
        mock_config.get_wordpress_config.return_value = {
            "wordpress": {
                "site_url": "https://example.com",
                "api_endpoint": "/wp-json/wp/v2",
            }
        }
        mock_config.get_env.return_value = "test_value"

        agents = [
            NewsResearchAgent.create_agent(),
            ContentExtractionAgent.create_agent(),
            ContentAnalysisAgent.create_agent(),
            ContentWritingAgent.create_agent(),
            PublishingAgent.create_agent(),
        ]

        for agent in agents:
            assert agent.instruction is not None
            assert len(agent.instruction) > 0

    def test_tool_usage_across_agents(self):
        """Test that tools are correctly distributed across agents."""
        # NewsResearchAgent should have 2 tools
        news_agent = NewsResearchAgent.create_agent()
        assert len(news_agent.tools) == 2

        # ContentExtractionAgent should have 1 tool
        extraction_agent = ContentExtractionAgent.create_agent()
        assert len(extraction_agent.tools) == 1

        # ContentAnalysisAgent should have 0 tools
        analysis_agent = ContentAnalysisAgent.create_agent()
        assert analysis_agent.tools is None or len(analysis_agent.tools) == 0

        # ContentWritingAgent should have 0 tools
        writing_agent = ContentWritingAgent.create_agent()
        assert writing_agent.tools is None or len(writing_agent.tools) == 0
