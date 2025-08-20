from typing import List, Optional
from src.domain.ports.repositories.documentRepository import DocumentRepository
from src.domain.ports.repositories.agentRepository import AgentRepository
from src.domain.value_objects.agentId import AgentId
from src.domain.exceptions.domainExceptions import AgentNotFoundException
from src.application.dto.documentDto import DocumentResponseDTO
import logging

logger = logging.getLogger(__name__)

class ListDocumentsQuery:
    """
    Caso de uso: Listar documentos con filtros opcionales
    
    Permite obtener una lista paginada de documentos, opcionalmente filtrada por agente
    """
    
    def __init__(
        self, 
        document_repository: DocumentRepository,
        agent_repository: AgentRepository
    ):
        self.document_repository = document_repository
        self.agent_repository = agent_repository
    
    async def execute(
        self, 
        agent_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None
    ) -> dict:
        """
        Ejecuta la consulta para listar documentos
        
        Args:
            agent_id: ID del agente para filtrar (opcional)
            skip: Número de documentos a omitir (paginación)
            limit: Número máximo de documentos a retornar
            search: Término de búsqueda en filename (opcional)
            
        Returns:
            Dict con la lista de documentos y metadata de paginación
            
        Raises:
            AgentNotFoundException: Si se especifica un agent_id que no existe
        """
        logger.info(f"Listing documents: agent_id={agent_id}, skip={skip}, limit={limit}, search={search}")
        
        # Si se especifica agent_id, validar que el agente existe
        if agent_id:
            agent_id_vo = AgentId(agent_id)
            agent = await self.agent_repository.get_agent_by_id(agent_id_vo)
            if not agent:
                logger.warning(f"Agent not found: {agent_id}")
                raise AgentNotFoundException(agent_id)
            
            # Obtener documentos del agente específico
            documents = await self.document_repository.find_by_agent_id(agent_id_vo)
            
            # Filtrar por término de búsqueda si se proporciona
            if search:
                search_lower = search.lower()
                documents = [
                    doc for doc in documents 
                    if search_lower in doc.filename.lower()
                ]
            
            # Aplicar paginación manual
            total = len(documents)
            documents = documents[skip:skip + limit]
            
        else:
            # Obtener todos los documentos (implementar en el futuro)
            # Por ahora, retornar lista vacía ya que no tenemos un método find_all
            # TODO: Implementar find_all en DocumentRepository
            documents = []
            total = 0
            logger.warning("Listing all documents not implemented yet. Use agent_id filter.")
        
        # Convertir a DTOs
        documents_dto = [
            DocumentResponseDTO(
                id=doc.id,
                agent_id=str(doc.agent_id),
                filename=doc.filename,
                document_type=doc.document_type.value,
                file_url=doc.s3_url,
                file_size=doc.file_size,
                file_size_mb=doc.get_size(),
                created_at=doc.created_at
            )
            for doc in documents
        ]
        
        # Calcular metadata de paginación
        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        has_next = skip + limit < total
        has_previous = skip > 0
        
        result = {
            "documents": documents_dto,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": limit,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_previous": has_previous
            }
        }
        
        logger.info(f"Found {len(documents_dto)} documents (total: {total})")
        return result
