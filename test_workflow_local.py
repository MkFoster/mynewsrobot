"""
Test script to run the complete MyNewsRobot workflow locally

This script starts the FastAPI server and tests the workflow endpoint.

Run this to test the entire workflow before deployment.
"""

import requests
import time
import subprocess
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_workflow_via_api():
    """Test the workflow by calling the FastAPI endpoint."""
    
    logger.info("=" * 80)
    logger.info("MyNewsRobot - Local Workflow Test via API")
    logger.info("=" * 80)
    
    base_url = "http://localhost:8080"
    
    # Test 1: Health check
    logger.info("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            logger.info("   ✓ Health check passed")
            logger.info(f"   Response: {response.json()}")
        else:
            logger.error(f"   ✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("   ✗ Server not running. Start it with: python src/main.py")
        logger.info("\nTo start the server, run in another terminal:")
        logger.info("   python src/main.py")
        return False
    except Exception as e:
        logger.error(f"   ✗ Health check error: {e}")
        return False
    
    # Test 2: Configuration status
    logger.info("\n2. Testing Configuration Status...")
    try:
        response = requests.get(f"{base_url}/config/status", timeout=5)
        if response.status_code == 200:
            config = response.json()
            logger.info("   ✓ Configuration loaded")
            logger.info(f"   News Sources: {config.get('news_sources', {})}")
            logger.info(f"   Topics: {config.get('topics', 0)}")
            logger.info(f"   Bookmarks: {config.get('bookmarks', 0)}")
            logger.info(f"   WordPress: {config.get('google_ai', {})}")
        else:
            logger.error(f"   ✗ Config check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"   ✗ Config check error: {e}")
        return False
    
    # Test 3: Run workflow
    logger.info("\n3. Testing Workflow Execution...")
    logger.info("   This will:")
    logger.info("   - Create the SequentialAgent workflow")
    logger.info("   - Initialize all 5 agents")
    logger.info("   - Log the workflow structure")
    logger.info("   (Note: Full execution requires ADK App runner)")
    
    try:
        response = requests.post(
            f"{base_url}/run",
            json={"test_mode": True},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info("   ✓ Workflow endpoint responded")
            logger.info(f"   Status: {result.get('status')}")
            logger.info(f"   Message: {result.get('message')}")
            logger.info(f"   Execution Time: {result.get('execution_time', 0):.2f}s")
        else:
            logger.error(f"   ✗ Workflow execution failed: {response.status_code}")
            logger.error(f"   Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"   ✗ Workflow execution error: {e}")
        return False
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("Test Summary")
    logger.info("=" * 80)
    logger.info("✓ Server is running")
    logger.info("✓ Health check passed")
    logger.info("✓ Configuration loaded")
    logger.info("✓ Workflow endpoint responded")
    logger.info("\nWorkflow Structure:")
    logger.info("  1. NewsResearchAgent - Discovers articles from RSS/HTML sources")
    logger.info("  2. ContentExtractionAgent - Extracts full content")
    logger.info("  3. ContentAnalysisAgent - Selects top 20 articles")
    logger.info("  4. ContentWritingAgent - Writes summaries (~200 tokens each)")
    logger.info("  5. PublishingAgent - Posts to WordPress (private status)")
    logger.info("\nNext Steps:")
    logger.info("  1. Implement ADK App runner for full agent execution")
    logger.info("  2. Add session/state management")
    logger.info("  3. Test with real news sources")
    logger.info("  4. Verify WordPress posting creates private posts")
    
    return True


if __name__ == "__main__":
    logger.info("Make sure the FastAPI server is running before this test!")
    logger.info("Start it with: python src/main.py\n")
    
    time.sleep(1)  # Give user time to read
    
    try:
        success = test_workflow_via_api()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        sys.exit(1)
