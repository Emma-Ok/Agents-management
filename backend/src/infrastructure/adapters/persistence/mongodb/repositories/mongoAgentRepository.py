from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.domain.entities.agent import Agent
from src.domain.value_objects.agentId import AgentId
from src.domain.ports.repositories.agentRepository import AgentRepository   

import logging

logger = logging.getLogger(__name__)

class MongoAgentRepository(AgentRepository):
    """
    Implementación MongoDB del repositorio de agentes
    
    Adapta la interfaz del dominio a las operaciones específicas de MongoDB
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["agents"]
    
    def _to_domain(self, model: dict) -> Agent:
        """Convierte un documento MongoDB a entidad del dominio"""
        return Agent(
            id=AgentId(model["_id"]),
            name=model["name"],
            prompt=model["prompt"],
            documents_count=model.get("document_count", 0),
            created_at=model["created_at"],
            updated_at=model["updated_at"]
        )
    
    def _to_model(self, entity: Agent) -> dict:
        """Convierte una entidad del dominio a documento MongoDB"""
        return {
            "_id": str(entity.id),
            "name": entity.name,
            "prompt": entity.prompt,
            "documents_count": entity.documents_count,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at
        }
    
    async def save_agent(self, agent: Agent) -> Agent:
        """Guarda o actualiza un agente"""
        model = self._to_model(agent)
        
        # Upsert: actualiza si existe, inserta si no
        result = await self.collection.replace_one(
            {"_id": model["_id"]},
            model,
            upsert=True
        )
        
        logger.debug(f"Agent saved: {agent.id}, modified: {result.modified_count}")
        return agent
    
    async def get_agent_by_id(self, agent_id: AgentId) -> Optional[Agent]:
        """Busca un agente por ID"""
        document = await self.collection.find_one({"_id": str(agent_id)})
        
        if document:
            return self._to_domain(document)
        return None
    
    async def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Busca un agente por nombre"""
        document = await self.collection.find_one({"name": name})
        
        if document:
            return self._to_domain(document)
        return None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Obtiene todos los agentes con paginación"""
        cursor = self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
        
        agents = []
        async for document in cursor:
            agents.append(self._to_domain(document))
        
        return agents
    
    async def delete_agent(self, agent_id: AgentId) -> bool:
        """Elimina un agente"""
        result = await self.collection.delete_one({"_id": str(agent_id)})
        return result.deleted_count > 0
    
    async def exists(self, agent_id: AgentId) -> bool:
        """Verifica si existe un agente"""
        count = await self.collection.count_documents(
            {"_id": str(agent_id)},
            limit=1
        )
        return count > 0
    
    async def count(self) -> int:
        """Cuenta el total de agentes"""
        return await self.collection.count_documents({})
