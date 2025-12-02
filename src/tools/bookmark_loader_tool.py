"""
Bookmark loader tool - Load weekly user bookmarks from configuration

Supports loading from local YAML files or Google Cloud Storage.
Bookmarks always get highest priority (11) in article selection.
"""

import logging
from typing import Any, Dict, List

import yaml

logger = logging.getLogger(__name__)


def load_user_bookmarks(
    config_path: str = "config/weekly_bookmarks.yaml",
    refresh: bool = False
) -> Dict[str, Any]:
    """
    Load weekly user bookmarks from configuration file.

    Loads bookmarks from config/weekly_bookmarks.yaml. Bookmarks are
    articles manually selected by the user for inclusion in the newsletter.
    They always get highest priority (11) in article selection.

    Args:
        config_path: Path to bookmarks YAML file (local or GCS path)
        refresh: Force reload from source (ignore cache)

    Returns:
        Dictionary containing:
        - success: bool indicating if load succeeded
        - bookmarks: List of bookmark dicts with url, note, submitted_date
        - count: Number of bookmarks loaded
        - source: File path of bookmark config
        - error: Error message if failed
    """
    logger.info(f"Loading bookmarks from: {config_path}")

    try:
        # Check if GCS path
        if config_path.startswith("gs://"):
            return _load_from_gcs(config_path)
        else:
            return _load_from_local(config_path)

    except FileNotFoundError:
        logger.warning(f"Bookmark file not found: {config_path}")
        return {
            "success": True,
            "bookmarks": [],
            "count": 0,
            "source": config_path,
            "warning": "Bookmark file not found, returning empty list",
        }
    except Exception as e:
        logger.error(f"Error loading bookmarks: {e}", exc_info=True)
        return {
            "success": False,
            "bookmarks": [],
            "count": 0,
            "source": config_path,
            "error": str(e),
        }


def _load_from_local(file_path: str) -> Dict[str, Any]:
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


def _load_from_gcs(gcs_path: str) -> Dict[str, Any]:
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
