"""
Test WordPress Authentication and Permissions

This script tests if the WordPress credentials are valid and what permissions the user has.
"""

import sys
from pathlib import Path
import requests
import base64

# Add project root to path
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.config_loader import config_loader

def main():
    """Test WordPress authentication and check user permissions."""
    
    print("\n" + "="*60)
    print("WordPress Authentication & Permissions Test")
    print("="*60 + "\n")
    
    # Get configuration
    wp_config = config_loader.get_wordpress_config()
    wp_settings = wp_config.get("wordpress", {})
    site_url = wp_settings.get("site_url", "https://mkfoster.com").rstrip("/")
    api_endpoint = wp_settings.get("api_endpoint", "/wp-json/wp/v2")
    username = config_loader.get_env("WORDPRESS_USERNAME", "")
    app_password = config_loader.get_env("WORDPRESS_APP_PASSWORD", "").replace(" ", "")
    
    print(f"Site: {site_url}")
    print(f"Username: {username}")
    print(f"Password length: {len(app_password)} chars\n")
    
    # Create auth header
    credentials = f"{username}:{app_password}"
    token = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }
    
    print("="*60)
    print("Test 1: Check if Application Passwords are available")
    print("="*60)
    
    try:
        response = requests.get(f"{site_url}/wp-json/", timeout=10)
        if response.ok:
            data = response.json()
            auth_info = data.get("authentication", {})
            print(f"✅ REST API is accessible")
            print(f"Authentication methods: {list(auth_info.keys())}")
            
            if "application-passwords" in auth_info:
                print("✅ Application Passwords are available")
            else:
                print("⚠️  Application Passwords NOT available")
                print("This might be because:")
                print("  - Site is not using HTTPS")
                print("  - Feature has been disabled")
        else:
            print(f"❌ REST API not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("Test 2: Get current user info (tests authentication)")
    print("="*60)
    
    try:
        response = requests.get(
            f"{site_url}{api_endpoint}/users/me?context=edit",
            headers=headers,
            timeout=10
        )
        
        if response.ok:
            user = response.json()
            print(f"✅ Authentication successful!")
            print(f"\nUser Details:")
            print(f"  ID: {user.get('id')}")
            print(f"  Username: {user.get('username')}")
            print(f"  Name: {user.get('name')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Roles: {user.get('roles')}")
            print(f"\nCapabilities:")
            caps = user.get('capabilities', {})
            for cap, value in sorted(caps.items()):
                if value:
                    print(f"  ✓ {cap}")
            
            # Check specific post-related capabilities
            print(f"\nPost Creation Capabilities:")
            post_caps = ['publish_posts', 'edit_posts', 'delete_posts', 'edit_published_posts']
            for cap in post_caps:
                has_cap = caps.get(cap, False)
                icon = "✅" if has_cap else "❌"
                print(f"  {icon} {cap}: {has_cap}")
                
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("Test 3: List existing posts (read permission)")
    print("="*60)
    
    try:
        response = requests.get(
            f"{site_url}{api_endpoint}/posts?per_page=5",
            headers=headers,
            timeout=10
        )
        
        if response.ok:
            posts = response.json()
            print(f"✅ Can read posts: Found {len(posts)} posts")
            for post in posts[:3]:
                print(f"  - {post.get('title', {}).get('rendered', 'Untitled')} (ID: {post.get('id')})")
        else:
            print(f"⚠️  Cannot read posts: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
