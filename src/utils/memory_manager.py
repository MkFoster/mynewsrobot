"""
Memory management for MyNewsRobot using ADK InMemoryMemoryService
"""

from typing import List, Optional, Set
from datetime import datetime, timedelta

from google.adk.memory import InMemoryMemoryService


class MemoryManager:
    """Manage article memory to prevent duplicates across weeks."""

    def __init__(self, session_ttl_days: int = 7):
        """
        Initialize the memory manager.

        Args:
            session_ttl_days: Number of days to keep article URLs in memory
        """
        self.service = InMemoryMemoryService()
        self.session_ttl_days = session_ttl_days
        self._processed_urls: Set[str] = set()

    def add_processed_url(self, url: str) -> None:
        """
        Add a URL to the processed articles list.

        Args:
            url: Article URL to mark as processed
        """
        self._processed_urls.add(url.strip().lower())

    def is_processed(self, url: str) -> bool:
        """
        Check if a URL has been processed recently.

        Args:
            url: Article URL to check

        Returns:
            True if URL was processed within TTL period
        """
        return url.strip().lower() in self._processed_urls

    def get_unprocessed_urls(self, urls: List[str]) -> List[str]:
        """
        Filter out already processed URLs.

        Args:
            urls: List of URLs to filter

        Returns:
            List of URLs that haven't been processed
        """
        return [url for url in urls if not self.is_processed(url)]

    def clear_old_entries(self) -> int:
        """
        Clear entries older than TTL period.

        Returns:
            Number of entries cleared
        """
        # In production, this would check timestamps
        # For now, this is a placeholder for the basic implementation
        initial_count = len(self._processed_urls)
        # TODO: Implement timestamp-based cleanup
        return 0

    def get_processed_count(self) -> int:
        """
        Get count of processed URLs in memory.

        Returns:
            Number of processed URLs
        """
        return len(self._processed_urls)

    def save_state(self) -> dict:
        """
        Save current memory state.

        Returns:
            Dictionary containing memory state
        """
        return {
            "processed_urls": list(self._processed_urls),
            "timestamp": datetime.now().isoformat(),
            "ttl_days": self.session_ttl_days,
        }

    def load_state(self, state: dict) -> None:
        """
        Load memory state from dictionary.

        Args:
            state: Dictionary containing memory state
        """
        if "processed_urls" in state:
            self._processed_urls = set(state["processed_urls"])

        if "ttl_days" in state:
            self.session_ttl_days = state["ttl_days"]


# Global memory manager instance
memory_manager = MemoryManager()
