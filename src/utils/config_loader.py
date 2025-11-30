"""
Configuration loader for MyNewsRobot

Handles loading YAML configuration files and environment variables.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class ConfigLoader:
    """Load and manage configuration from YAML files and environment variables."""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the configuration loader.

        Args:
            config_dir: Path to configuration directory. Defaults to ./config
        """
        # Load environment variables
        load_dotenv()

        # Set config directory
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "config"
        self.config_dir = Path(config_dir)

        # Cache for loaded configs
        self._cache: Dict[str, Any] = {}

    def load_yaml(self, filename: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load a YAML configuration file.

        Args:
            filename: Name of the YAML file (e.g., 'news_sources.yaml')
            use_cache: Whether to use cached version if available

        Returns:
            Parsed YAML content as dictionary

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        if use_cache and filename in self._cache:
            return self._cache[filename]

        file_path = self.config_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if use_cache:
            self._cache[filename] = config

        return config

    def get_news_sources(self) -> Dict[str, Any]:
        """Load news sources configuration."""
        env_path = os.getenv("NEWS_SOURCES_CONFIG")
        filename = env_path if env_path else "news_sources.yaml"
        return self.load_yaml(filename)

    def get_topic_priorities(self) -> Dict[str, Any]:
        """Load topic priorities configuration."""
        env_path = os.getenv("TOPIC_PRIORITIES_CONFIG")
        filename = env_path if env_path else "topic_priorities.yaml"
        return self.load_yaml(filename)

    def get_weekly_bookmarks(self) -> Dict[str, Any]:
        """Load weekly bookmarks configuration."""
        env_path = os.getenv("BOOKMARK_CONFIG_PATH")
        if env_path:
            # Handle GCS paths or custom paths
            filename = env_path
        else:
            filename = "weekly_bookmarks.yaml"

        try:
            return self.load_yaml(filename, use_cache=False)  # Don't cache bookmarks
        except FileNotFoundError:
            # Return empty bookmarks if file doesn't exist
            return {"bookmarks": []}

    def get_wordpress_config(self) -> Dict[str, Any]:
        """Load WordPress configuration."""
        config = self.load_yaml("wordpress.yaml")

        # Override with environment variables if present
        if os.getenv("WORDPRESS_USERNAME"):
            config.setdefault("wordpress", {})
            config["wordpress"]["username"] = os.getenv("WORDPRESS_USERNAME")

        if os.getenv("WORDPRESS_APP_PASSWORD"):
            config.setdefault("wordpress", {})
            config["wordpress"]["app_password"] = os.getenv("WORDPRESS_APP_PASSWORD")

        return config

    def get_writing_style(self) -> Dict[str, Any]:
        """Load writing style configuration."""
        return self.load_yaml("writing_style.yaml")

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable value.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)

    def get_google_ai_config(self) -> Dict[str, str]:
        """Get Google AI Studio configuration from environment."""
        api_key = self.get_env("GOOGLE_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment. "
                "Get your API key from https://aistudio.google.com/apikey"
            )
        return {
            "api_key": api_key,
            "project": self.get_env("GOOGLE_CLOUD_PROJECT", ""),
            "location": self.get_env("GOOGLE_CLOUD_LOCATION", "us-central1"),
        }

    def get_google_cloud_config(self) -> Dict[str, str]:
        """Get Google Cloud configuration (legacy, use get_google_ai_config instead)."""
        return self.get_google_ai_config()

    def reload(self) -> None:
        """Clear cache and reload environment variables."""
        self._cache.clear()
        load_dotenv(override=True)


# Global config loader instance
config_loader = ConfigLoader()
