from src.domain.value_objects.agentId import AgentId
from src.domain.ports.repositories.agentRepository import AgentRepository
from src.domain.ports.repositories.documentRepository import DocumentRepository
from src.domain.ports.services.fileStorage import FileStorage
from src.domain.exceptions.domainExceptions import DocumentNotFoundException, AgentNotFoundException
import logging

logger = logging.getLogger(__name__)

class DeleteDocumentCommand:
    """
    Caso de uso: Eliminar un documento específico
    
    Elimina el archivo de S3 y el registro de la BD
    """
    
    def __init__(
        self,
        agent_repository: AgentRepository,
        document_repository: DocumentRepository,
        file_storage: FileStorage
    ):
        self.agent_repository = agent_repository
        self.document_repository = document_repository
        self.file_storage = file_storage
    
    async def execute(self, document_id: str) -> bool:
        """
        Ejecuta la eliminación del documento
        
        1. Busca el documento
        2. Elimina el archivo de S3
        3. Elimina el registro de BD
        4. Actualiza el contador del agente
        """
        logger.info(f"Deleting document with ID: {document_id}")
        
        # Buscar el documento
        document = await self.document_repository.find_by_id(document_id)
        if not document:
            raise DocumentNotFoundException(document_id)
        
        # Buscar el agente para actualizar el contador
        agent = await self.agent_repository.get_agent_by_id(document.agent_id)
        if not agent:
            raise AgentNotFoundException(str(document.agent_id))
        
        # Eliminar archivo de S3
        try:
            await self.file_storage.delete_file(document.s3_key)
            logger.info(f"File {document.s3_key} deleted from storage")
        except Exception as e:
            logger.error(f"Error deleting file from storage: {e}")
            # Continuar con la eliminación del registro
        
        # Eliminar registro de BD
        result = await self.document_repository.delete(document_id)
        
        if result:
            # Actualizar contador del agente
            agent.documents_count = max(0, agent.documents_count - 1)
            await self.agent_repository.save_agent(agent)
            logger.info(f"Document {document_id} deleted successfully")
        
        return result