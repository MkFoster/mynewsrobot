"""
Unit tests for WordPressTool
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.tools.wordpress_tool import WordPressTool


@pytest.fixture
def wp_tool():
    """Create a WordPressTool instance for testing."""
    return WordPressTool(
        site_url="https://mkfoster.com",
        username="testuser",
        app_password="test-app-password",
    )


def test_wordpress_tool_init(wp_tool):
    """Test WordPressTool initialization."""
    assert wp_tool.name == "wordpress_publisher"
    assert wp_tool.site_url == "https://mkfoster.com"
    assert wp_tool.username == "testuser"
    assert "Authorization" in wp_tool.session.headers


def test_init_strips_trailing_slash():
    """Test that site URL trailing slash is removed."""
    tool = WordPressTool(
        site_url="https://example.com/",
        username="user",
        app_password="pass",
    )
    assert tool.site_url == "https://example.com"


@patch("src.tools.wordpress_tool.requests.Session")
def test_run_create_post_success(mock_session_class, wp_tool):
    """Test successful post creation."""
    # Mock response
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "id": 123,
        "link": "https://mkfoster.com/test-post",
        "status": "private",
    }
    
    # Mock session
    wp_tool.session.post = Mock(return_value=mock_response)
    wp_tool._get_or_create_categories = Mock(return_value=[1, 2])
    
    result = wp_tool.run(
        title="Test Post",
        content="Test content",
        status="private",
        categories=["WeeklySummary"],
    )
    
    assert result["success"] is True
    assert result["post_id"] == 123
    assert result["post_url"] == "https://mkfoster.com/test-post"
    assert "edit_url" in result


def test_run_create_post_with_excerpt(wp_tool):
    """Test post creation with excerpt."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "id": 456,
        "link": "https://mkfoster.com/post-with-excerpt",
    }
    
    wp_tool.session.post = Mock(return_value=mock_response)
    wp_tool._get_or_create_categories = Mock(return_value=[])
    
    result = wp_tool.run(
        title="Test Post",
        content="Content",
        excerpt="Test excerpt",
    )
    
    # Verify excerpt was included in request
    call_kwargs = wp_tool.session.post.call_args[1]
    assert call_kwargs["json"]["excerpt"] == "Test excerpt"


def test_run_create_post_with_featured_image(wp_tool):
    """Test post creation with featured image."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "id": 789,
        "link": "https://mkfoster.com/post-with-image",
    }
    
    wp_tool.session.post = Mock(return_value=mock_response)
    wp_tool._get_or_create_categories = Mock(return_value=[])
    
    result = wp_tool.run(
        title="Test Post",
        content="Content",
        featured_media_id=99,
    )
    
    # Verify featured_media was included
    call_kwargs = wp_tool.session.post.call_args[1]
    assert call_kwargs["json"]["featured_media"] == 99


def test_run_create_post_http_error(wp_tool):
    """Test post creation with HTTP error."""
    import requests
    
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"message": "Authentication failed"}
    
    http_error = requests.exceptions.HTTPError()
    http_error.response = mock_response
    
    wp_tool.session.post = Mock(side_effect=http_error)
    wp_tool._get_or_create_categories = Mock(return_value=[])
    
    result = wp_tool.run(title="Test", content="Content")
    
    assert result["success"] is False
    assert "error" in result
    assert "401" in result["error"]


def test_run_create_post_generic_error(wp_tool):
    """Test post creation with generic error."""
    wp_tool.session.post = Mock(side_effect=Exception("Network error"))
    wp_tool._get_or_create_categories = Mock(return_value=[])
    
    result = wp_tool.run(title="Test", content="Content")
    
    assert result["success"] is False
    assert "Network error" in result["error"]


def test_update_post_success(wp_tool):
    """Test successful post update."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "id": 123,
        "link": "https://mkfoster.com/updated-post",
    }
    
    wp_tool.session.post = Mock(return_value=mock_response)
    
    result = wp_tool.update_post(
        post_id=123,
        title="Updated Title",
        content="Updated content",
    )
    
    assert result["success"] is True
    assert result["post_id"] == 123


def test_get_or_create_categories_existing(wp_tool):
    """Test getting existing category."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = [
        {"id": 5, "name": "WeeklySummary"}
    ]
    
    wp_tool.session.get = Mock(return_value=mock_response)
    
    category_ids = wp_tool._get_or_create_categories(["WeeklySummary"])
    
    assert category_ids == [5]


def test_get_or_create_categories_create_new(wp_tool):
    """Test creating new category."""
    # Mock GET response (not found)
    mock_get_response = Mock()
    mock_get_response.ok = True
    mock_get_response.json.return_value = []
    
    # Mock POST response (created)
    mock_post_response = Mock()
    mock_post_response.ok = True
    mock_post_response.json.return_value = {"id": 10, "name": "NewCategory"}
    
    wp_tool.session.get = Mock(return_value=mock_get_response)
    wp_tool.session.post = Mock(return_value=mock_post_response)
    
    category_ids = wp_tool._get_or_create_categories(["NewCategory"])
    
    assert category_ids == [10]


def test_get_or_create_categories_handles_errors(wp_tool):
    """Test category creation error handling."""
    # Mock GET to return empty (category not found)
    mock_get_response = Mock()
    mock_get_response.ok = True
    mock_get_response.json.return_value = []
    
    # Mock POST to fail
    wp_tool.session.get = Mock(return_value=mock_get_response)
    wp_tool.session.post = Mock(side_effect=Exception("API Error"))
    
    # Should return empty list when creation fails
    category_ids = wp_tool._get_or_create_categories(["TestCategory"])
    
    assert category_ids == []


@patch("builtins.open", create=True)
@patch("os.path.exists")
def test_upload_media_success(mock_exists, mock_open_func, wp_tool):
    """Test successful media upload."""
    mock_exists.return_value = True
    mock_open_func.return_value.__enter__.return_value.read.return_value = b"fake image data"
    
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "id": 50,
        "source_url": "https://mkfoster.com/wp-content/uploads/image.jpg",
    }
    
    with patch("requests.post", return_value=mock_response):
        result = wp_tool.upload_media("/path/to/image.jpg")
    
    assert result["success"] is True
    assert result["media_id"] == 50
    assert "url" in result


@patch("os.path.exists")
def test_upload_media_file_not_found(mock_exists, wp_tool):
    """Test media upload with missing file."""
    mock_exists.return_value = False
    
    result = wp_tool.upload_media("/nonexistent/image.jpg")
    
    assert result["success"] is False
    assert "error" in result


def test_close(wp_tool):
    """Test session cleanup."""
    wp_tool.close()
    # Just ensure no errors occur
