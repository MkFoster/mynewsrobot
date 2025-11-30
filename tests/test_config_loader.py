"""
Test configuration loader
"""

import pytest
from pathlib import Path
from src.utils.config_loader import ConfigLoader


def test_config_loader_initialization():
    """Test that config loader initializes correctly."""
    loader = ConfigLoader()
    assert loader.config_dir.exists()
    assert loader._cache == {}


def test_load_news_sources():
    """Test loading news sources configuration."""
    loader = ConfigLoader()
    sources = loader.get_news_sources()
    assert "news_sources" in sources
    assert isinstance(sources["news_sources"], dict)


def test_load_topic_priorities():
    """Test loading topic priorities configuration."""
    loader = ConfigLoader()
    topics = loader.get_topic_priorities()
    assert "topics" in topics
    assert isinstance(topics["topics"], list)
    # Check that topics have required fields
    if topics["topics"]:
        first_topic = topics["topics"][0]
        assert "name" in first_topic
        assert "keywords" in first_topic
        assert "priority" in first_topic


def test_get_google_ai_config():
    """Test getting Google AI Studio configuration."""
    import os
    # Set a test API key if not already set
    if not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = "test-api-key"
    
    loader = ConfigLoader()
    config = loader.get_google_ai_config()
    assert "api_key" in config
    assert "project" in config
    assert "location" in config
