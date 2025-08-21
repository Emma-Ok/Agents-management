from typing import List
from src.domain.value_objects.agentId import AgentId
from src.domain.ports.repositories.agentRepository import AgentRepository
from src.domain.ports.repositories.documentRepository import DocumentRepository
from src.domain.exceptions.domainExceptions import AgentNotFoundException
from src.application.dto.agentDto import AgentResponseDTO
from src.application.dto.documentDto import DocumentResponseDTO
import logging

logger = logging.getLogger(__name__)

class GetAgentDetailQuery:
    """
    Caso de uso: Obtener el detalle completo de un agente
    
    Incluye la información del agente y todos sus documentos
    """
    
    def __init__(
        self,
        agent_repository: AgentRepository,
        document_repository: DocumentRepository
    ):
        self.agent_repository = agent_repository
        self.document_repository = document_repository
    
    async def execute(self, agent_id: str) -> dict:
        """
        Ejecuta la consulta de detalle
        
        Returns:
            Dict con el agente y sus documentos
        """
        logger.info(f"Getting agent detail for ID: {agent_id}")
        
        agent_id_vo = AgentId(agent_id)
        
        # Obtener el agente
        agent = await self.agent_repository.get_agent_by_id(agent_id_vo)
        if not agent:
            raise AgentNotFoundException(agent_id)
        
        # Obtener documentos del agente
        documents = await self.document_repository.find_by_agent_id(agent_id_vo)
        
        # Convertir agente a DTO
        agent_dto = AgentResponseDTO(
            id=str(agent.id),
            name=agent.name,
            prompt=agent.prompt,
            documents_count=len(documents),
            created_at=agent.created_at,
            updated_at=agent.updated_at
        )
        
        # Convertir documentos a DTOs
        documents_dto = [
            DocumentResponseDTO(
                id=doc.id,
                agent_id=str(doc.agent_id),
                filename=doc.filename,
                document_type=doc.document_type.value,
                file_url=doc.s3_url,
                s3_key=doc.s3_key,
                file_size=doc.file_size,
                file_size_mb=doc.file_size / (1024 * 1024),
                created_at=doc.created_at
            )
            for doc in documents
        ]
        
        return {
            "agent": agent_dto,
            "documents": documents_dto
        }
