"""
Unit tests for BookmarkLoaderTool
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from src.tools.bookmark_loader_tool import BookmarkLoaderTool


@pytest.fixture
def bookmark_tool():
    """Create a BookmarkLoaderTool instance for testing."""
    return BookmarkLoaderTool("config/weekly_bookmarks.yaml")


@pytest.fixture
def sample_bookmarks_yaml():
    """Sample bookmark YAML content."""
    return """
bookmarks:
  - url: "https://example.com/article1"
    note: "Test article 1"
    submitted_date: "2025-11-28"
  - url: "https://example.com/article2"
    note: "Test article 2"
    submitted_date: "2025-11-29"
"""


def test_bookmark_loader_init(bookmark_tool):
    """Test BookmarkLoaderTool initialization."""
    assert bookmark_tool.name == "bookmark_loader"
    assert bookmark_tool.config_path == "config/weekly_bookmarks.yaml"


def test_load_from_local_success(bookmark_tool, sample_bookmarks_yaml):
    """Test successful loading from local file."""
    with patch("builtins.open", mock_open(read_data=sample_bookmarks_yaml)):
        result = bookmark_tool._load_from_local("config/weekly_bookmarks.yaml")
        
        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["bookmarks"]) == 2
        assert result["bookmarks"][0]["url"] == "https://example.com/article1"
        assert result["bookmarks"][0]["priority"] == 11
        assert result["bookmarks"][1]["note"] == "Test article 2"


def test_load_from_local_empty_bookmarks(bookmark_tool):
    """Test loading from file with empty bookmarks list."""
    empty_yaml = "bookmarks: []"
    
    with patch("builtins.open", mock_open(read_data=empty_yaml)):
        result = bookmark_tool._load_from_local("config/weekly_bookmarks.yaml")
        
        assert result["success"] is True
        assert result["count"] == 0
        assert result["bookmarks"] == []


def test_load_from_local_none_bookmarks(bookmark_tool):
    """Test loading from file with None bookmarks."""
    none_yaml = "bookmarks:"
    
    with patch("builtins.open", mock_open(read_data=none_yaml)):
        result = bookmark_tool._load_from_local("config/weekly_bookmarks.yaml")
        
        assert result["success"] is True
        assert result["count"] == 0
        assert result["bookmarks"] == []


def test_load_from_local_invalid_bookmark(bookmark_tool):
    """Test handling of invalid bookmark entries."""
    invalid_yaml = """
bookmarks:
  - url: "https://valid.com/article"
    note: "Valid"
  - invalid_entry
  - missing_url: true
    note: "No URL field"
"""
    
    with patch("builtins.open", mock_open(read_data=invalid_yaml)):
        result = bookmark_tool._load_from_local("config/weekly_bookmarks.yaml")
        
        assert result["success"] is True
        assert result["count"] == 1  # Only one valid bookmark
        assert result["bookmarks"][0]["url"] == "https://valid.com/article"


def test_run_local_file_success(bookmark_tool, sample_bookmarks_yaml):
    """Test run() with local file."""
    with patch("builtins.open", mock_open(read_data=sample_bookmarks_yaml)):
        result = bookmark_tool.run()
        
        assert result["success"] is True
        assert result["count"] == 2
        assert "source" in result


def test_run_file_not_found(bookmark_tool):
    """Test run() when file doesn't exist."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = bookmark_tool.run()
        
        assert result["success"] is True  # Gracefully handles missing file
        assert result["count"] == 0
        assert result["bookmarks"] == []
        assert "warning" in result


def test_run_yaml_parse_error(bookmark_tool):
    """Test run() with invalid YAML."""
    invalid_yaml = "bookmarks: [invalid yaml structure"
    
    with patch("builtins.open", mock_open(read_data=invalid_yaml)):
        result = bookmark_tool.run()
        
        assert result["success"] is False
        assert "error" in result


def test_gcs_path_detection(bookmark_tool):
    """Test GCS path detection."""
    gcs_tool = BookmarkLoaderTool("gs://my-bucket/bookmarks.yaml")
    
    with patch.object(gcs_tool, "_load_from_gcs") as mock_gcs:
        mock_gcs.return_value = {"success": True, "bookmarks": [], "count": 0}
        result = gcs_tool.run()
        mock_gcs.assert_called_once()


@patch("google.cloud.storage")
def test_load_from_gcs_success(mock_storage_module, sample_bookmarks_yaml):
    """Test successful loading from GCS."""
    # Mock GCS client
    mock_client = Mock()
    mock_bucket = Mock()
    mock_blob = Mock()
    mock_blob.download_as_text.return_value = sample_bookmarks_yaml
    mock_bucket.blob.return_value = mock_blob
    mock_client.bucket.return_value = mock_bucket
    mock_storage_module.Client.return_value = mock_client
    
    tool = BookmarkLoaderTool("gs://test-bucket/bookmarks.yaml")
    result = tool._load_from_gcs("gs://test-bucket/bookmarks.yaml")
    
    assert result["success"] is True
    assert result["count"] == 2
    assert result["source"] == "gs://test-bucket/bookmarks.yaml"


def test_load_from_gcs_invalid_path(bookmark_tool):
    """Test GCS loading with invalid path."""
    with pytest.raises(ValueError, match="Invalid GCS path"):
        bookmark_tool._load_from_gcs("invalid://path")


def test_bookmark_priority_always_11(bookmark_tool, sample_bookmarks_yaml):
    """Test that all bookmarks get priority 11."""
    with patch("builtins.open", mock_open(read_data=sample_bookmarks_yaml)):
        result = bookmark_tool.run()
        
        for bookmark in result["bookmarks"]:
            assert bookmark["priority"] == 11
