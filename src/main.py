"""
MyNewsRobot - Main Application Entry Point

This module initializes and runs the weekly news summary workflow.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config_loader import config_loader
from utils.date_formatter import format_newsletter_date
from utils.memory_manager import memory_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="MyNewsRobot",
    description="AI-powered weekly news summary agent",
    version="0.1.0",
)


class RunRequest(BaseModel):
    """Request model for triggering a workflow run."""

    manual_trigger: bool = False
    test_mode: bool = False


class RunResponse(BaseModel):
    """Response model for workflow execution."""

    status: str
    message: str
    execution_time: float
    articles_found: int = 0
    summary_url: str = ""


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "service": "MyNewsRobot",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health():
    """Health check endpoint for Cloud Run."""
    try:
        # Test configuration loading
        config_loader.get_google_ai_config()
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/run", response_model=RunResponse)
async def run_workflow(request: RunRequest):
    """
    Trigger the weekly news summary workflow.

    This endpoint is called by Cloud Scheduler or can be triggered manually.
    """
    start_time = datetime.now()
    logger.info("Starting weekly news summary workflow")

    try:
        # Load configurations
        logger.info("Loading configurations...")
        news_sources = config_loader.get_news_sources()
        topic_priorities = config_loader.get_topic_priorities()
        bookmarks = config_loader.get_weekly_bookmarks()
        wordpress_config = config_loader.get_wordpress_config()

        logger.info(
            f"Loaded {len(news_sources.get('news_sources', {}))} source categories"
        )
        logger.info(f"Loaded {len(topic_priorities.get('topics', []))} topic priorities")
        logger.info(f"Loaded {len(bookmarks.get('bookmarks', []))} bookmarks")

        # TODO: Phase 2-4 - Implement workflow agents
        # This is a placeholder for now
        logger.info("Workflow agents will be implemented in Phase 2-4")

        execution_time = (datetime.now() - start_time).total_seconds()

        return RunResponse(
            status="success",
            message=f"Workflow completed successfully (Phase 1 - configuration only)",
            execution_time=execution_time,
            articles_found=0,
            summary_url="",
        )

    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        execution_time = (datetime.now() - start_time).total_seconds()

        return RunResponse(
            status="error",
            message=f"Workflow failed: {str(e)}",
            execution_time=execution_time,
        )


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
