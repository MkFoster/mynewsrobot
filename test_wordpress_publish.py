"""
Test WordPress Publishing Tool

This script tests the WordPress publishing functionality by creating a sample post.
Run this from the command line to verify WordPress API connectivity and credentials.
"""

import sys
from pathlib import Path
import logging

# Setup logging to see debug output
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Add project root to path
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.tools.wordpress_tool import publish_to_wordpress
import json

def main():
    """Test publishing a sample post to WordPress."""
    
    # Check configuration
    from src.utils.config_loader import config_loader
    wp_config = config_loader.get_wordpress_config()
    site_url = wp_config.get("wordpress", {}).get("site_url", "")
    username = config_loader.get_env("WORDPRESS_USERNAME", "")
    app_password = config_loader.get_env("WORDPRESS_APP_PASSWORD", "")
    app_password_clean = app_password.replace(" ", "")
    
    print(f"Site URL: {site_url}")
    print(f"Username: {username}")
    print(f"App Password (raw from .env): {app_password}")
    print(f"App Password (spaces removed): {app_password_clean}")
    print(f"App Password length: {len(app_password)} chars (raw), {len(app_password_clean)} chars (clean)")
    print(f"Credentials string: {username}:{app_password_clean}")
    print()
    
    # Sample newsletter content
    sample_title = "Test Post from MyNewsRobot"
    sample_excerpt = "This is a test post to verify WordPress API connectivity and authentication."
    sample_content = """
    <h2>Test Newsletter</h2>
    <p>This is a test post created by the MyNewsRobot WordPress publishing tool.</p>
    
    <h3>Test Article 1</h3>
    <p>This is a sample article with some content to test HTML formatting.</p>
    
    <h3>Test Article 2</h3>
    <p>Another sample article to ensure the publishing system works correctly.</p>
    
    <p><strong>If you can see this post in WordPress, the publishing system is working!</strong></p>
    """
    
    print(f"Title: {sample_title}")
    print(f"Excerpt: {sample_excerpt}")
    print(f"Status: private")
    print(f"Categories: ['WeeklySummary']")
    print(f"Content length: {len(sample_content)} characters\n")
    
    print("Attempting to publish to WordPress...")
    print("-" * 60 + "\n")
    
    try:
        result = publish_to_wordpress(
            title=sample_title,
            content=sample_content,
            status="private",
            categories=["WeeklySummary"],
            excerpt=sample_excerpt
        )
        
        print("\n" + "="*60)
        print("RESULT:")
        print("="*60)
        print(json.dumps(result, indent=2))
        print()
        
        if result.get("success"):
            print("✅ SUCCESS! Post published to WordPress")
            if result.get("post_url"):
                print(f"📍 Post URL: {result['post_url']}")
            if result.get("edit_url"):
                print(f"✏️  Edit URL: {result['edit_url']}")
            print(f"🆔 Post ID: {result.get('post_id')}")
            print(f"📊 Status: {result.get('status')}")
        else:
            print("❌ FAILED! Post was not published")
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        print("\n" + "="*60 + "\n")
        
        return 0 if result.get("success") else 1
        
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
