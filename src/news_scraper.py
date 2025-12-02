"""
news_scraper.py - Scrape all news sources and weekly bookmarks, output article metadata to JSON

This script:
1. Loads news sources from config
2. Loads weekly bookmarks
3. Scrapes each news source for article metadata (not full content)
4. Stores all discovered articles in discovered_articles.json for analysis
"""

import logging
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.tools import scrape_web_content, load_user_bookmarks
from src.utils.config_loader import config_loader
from src.utils.memory_manager import memory_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("news_scraper")

OUTPUT_FILE = "discovered_articles.json"

def main():
    # Load news sources
    news_config = config_loader.get_news_sources()
    sources = []
    for category, category_data in (news_config.get("news_sources") or {}).items():
        pages = category_data.get("pages") or []
        for page in pages:
            sources.append({
                "url": page["url"],
                "name": page["name"],
                "type": page.get("type", "auto"),
                "category": category,
            })
    logger.info(f"Loaded {len(sources)} news sources from config")

    # Load weekly bookmarks
    bookmarks_result = load_user_bookmarks()
    bookmarks = bookmarks_result.get("bookmarks", [])
    logger.info(f"Loaded {len(bookmarks)} weekly bookmarks")

    # Scrape each news source for metadata (RSS feeds only)
    articles = []
    for source in sources:
        # Enforce RSS-only - skip if not RSS feed
        source_type = source["type"]
        if source_type not in ["rss", "auto"]:
            logger.warning(f"Skipping non-RSS source {source['url']} (type={source_type}). Only RSS feeds are supported.")
            continue
            
        # Force RSS mode - we only support RSS feeds now
        result = scrape_web_content(
            url=source["url"],
            mode="rss",  # Always use RSS mode
            extract_links=False,  # Don't extract links, RSS feeds provide entries directly
            timeout=30
        )
        if result.get("success"):
            result_type = result.get("type")
            if result_type != "rss":
                logger.warning(f"Skipping {source['url']} - not a valid RSS feed (detected type: {result_type})")
                continue
                
            entries = result.get("entries") or []
            for entry in entries:
                article = {
                    "url": entry.get("link"),
                    "title": entry.get("title"),
                    "excerpt": entry.get("summary") or entry.get("content"),
                    "source": source["name"],
                    "category": source["category"],
                    "published_date": entry.get("published_date"),
                    "is_bookmark": False,
                }
                # Filter out processed URLs
                if not memory_manager.is_processed(article["url"]):
                    articles.append(article)
        else:
            logger.warning(f"Failed to scrape RSS feed {source['url']}: {result.get('error')}")

    # Add bookmarks (always include)
    for bm in bookmarks:
        articles.append({
            "url": bm["url"],
            "title": bm.get("note", "User Bookmark"),
            "excerpt": bm.get("note", ""),
            "source": "User Bookmark",
            "category": "bookmark",
            "published_date": bm.get("submitted_date"),
            "is_bookmark": True,
        })

    logger.info(f"Discovered {len(articles)} articles (including bookmarks)")

    # Save to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved discovered articles to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
