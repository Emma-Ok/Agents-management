from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.agent import Agent
from src.domain.value_objects.agentId import AgentId

class AgentRepository(ABC):
    """
    Puerto de salida para el repositorio de agentes

    Define las operaciones que se pueden realizar sobre los agentes.
    """

    @abstractmethod
    async def save_agent(self, agent: Agent) -> Agent:
        """Agrega un nuevo agente."""
        pass

    @abstractmethod
    async def get_agent_by_id(self, agent_id: AgentId) -> Optional[Agent]:
        """Obtiene un agente por su ID."""
        pass

    @abstractmethod
    async def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Obtiene un agente por su nombre."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 10) -> List[Agent]:
        """Obtiene todos los agentes con paginación"""
        pass

    @abstractmethod
    async def exists(self, agent_id: AgentId) -> bool:
        """Verifica si existe un agente"""
        pass

    @abstractmethod
    async def delete_agent(self, agent_id: AgentId) -> bool:
        """Elimina un agente por su ID."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Cuenta el total de agentes"""
        pass