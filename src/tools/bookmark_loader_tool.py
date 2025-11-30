"""
BookmarkLoaderTool - Load weekly user bookmarks from configuration

Supports loading from local YAML files or Google Cloud Storage.
Bookmarks always get highest priority (11) in article selection.
"""

import logging
from typing import Any, Dict, List

import yaml
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)


class BookmarkLoaderTool(BaseTool):
    """Custom tool to load weekly bookmarks from configuration."""

    def __init__(self, config_path: str = "config/weekly_bookmarks.yaml"):
        """
        Initialize bookmark loader.

        Args:
            config_path: Path to bookmarks YAML file (local or GCS path)
        """
        super().__init__(
            name="bookmark_loader",
            description=(
                "Loads weekly user bookmarks from configuration file. "
                "Supports local files and Google Cloud Storage paths."
            ),
        )
        self.config_path = config_path

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Run the tool asynchronously (required by ADK)."""
        return self.run(refresh=args.get("refresh", False))

    def run(self, refresh: bool = False) -> Dict[str, Any]:
        """
        Load bookmarks from configuration.

        Args:
            refresh: Force reload from source (ignore cache)

        Returns:
            Dictionary containing:
            - success: bool
            - bookmarks: List[Dict] with url, note, submitted_date
            - count: int
            - source: str (file path)
            - error: Optional[str]
        """
        logger.info(f"Loading bookmarks from: {self.config_path}")

        try:
            # Check if GCS path
            if self.config_path.startswith("gs://"):
                return self._load_from_gcs(self.config_path)
            else:
                return self._load_from_local(self.config_path)

        except FileNotFoundError:
            logger.warning(f"Bookmark file not found: {self.config_path}")
            return {
                "success": True,
                "bookmarks": [],
                "count": 0,
                "source": self.config_path,
                "warning": "Bookmark file not found, returning empty list",
            }
        except Exception as e:
            logger.error(f"Error loading bookmarks: {e}", exc_info=True)
            return {
                "success": False,
                "bookmarks": [],
                "count": 0,
                "source": self.config_path,
                "error": str(e),
            }

    def _load_from_local(self, file_path: str) -> Dict[str, Any]:
        """
        Load bookmarks from local YAML file.

        Args:
            file_path: Local file path

        Returns:
            Bookmark data
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        bookmarks = data.get("bookmarks") or []

        # Validate bookmark structure
        validated_bookmarks = []
        for bookmark in bookmarks:
            if not isinstance(bookmark, dict):
                logger.warning(f"Invalid bookmark format: {bookmark}")
                continue

            if "url" not in bookmark:
                logger.warning(f"Bookmark missing URL: {bookmark}")
                continue

            validated_bookmarks.append(
                {
                    "url": bookmark["url"],
                    "note": bookmark.get("note", ""),
                    "submitted_date": bookmark.get("submitted_date", ""),
                    "priority": 11,  # Always highest priority
                }
            )

        logger.info(f"Loaded {len(validated_bookmarks)} bookmarks from local file")

        return {
            "success": True,
            "bookmarks": validated_bookmarks,
            "count": len(validated_bookmarks),
            "source": file_path,
        }

    def _load_from_gcs(self, gcs_path: str) -> Dict[str, Any]:
        """
        Load bookmarks from Google Cloud Storage.

        Args:
            gcs_path: GCS path (gs://bucket/path/file.yaml)

        Returns:
            Bookmark data
        """
        try:
            from google.cloud import storage
        except ImportError:
            raise ImportError(
                "google-cloud-storage is required for GCS support. "
                "Install with: pip install google-cloud-storage"
            )

        # Parse GCS path
        if not gcs_path.startswith("gs://"):
            raise ValueError(f"Invalid GCS path: {gcs_path}")

        path_parts = gcs_path[5:].split("/", 1)
        bucket_name = path_parts[0]
        blob_path = path_parts[1] if len(path_parts) > 1 else ""

        # Download from GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)

        content = blob.download_as_text()
        data = yaml.safe_load(content)

        bookmarks = data.get("bookmarks") or []

        # Validate bookmark structure
        validated_bookmarks = []
        for bookmark in bookmarks:
            if not isinstance(bookmark, dict) or "url" not in bookmark:
                continue

            validated_bookmarks.append(
                {
                    "url": bookmark["url"],
                    "note": bookmark.get("note", ""),
                    "submitted_date": bookmark.get("submitted_date", ""),
                    "priority": 11,  # Always highest priority
                }
            )

        logger.info(f"Loaded {len(validated_bookmarks)} bookmarks from GCS")

        return {
            "success": True,
            "bookmarks": validated_bookmarks,
            "count": len(validated_bookmarks),
            "source": gcs_path,
        }
