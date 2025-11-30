from typing import Protocol
from src.domain.system.entity import SystemHealth

class SystemRepository(Protocol):
    """
    Abstract Interface for System data access.
    Defined in Application layer, implemented in Infrastructure layer.
    """
    async def get_system_health(self) -> SystemHealth:
        ...
