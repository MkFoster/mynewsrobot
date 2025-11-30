"""
WordPressTool - Publish content to WordPress via REST API

Posts weekly summaries to WordPress with proper formatting, categories,
and status. Supports application password authentication.
"""

import base64
import logging
from typing import Any, Dict, List, Optional

import requests
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)


class WordPressTool(BaseTool):
    """Custom tool to publish content to WordPress via REST API."""

    def __init__(
        self,
        site_url: str,
        username: str,
        app_password: str,
        api_endpoint: str = "/wp-json/wp/v2",
    ):
        """
        Initialize WordPress tool.

        Args:
            site_url: WordPress site URL (e.g., https://mkfoster.com)
            username: WordPress username
            app_password: WordPress application password
            api_endpoint: WordPress REST API endpoint path
        """
        super().__init__(
            name="wordpress_publisher",
            description=(
                "Publishes content to WordPress via REST API. "
                "Creates posts with specified status, categories, and content."
            ),
        )
        self.site_url = site_url.rstrip("/")
        self.api_endpoint = api_endpoint
        self.username = username
        self.app_password = app_password

        # Create session with authentication
        self.session = requests.Session()
        credentials = f"{username}:{app_password}"
        token = base64.b64encode(credentials.encode()).decode()
        self.session.headers.update(
            {
                "Authorization": f"Basic {token}",
                "Content-Type": "application/json",
                "User-Agent": "MyNewsRobot/1.0",
            }
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Dict[str, Any]:
        """Run the tool asynchronously (required by ADK)."""
        return self.run(
            title=args["title"],
            content=args["content"],
            status=args.get("status", "private"),
            categories=args.get("categories"),
            excerpt=args.get("excerpt"),
            featured_media_id=args.get("featured_media_id"),
        )

    def run(
        self,
        title: str,
        content: str,
        status: str = "private",
        categories: Optional[List[str]] = None,
        excerpt: Optional[str] = None,
        featured_media_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a new WordPress post.

        Args:
            title: Post title
            content: Post content (HTML allowed)
            status: Post status ('draft', 'private', 'publish')
            categories: List of category names
            excerpt: Post excerpt
            featured_media_id: Featured image media ID

        Returns:
            Dictionary containing:
            - success: bool
            - post_id: Optional[int]
            - post_url: Optional[str]
            - edit_url: Optional[str]
            - error: Optional[str]
        """
        logger.info(f"Creating WordPress post: {title}")

        try:
            # Get category IDs
            category_ids = []
            if categories:
                category_ids = self._get_or_create_categories(categories)

            # Prepare post data
            post_data = {
                "title": title,
                "content": content,
                "status": status,
                "categories": category_ids,
            }

            if excerpt:
                post_data["excerpt"] = excerpt

            if featured_media_id:
                post_data["featured_media"] = featured_media_id

            # Create post
            url = f"{self.site_url}{self.api_endpoint}/posts"
            response = self.session.post(url, json=post_data, timeout=30)
            response.raise_for_status()

            post = response.json()
            post_id = post["id"]
            post_url = post["link"]
            edit_url = f"{self.site_url}/wp-admin/post.php?post={post_id}&action=edit"

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

    def update_post(
        self,
        post_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        status: Optional[str] = None,
        featured_media_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing WordPress post.

        Args:
            post_id: Post ID to update
            title: New title (optional)
            content: New content (optional)
            status: New status (optional)
            featured_media_id: Featured image media ID (optional)

        Returns:
            Update result
        """
        logger.info(f"Updating WordPress post {post_id}")

        try:
            # Prepare update data
            update_data = {}
            if title:
                update_data["title"] = title
            if content:
                update_data["content"] = content
            if status:
                update_data["status"] = status
            if featured_media_id:
                update_data["featured_media"] = featured_media_id

            # Update post
            url = f"{self.site_url}{self.api_endpoint}/posts/{post_id}"
            response = self.session.post(url, json=update_data, timeout=30)
            response.raise_for_status()

            post = response.json()

            logger.info(f"Successfully updated post {post_id}")

            return {
                "success": True,
                "post_id": post_id,
                "post_url": post["link"],
            }

        except Exception as e:
            logger.error(f"Error updating post: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    def _get_or_create_categories(self, category_names: List[str]) -> List[int]:
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
            url = f"{self.site_url}{self.api_endpoint}/categories"
            response = self.session.get(
                url, params={"search": name, "per_page": 1}, timeout=10
            )

            if response.ok:
                categories = response.json()
                if categories and categories[0]["name"].lower() == name.lower():
                    category_ids.append(categories[0]["id"])
                    continue

            # Category doesn't exist, create it
            try:
                response = self.session.post(
                    url, json={"name": name}, timeout=10
                )
                if response.ok:
                    category = response.json()
                    category_ids.append(category["id"])
                    logger.info(f"Created new category: {name} (ID: {category['id']})")
            except Exception as e:
                logger.warning(f"Failed to create category {name}: {e}")

        return category_ids

    def upload_media(
        self, file_path: str, title: Optional[str] = None, alt_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload media file to WordPress.

        Args:
            file_path: Path to media file
            title: Media title
            alt_text: Alt text for images

        Returns:
            Upload result with media ID
        """
        logger.info(f"Uploading media: {file_path}")

        try:
            import os
            from mimetypes import guess_type

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Guess MIME type
            mime_type, _ = guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"

            # Read file
            with open(file_path, "rb") as f:
                file_data = f.read()

            # Prepare headers
            headers = {
                "Authorization": self.session.headers["Authorization"],
                "Content-Type": mime_type,
                "Content-Disposition": f'attachment; filename="{os.path.basename(file_path)}"',
            }

            # Upload
            url = f"{self.site_url}{self.api_endpoint}/media"
            response = requests.post(url, headers=headers, data=file_data, timeout=60)
            response.raise_for_status()

            media = response.json()
            media_id = media["id"]

            # Update title and alt text if provided
            if title or alt_text:
                update_data = {}
                if title:
                    update_data["title"] = title
                if alt_text:
                    update_data["alt_text"] = alt_text

                self.session.post(
                    f"{url}/{media_id}", json=update_data, timeout=10
                )

            logger.info(f"Successfully uploaded media {media_id}")

            return {
                "success": True,
                "media_id": media_id,
                "url": media["source_url"],
            }

        except Exception as e:
            logger.error(f"Error uploading media: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    def close(self):
        """Clean up resources."""
        if self.session:
            self.session.close()
