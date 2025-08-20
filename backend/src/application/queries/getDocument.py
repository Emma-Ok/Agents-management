from typing import Optional
from src.domain.ports.repositories.documentRepository import DocumentRepository
from src.domain.exceptions.domainExceptions import DocumentNotFoundException
from src.application.dto.documentDto import DocumentResponseDTO
import logging

logger = logging.getLogger(__name__)

class GetDocumentQuery:
    """
    Caso de uso: Obtener el detalle completo de un documento específico
    
    Permite obtener toda la información de un documento incluyendo su metadata
    """
    
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository
    
    async def execute(self, document_id: str) -> DocumentResponseDTO:
        """
        Ejecuta la consulta para obtener un documento
        
        Args:
            document_id: ID del documento a consultar
            
        Returns:
            DocumentResponseDTO con toda la información del documento
            
        Raises:
            DocumentNotFoundException: Si el documento no existe
        """
        logger.info(f"Getting document detail for ID: {document_id}")
        
        # Buscar el documento
        document = await self.document_repository.find_by_id(document_id)
        if not document:
            logger.warning(f"Document not found: {document_id}")
            raise DocumentNotFoundException(document_id)
        
        # Convertir a DTO
        document_dto = DocumentResponseDTO(
            id=document.id,
            agent_id=str(document.agent_id),
            filename=document.filename,
            document_type=document.document_type.value,
            file_url=document.s3_url,
            file_size=document.file_size,
            file_size_mb=document.get_size(),
            created_at=document.created_at
        )
        
        logger.info(f"Document found: {document_id}")
        return document_dto
