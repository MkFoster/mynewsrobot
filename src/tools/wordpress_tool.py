"""
WordPress publishing tool - Publish content to WordPress via REST API

Posts weekly summaries to WordPress with proper formatting, categories,
and status. Supports application password authentication.
"""

import base64
import logging
from typing import Any, Dict, List, Optional

import requests
from ..utils.config_loader import config_loader

logger = logging.getLogger(__name__)

# Initialize WordPress configuration
_wp_config = config_loader.get_wordpress_config()
_wp_settings = _wp_config.get("wordpress", {})
_site_url = _wp_settings.get("site_url", "https://mkfoster.com").rstrip("/")
_api_endpoint = _wp_settings.get("api_endpoint", "/wp-json/wp/v2")
_username = config_loader.get_env("WORDPRESS_USERNAME", "")
_app_password = config_loader.get_env("WORDPRESS_APP_PASSWORD", "").replace(" ", "")  # Remove spaces from app password

# Create session with authentication
_session = requests.Session()
_credentials = f"{_username}:{_app_password}"
_token = base64.b64encode(_credentials.encode()).decode()
_session.headers.update({
    "Authorization": f"Basic {_token}",
    "Content-Type": "application/json",
    "User-Agent": "MyNewsRobot/1.0",
})


def publish_to_wordpress(
    title: str,
    content: str,
    status: str,
    categories: List[str],
    excerpt: str,
) -> Dict[str, Any]:
    """
    Publish a post to WordPress via REST API.

    Creates a new WordPress post with the specified content, status, and categories.
    Posts can be 'private' (not publicly visible), 'draft', or 'publish'.

    Args:
        title: Post title
        content: Post HTML content
        status: Post status - 'private', 'draft', or 'publish'
        categories: List of category names to assign (e.g., ["WeeklySummary"])
        excerpt: Post excerpt/summary

    Returns:
        Dictionary containing:
        - success: bool indicating if publish succeeded
        - post_id: WordPress post ID
        - post_url: Public URL of the post
        - edit_url: WordPress admin edit URL
        - status: Post status
        - error: Error message if failed
    """
    logger.info(f"Creating WordPress post: {title}")

    try:
        # Get category IDs
        category_ids = []
        if categories:
            category_ids = _get_or_create_categories(categories)

        # Prepare post data
        post_data = {
            "title": title,
            "content": content,
            "status": status,
            "categories": category_ids,
        }

        if excerpt:
            post_data["excerpt"] = excerpt

        # Create post
        url = f"{_site_url}{_api_endpoint}/posts"
        response = _session.post(url, json=post_data, timeout=30)
        response.raise_for_status()

        post = response.json()
        post_id = post["id"]
        post_url = post["link"]
        edit_url = f"{_site_url}/wp-admin/post.php?post={post_id}&action=edit"

        logger.info(f"Successfully created post {post_id}: {post_url}")

        return {
            "success": True,
            "post_id": post_id,
            "post_url": post_url,
            "edit_url": edit_url,
            "status": status,
        }

    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error: {e.response.status_code}"
        try:
            error_data = e.response.json()
            error_msg += f" - {error_data.get('message', '')}"
        except Exception:
            pass
        logger.error(f"Failed to create post: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
        }

    except Exception as e:
        logger.error(f"Error creating post: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


def _get_or_create_categories(category_names: List[str]) -> List[int]:
        """
        Get category IDs, creating categories if they don't exist.

        Args:
            category_names: List of category names

        Returns:
            List of category IDs
        """
        category_ids = []

        for name in category_names:
            # Search for existing category
            url = f"{_site_url}{_api_endpoint}/categories"
            response = _session.get(
                url, params={"search": name, "per_page": 1}, timeout=10
            )

            if response.ok:
                categories = response.json()
                if categories and categories[0]["name"].lower() == name.lower():
                    category_ids.append(categories[0]["id"])
                    continue

            # Category doesn't exist, create it
            try:
                response = _session.post(
                    url, json={"name": name}, timeout=10
                )
                if response.ok:
                    category = response.json()
                    category_ids.append(category["id"])
                    logger.info(f"Created new category: {name} (ID: {category['id']})")
            except Exception as e:
                logger.warning(f"Failed to create category {name}: {e}")

        return category_ids
