"""
Servicio de validación de reglas de negocio para documentos
"""

from typing import List
from src.domain.entities.document import Document
from src.domain.value_objects.agentId import AgentId
from src.domain.ports.repositories.documentRepository import DocumentRepository
from src.domain.exceptions.businessExceptions import (
    AgentHasDocumentsException,
    MaxDocumentsPerAgentExceededException,
    DuplicateDocumentException,
    DocumentSizeExceededException,
    UnsupportedFileTypeException
)
import logging

logger = logging.getLogger(__name__)

class DocumentValidationService:
    """
    Servicio para validar reglas de negocio relacionadas con documentos
    """
    
    # Límites de negocio
    MAX_DOCUMENTS_PER_AGENT = 50
    MAX_FILE_SIZE_MB = 20
    SUPPORTED_FILE_TYPES = ['pdf', 'docx', 'xlsx', 'pptx', 'txt', 'csv']
    
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository
    
    async def validate_document_upload(
        self, 
        agent_id: AgentId, 
        filename: str, 
        file_size: int,
        file_type: str
    ) -> None:
        """
        Valida todas las reglas de negocio antes de subir un documento
        
        Args:
            agent_id: ID del agente
            filename: Nombre del archivo
            file_size: Tamaño del archivo en bytes
            file_type: Tipo/extensión del archivo
            
        Raises:
            MaxDocumentsPerAgentExceededException: Si se excede el límite de documentos
            DuplicateDocumentException: Si ya existe un documento con el mismo nombre
            DocumentSizeExceededException: Si el archivo es demasiado grande
            UnsupportedFileTypeException: Si el tipo de archivo no está soportado
        """
        logger.info(f"Validating document upload for agent {agent_id}: {filename}")
        
        # 1. Validar límite de documentos por agente
        await self._validate_documents_limit(agent_id)
        
        # 2. Validar duplicados
        await self._validate_duplicate_document(agent_id, filename)
        
        # 3. Validar tamaño del archivo
        self._validate_file_size(filename, file_size)
        
        # 4. Validar tipo de archivo
        self._validate_file_type(filename, file_type)
        
        logger.info(f"Document validation passed for {filename}")
    
    async def _validate_documents_limit(self, agent_id: AgentId) -> None:
        """Valida que el agente no exceda el límite de documentos"""
        current_count = await self.document_repository.count_by_agent_id(agent_id)
        
        if current_count >= self.MAX_DOCUMENTS_PER_AGENT:
            logger.warning(
                f"Agent {agent_id} has reached documents limit: "
                f"{current_count}/{self.MAX_DOCUMENTS_PER_AGENT}"
            )
            raise MaxDocumentsPerAgentExceededException(
                str(agent_id), current_count, self.MAX_DOCUMENTS_PER_AGENT
            )
    
    async def _validate_duplicate_document(self, agent_id: AgentId, filename: str) -> None:
        """Valida que no exista un documento con el mismo nombre para el agente"""
        existing_documents = await self.document_repository.find_by_agent_id(agent_id)
        
        for doc in existing_documents:
            if doc.filename.lower() == filename.lower():
                logger.warning(f"Duplicate document found: {filename} for agent {agent_id}")
                raise DuplicateDocumentException(str(agent_id), filename)
    
    def _validate_file_size(self, filename: str, file_size: int) -> None:
        """Valida que el archivo no exceda el tamaño máximo"""
        size_mb = file_size / (1024 * 1024)
        
        if size_mb > self.MAX_FILE_SIZE_MB:
            logger.warning(f"File too large: {filename} ({size_mb:.2f}MB)")
            raise DocumentSizeExceededException(filename, size_mb, self.MAX_FILE_SIZE_MB)
    
    def _validate_file_type(self, filename: str, file_type: str) -> None:
        """Valida que el tipo de archivo esté soportado"""
        # Limpiar el tipo de archivo (remover punto si existe)
        clean_type = file_type.lower().lstrip('.')
        
        if clean_type not in self.SUPPORTED_FILE_TYPES:
            logger.warning(f"Unsupported file type: {file_type} for {filename}")
            raise UnsupportedFileTypeException(filename, file_type, self.SUPPORTED_FILE_TYPES)
    
    async def validate_agent_deletion(self, agent_id: AgentId) -> None:
        """
        Valida que se pueda eliminar un agente
        
        Args:
            agent_id: ID del agente a eliminar
            
        Raises:
            AgentHasDocumentsException: Si el agente tiene documentos asociados
        """
        documents_count = await self.document_repository.count_by_agent_id(agent_id)
        
        if documents_count > 0:
            logger.warning(f"Cannot delete agent {agent_id}: has {documents_count} documents")
            raise AgentHasDocumentsException(str(agent_id), documents_count)
    
    def get_file_type_from_filename(self, filename: str) -> str:
        """Extrae el tipo de archivo del nombre del archivo"""
        if '.' not in filename:
            return ''
        return filename.split('.')[-1].lower()
    
    def format_file_size(self, size_bytes: int) -> str:
        """Formatea el tamaño del archivo para mostrar"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
