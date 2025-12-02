"""
MyNewsRobot - Main Application Entry Point

This module initializes and runs the weekly news summary workflow.
"""

import asyncio
import logging
import os
import sys
import subprocess

from datetime import datetime
from pathlib import Path
import json

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.genai import types
from google.adk import Runner
from google.adk.apps import App
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from google.adk import Agent

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.config_loader import config_loader
from src.agents.content_analysis_agent import ContentAnalysisAgent
from src.agents.content_writing_agent import ContentWritingAgent
from src.agents.publishing_agent import PublishingAgent

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create the content analysis agent as the root agent for the app
content_analysis_agent = ContentAnalysisAgent.create_agent()

# Initialize Google GenAI App with the ContentAnalysisAgent
app_instance = App(
    name="MyNewsRobotApp",
    root_agent=content_analysis_agent,
    resumability_config=None
)

# Initialize Google GenAI Runner and session service
session_service = InMemorySessionService()
runner = Runner(
    app=app_instance,
    session_service=session_service,
    artifact_service=InMemoryArtifactService(),
    memory_service=InMemoryMemoryService()
)

# Define request and response models
class RunRequest(BaseModel):
    """Request model for running the workflow."""
    newsletter_date: str

class RunResponse(BaseModel):
    """Response model for workflow execution."""
    status: str
    message: str
    execution_time: float
    articles_found: int
    summary_url: str
    tool_calls_made: int


def format_newsletter_date(date: datetime = None) -> str:
    """Format the newsletter date for the subject and folder naming."""
    if date is None:
        date = datetime.now()
    return date.strftime("%Y-%m-%d")


# Function to run the news scraper script
def run_news_scraper():
    logger.info("📰 Step 1: Discovering articles from RSS feeds...")
    scraper_path = Path(__file__).parent / "news_scraper.py"
    if not scraper_path.exists():
        raise RuntimeError("news_scraper.py not found. Ensure the script is in the same directory.")

    # Set the working directory explicitly to ensure the scraper runs in the correct context
    result = subprocess.run(["python", str(scraper_path)], cwd=Path(__file__).parent, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"news_scraper.py failed: {result.stderr}")

    logger.info("✅ News scraper executed successfully.")

# Function to analyze articles using the content analysis agent
async def analyze_articles(articles):
    """
    Analyze articles using the ContentAnalysisAgent to select the top 20.
    
    Args:
        articles: List of discovered articles with titles and excerpts
        
    Returns:
        List of top 20 analyzed articles with priority scores
    """
    logger.info("🔍 Step 2: Analyzing articles and selecting top 20 by topic priorities...")
    # Prepare the prompt with articles data
    articles_json = json.dumps(articles, indent=2)
    prompt = f"""
Analyze the following {len(articles)} articles and select the top 20 based on topic priorities.

Articles:
{articles_json}

Remember to:
1. FIRST call get_topic_priorities() to load the topic configuration
2. Match each article against the topic keywords
3. Assign priority scores (7-11) based on topic relevance
4. Select the top 20 highest-priority articles
5. Return the selected articles with their priority scores and matched topics
"""
    
    # Create a session for this analysis
    session = await session_service.create_session(
        app_name="MyNewsRobotApp",
        user_id="default_user",
        session_id=f"content_analysis_{datetime.now().timestamp()}"
    )
    
    message = types.Content(role='user', parts=[types.Part(text=prompt)])
    
    analyzed_articles = []
    response_text = ""
    tool_calls_count = 0
    
    logger.info("🤖 Starting agent execution...")
    async for event in runner.run_async(
        user_id="default_user",
        session_id=session.id,
        new_message=message
    ):
        # Log tool calls
        if hasattr(event, 'tool_call') and event.tool_call:
            tool_calls_count += 1
            logger.info(f"🔧 Tool call #{tool_calls_count}: {event.tool_call.name if hasattr(event.tool_call, 'name') else 'unknown'}")
        
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    # Log the agent's response
                    logger.info(f"📝 Agent response chunk ({len(part.text)} chars)")
                    response_text += part.text
    
    logger.info(f"✅ Agent execution complete. Total response: {len(response_text)} chars, {tool_calls_count} tool calls")
    
    # Parse the agent's response to extract the selected articles
    # The agent should return JSON with the selected articles
    try:
        # Try to find JSON in the response
        import re
        # Look for JSON array in the response
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            logger.info(f"📊 Found JSON in response ({len(json_match.group())} chars), parsing...")
            selected_articles_data = json.loads(json_match.group())
            logger.info(f"✅ Successfully parsed {len(selected_articles_data)} articles from agent response")
            analyzed_articles = selected_articles_data
        else:
            # Fallback: if no JSON found, use first 20 articles
            logger.warning("⚠️ Could not find JSON array in agent response")
            logger.warning(f"Response preview: {response_text[:500]}...")
            logger.warning("Using first 20 articles as fallback")
            analyzed_articles = articles[:20]
    except Exception as e:
        logger.error(f"❌ Error parsing agent response: {e}")
        logger.error(f"Response preview: {response_text[:500]}...")
        logger.warning("Using first 20 articles as fallback")
        analyzed_articles = articles[:20]
    
    return analyzed_articles


async def write_newsletter(articles: list) -> str:
    """
    Generate newsletter content using ContentWritingAgent.
    
    Args:
        articles: List of analyzed articles with metadata
        
    Returns:
        Newsletter HTML content
    """
    # Create a prompt for the writing agent
    newsletter_date = ContentWritingAgent.get_newsletter_date()
    writing_style = ContentWritingAgent.get_writing_style()
    
    prompt = f"""
    Write a weekly newsletter for the date: {newsletter_date}
    
    Here are the {len(articles)} selected articles to include:
    
    {json.dumps(articles, indent=2)}
    
    Writing Style Guidelines:
    {json.dumps(writing_style, indent=2)}
    
    Create a complete newsletter with:
    1. Title: "Mark's Weekly Update: {newsletter_date}"
    2. Introduction paragraph (150-200 words)
    3. All {len(articles)} articles with summaries (~150 words each)
    4. Brief conclusion
    
    Format as clean HTML ready for WordPress.
    """
    
    # Create the writing agent
    writing_agent = ContentWritingAgent.create_agent()
    writing_app = App(
        name="NewsletterWritingApp",
        root_agent=writing_agent,
        resumability_config=None
    )
    writing_runner = Runner(
        app=writing_app,
        session_service=session_service,
        artifact_service=InMemoryArtifactService(),
        memory_service=InMemoryMemoryService()
    )
    
    # Create session for writing agent
    session = await session_service.create_session(
        app_name="NewsletterWritingApp",
        user_id="default_user"
    )
    message = types.Content(role='user', parts=[types.Part(text=prompt)])
    
    newsletter_content = ""
    response_text = ""
    tool_calls_count = 0
    
    logger.info("📝 Starting newsletter writing...")
    async for event in writing_runner.run_async(
        user_id="default_user",
        session_id=session.id,
        new_message=message
    ):
        # Log tool calls
        if hasattr(event, 'tool_call') and event.tool_call:
            tool_calls_count += 1
            logger.info(f"🔧 Tool call #{tool_calls_count}: {event.tool_call.name if hasattr(event.tool_call, 'name') else 'unknown'}")
        
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    logger.info(f"📝 Newsletter content chunk ({len(part.text)} chars)")
                    response_text += part.text
    
    logger.info(f"✅ Newsletter writing complete. Total: {len(response_text)} chars, {tool_calls_count} tool calls")
    
    # The response should be the newsletter HTML
    newsletter_content = response_text
    
    # Save newsletter to file for debugging
    newsletter_output_path = Path(__file__).parent / "newsletter_draft.html"
    with open(newsletter_output_path, "w", encoding="utf-8") as f:
        f.write(newsletter_content)
    
    logger.info(f"💾 Newsletter saved to: {newsletter_output_path}")
    
    return newsletter_content


async def publish_newsletter(newsletter_html: str, newsletter_date: str) -> Dict:
    """
    Publish newsletter to WordPress using PublishingAgent.
    
    Args:
        newsletter_html: Complete newsletter HTML content
        newsletter_date: Newsletter date string (e.g., "December 1, 2025")
        
    Returns:
        Publication result with URLs
    """
    # Extract title and excerpt from HTML (simple parsing)
    import re
    
    # Use formatted date for the title
    from src.utils.date_formatter import format_newsletter_date
    formatted_date = format_newsletter_date() if newsletter_date == "string" else newsletter_date
    title = f"Mark's Weekly Update: {formatted_date}"
    
    # Extract first paragraph as excerpt
    excerpt_match = re.search(r'<p[^>]*>(.+?)</p>', newsletter_html, re.IGNORECASE)
    if excerpt_match:
        excerpt = excerpt_match.group(1)
        excerpt = re.sub(r'<[^>]+>', '', excerpt).strip()[:200]  # Remove tags, limit length
    else:
        excerpt = f"Weekly newsletter for {formatted_date}"
    
    prompt = f"""
    YOU MUST call the publish_to_wordpress tool to publish this newsletter to WordPress.
    
    Call publish_to_wordpress with these exact parameters:
    
    title: {title}
    content: {newsletter_html}
    status: private
    categories: ["WeeklySummary"]
    excerpt: {excerpt}
    
    Do NOT respond with text. ONLY call the publish_to_wordpress tool.
    """
    
    # Create the publishing agent
    publishing_agent = PublishingAgent.create_agent()
    publishing_app = App(
        name="NewsletterPublishingApp",
        root_agent=publishing_agent,
        resumability_config=None
    )
    publishing_runner = Runner(
        app=publishing_app,
        session_service=session_service,
        artifact_service=InMemoryArtifactService(),
        memory_service=InMemoryMemoryService()
    )
    
    # Create session for publishing agent
    session = await session_service.create_session(
        app_name="NewsletterPublishingApp",
        user_id="default_user"
    )
    message = types.Content(role='user', parts=[types.Part(text=prompt)])
    
    publication_result = {}
    response_text = ""
    tool_calls_count = 0
    
    logger.info("🚀 Starting newsletter publishing...")
    async for event in publishing_runner.run_async(
        user_id="default_user",
        session_id=session.id,
        new_message=message
    ):
        # Log tool calls
        if hasattr(event, 'tool_call') and event.tool_call:
            tool_calls_count += 1
            logger.info(f"🔧 Tool call #{tool_calls_count}: {event.tool_call.name if hasattr(event.tool_call, 'name') else 'unknown'}")
        
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    logger.info(f"📤 Publishing response chunk ({len(part.text)} chars)")
                    response_text += part.text
    
    logger.info(f"✅ Newsletter publishing complete. Total: {len(response_text)} chars, {tool_calls_count} tool calls")
    
    # Try to extract URLs from response
    post_url = None
    edit_url = None
    
    # Look for URLs in the response
    url_pattern = r'https?://[^\s<>"]+'
    urls = re.findall(url_pattern, response_text)
    if urls:
        for url in urls:
            if 'wp-admin' in url or 'action=edit' in url:
                edit_url = url
            elif not post_url:
                post_url = url
    
    publication_result = {
        "success": bool(post_url or edit_url),
        "post_url": post_url,
        "edit_url": edit_url,
        "response": response_text,
        "tool_calls": tool_calls_count
    }
    
    return publication_result


# Correcting misplaced code and ensuring proper indentation
async def run_workflow(request: RunRequest):
    start_time = datetime.now()

    # Step 1: Run the news scraper
    run_news_scraper()

    # Step 2: Load discovered articles from JSON
    discovered_articles_path = Path(__file__).parent / "discovered_articles.json"
    if not discovered_articles_path.exists():
        raise RuntimeError("discovered_articles.json not found. Run news_scraper.py first.")

    with open(discovered_articles_path, "r", encoding="utf-8") as f:
        discovered_articles = json.load(f)

    logger.info(f"Loaded {len(discovered_articles)} articles from discovered_articles.json")

    # Step 3: Analyze articles using ContentAnalysisAgent
    analyzed_articles = await analyze_articles(discovered_articles)

    # Step 4: Save analysis results to JSON
    analysis_output_path = Path(__file__).parent / "analyzed_articles.json"
    with open(analysis_output_path, "w", encoding="utf-8") as f:
        json.dump(analyzed_articles, f, indent=4)

    logger.info(f"✅ Analysis complete. Top {len(analyzed_articles)} articles selected and saved.")

    # Step 3: Generate newsletter content using ContentWritingAgent
    logger.info("✍️ Step 3: Writing newsletter summaries...")
    newsletter_content = await write_newsletter(analyzed_articles)
    logger.info(f"✅ Newsletter writing complete. {len(newsletter_content)} characters generated.")
    
    # Step 4: Publish to WordPress using PublishingAgent
    logger.info("🚀 Step 4: Publishing to WordPress...")
    publication_result = await publish_newsletter(newsletter_content, request.newsletter_date)
    
    if publication_result.get("success"):
        logger.info(f"✅ Newsletter published successfully!")
        if publication_result.get("post_url"):
            logger.info(f"📍 Post URL: {publication_result['post_url']}")
        if publication_result.get("edit_url"):
            logger.info(f"✏️ Edit URL: {publication_result['edit_url']}")
    else:
        logger.warning("⚠️ Newsletter publishing may have failed. Check the logs.")

    # Complete workflow
    execution_time = (datetime.now() - start_time).total_seconds()
    summary_url = publication_result.get("post_url") or publication_result.get("edit_url") or str(Path(__file__).parent / "newsletter_draft.html")
    
    return RunResponse(
        status="success",
        message=f"Workflow complete. {len(analyzed_articles)} articles analyzed, newsletter written and published.",
        execution_time=execution_time,
        articles_found=len(discovered_articles),
        summary_url=summary_url,
        tool_calls_made=publication_result.get("tool_calls", 0)
    )


@app.post("/run")
async def run_endpoint(request: RunRequest):
    """Run the news summary workflow."""
    logger.info(f"\n🤖 === Starting MyNewsRobot Workflow: {request.newsletter_date} ===")
    response = await run_workflow(request)
    logger.info("✅ === Workflow Complete ===")
    return response


@app.get("/config/status")
async def config_status():
    """Get configuration status and validation."""
    try:
        news_sources = config_loader.get_news_sources()
        topic_priorities = config_loader.get_topic_priorities()
        bookmarks = config_loader.get_weekly_bookmarks()
        gcp_config = config_loader.get_google_cloud_config()

        # Count sources - handle None values from YAML
        total_pages = sum(
            len(category.get("pages", []) or [])
            for category in (news_sources.get("news_sources") or {}).values()
        )

        return {
            "status": "configured",
            "news_sources": {
                "categories": len(news_sources.get("news_sources") or {}),
                "total_pages": total_pages,
            },
            "topics": len(topic_priorities.get("topics") or []),
            "bookmarks": len(bookmarks.get("bookmarks") or []),
            "google_ai": {
                "api_key_configured": bool(gcp_config.get("api_key")),
                "project": gcp_config.get("project", "not-set"),
                "location": gcp_config.get("location", "not-set"),
            },
            "memory_stats": {"processed_urls": memory_manager.get_processed_count()},
        }
    except Exception as e:
        logger.error(f"Config status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


def main():
    """Main entry point for the application."""
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting MyNewsRobot on {host}:{port}")

    # Print current week for newsletter
    current_date = format_newsletter_date()
    logger.info(f"Current newsletter date: Mark's Weekly Update: {current_date}")

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
