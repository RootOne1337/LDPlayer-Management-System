"""
Server uptime tracking module.

Provides functionality to track server start time and calculate uptime.
"""

import time
from datetime import datetime, timedelta
from typing import Optional


class UptimeTracker:
    """Tracks server uptime since startup."""
    
    def __init__(self):
        self._start_time: Optional[float] = None
        self._start_datetime: Optional[datetime] = None
    
    def start(self) -> None:
        """Mark the server as started."""
        self._start_time = time.time()
        self._start_datetime = datetime.now()
    
    def get_uptime_seconds(self) -> int:
        """
        Get uptime in seconds since server started.
        
        Returns:
            Uptime in seconds, or 0 if server hasn't started yet
        """
        if self._start_time is None:
            return 0
        return int(time.time() - self._start_time)
    
    def get_uptime_formatted(self) -> str:
        """
        Get uptime formatted as HH:MM:SS.
        
        Returns:
            Formatted uptime string like "01:23:45"
        """
        if self._start_time is None:
            return "0:00:00"
        
        uptime_seconds = self.get_uptime_seconds()
        
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        elif minutes > 0:
            return f"0:{minutes:02d}:{seconds:02d}"
        else:
            return f"0:00:{seconds:02d}"
    
    def get_uptime_timedelta(self) -> timedelta:
        """
        Get uptime as a timedelta object.
        
        Returns:
            Timedelta representing uptime duration
        """
        return timedelta(seconds=self.get_uptime_seconds())
    
    def get_start_datetime(self) -> Optional[datetime]:
        """
        Get the exact datetime when server started.
        
        Returns:
            datetime of server start, or None if not started
        """
        return self._start_datetime
    
    def is_running(self) -> bool:
        """Check if server has been started."""
        return self._start_time is not None
    
    def reset(self) -> None:
        """Reset uptime tracker (mainly for testing)."""
        self._start_time = None
        self._start_datetime = None


# Global instance
_uptime_tracker = UptimeTracker()


def start_uptime_tracking() -> None:
    """Start tracking server uptime."""
    _uptime_tracker.start()


def get_uptime_seconds() -> int:
    """Get current uptime in seconds."""
    return _uptime_tracker.get_uptime_seconds()


def get_uptime_formatted() -> str:
    """Get current uptime formatted as HH:MM:SS."""
    return _uptime_tracker.get_uptime_formatted()


def get_uptime_timedelta() -> timedelta:
    """Get current uptime as timedelta."""
    return _uptime_tracker.get_uptime_timedelta()


def get_server_start_time() -> Optional[datetime]:
    """Get server start datetime."""
    return _uptime_tracker.get_start_datetime()


def is_server_running() -> bool:
    """Check if server has started."""
    return _uptime_tracker.is_running()


def reset_uptime_tracker() -> None:
    """Reset uptime tracker (for testing)."""
    _uptime_tracker.reset()


# Example usage in health check:
# from src.core.uptime import get_uptime_formatted
# uptime = get_uptime_formatted()  # Returns "01:23:45"
