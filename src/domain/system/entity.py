from dataclasses import dataclass
from datetime import datetime

@dataclass
class SystemHealth:
    """
    Domain Entity representing the system's health status.
    Pure Python, no libraries.
    """
    database_time: datetime
    status: str = "ok"
