from typing import List, Optional
from src.domain.ports.repositories.agentRepository import AgentRepository
from ..dto.agentDto import AgentListItemDTO
import logging

logger = logging.getLogger(__name__)

class ListAgentsQuery:
    """
    Caso de uso: Listar todos los agentes con paginación
    
    Query optimizada para mostrar la lista de agentes
    con información resumida
    """
    
    def __init__(self, agent_repository: AgentRepository):
        self.agent_repository = agent_repository
    
    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None
    ) -> dict:
        """
        Ejecuta la consulta de agentes
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            search: Término de búsqueda opcional
        
        Returns:
            Dict con los agentes y metadata de paginación
        """
        logger.info(f"Listing agents: skip={skip}, limit={limit}, search={search}")
        
        # Obtener agentes
        agents = await self.agent_repository.get_all(skip=skip, limit=limit)
        
        # Obtener total para paginación
        total = await self.agent_repository.count()
        
        # Convertir a DTOs
        items = [
            AgentListItemDTO(
                id=str(agent.id),
                documents_count=agent.documents_count,
                created_at=agent.created_at
            )
            for agent in agents
        ]
        
        # Calcular metadata de paginación
        has_more = (skip + limit) < total
        next_skip = skip + limit if has_more else None
        
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": has_more,
            "next_skip": next_skip
        }