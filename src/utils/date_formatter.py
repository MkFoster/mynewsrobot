"""
Date formatting utilities for MyNewsRobot
"""

from datetime import datetime
from typing import Optional


def format_newsletter_date(
    date: Optional[datetime] = None, pattern: str = "%B %dth, %Y"
) -> str:
    """
    Format a date for the newsletter title.

    Args:
        date: Date to format. Defaults to current date.
        pattern: strftime pattern. Defaults to "November 28th, 2025" format.

    Returns:
        Formatted date string

    Examples:
        >>> format_newsletter_date(datetime(2025, 11, 28))
        'November 28th, 2025'
    """
    if date is None:
        date = datetime.now()

    # Handle ordinal suffix (1st, 2nd, 3rd, 4th, etc.)
    day = date.day
    if 10 <= day % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    # Replace %dth with actual day + suffix
    formatted = date.strftime(pattern.replace("%dth", f"{day}{suffix}"))

    return formatted


def get_week_range(date: Optional[datetime] = None) -> tuple[datetime, datetime]:
    """
    Get the start and end dates of the week containing the given date.

    Args:
        date: Reference date. Defaults to current date.

    Returns:
        Tuple of (week_start, week_end) as datetime objects
    """
    if date is None:
        date = datetime.now()

    # Find Monday of the current week
    days_since_monday = date.weekday()
    week_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = week_start - datetime.timedelta(days=days_since_monday)

    # Find Sunday of the current week
    week_end = week_start + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59)

    return week_start, week_end


def format_iso_date(date: Optional[datetime] = None) -> str:
    """
    Format date as ISO 8601 string.

    Args:
        date: Date to format. Defaults to current date.

    Returns:
        ISO formatted date string (YYYY-MM-DD)
    """
    if date is None:
        date = datetime.now()

    return date.strftime("%Y-%m-%d")
