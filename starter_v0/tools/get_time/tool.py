from __future__ import annotations

from datetime import datetime
from typing import Any


def get_current_time() -> dict[str, Any]:
    """Returns the current date and time of the system."""
    now = datetime.now()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return {
        "tool": "get_time",
        "formatted_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": str(now.astimezone().tzinfo),
        "day_of_week": days[now.weekday()],
    }
