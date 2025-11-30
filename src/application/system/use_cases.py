from dataclasses import dataclass
from src.application.system.interfaces import SystemRepository
from src.domain.system.entity import SystemHealth

@dataclass
class GetSystemHealthUseCase:
    """
    Application Service (UseCase) to retrieve system health.
    Orchestrates the flow between Domain and Repository.
    """
    repository: SystemRepository

    async def execute(self) -> SystemHealth:
        return await self.repository.get_system_health()
