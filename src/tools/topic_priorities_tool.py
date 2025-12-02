"""
TopicPrioritiesTool - A tool for retrieving topic priorities

This tool:
1. Loads topic priorities from configuration
2. Logs the priorities for debugging
3. Returns the priorities for use in other agents or tools
"""

import logging
from typing import Any, Dict

from ..utils.config_loader import config_loader

logger = logging.getLogger(__name__)

def get_topic_priorities() -> Dict[str, Any]:
    """
    Get configured topic priorities for article analysis.
    
    This tool retrieves the topic priority configuration which includes:
    - Topic names and their priority levels (7-11 scale)
    - Keywords associated with each topic
    - Priority weights for ranking articles
    
    Returns:
        Dictionary containing topic priorities configuration with topics,
        keywords, and priority levels for article ranking.
    """
    # Log the topic priorities to the terminal for debugging
    topic_priorities = config_loader.get_topic_priorities()
    logger.info(f"Loaded topic priorities: {topic_priorities}")
    return topic_priorities