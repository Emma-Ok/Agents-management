from src.domain.value_objects.agentId import AgentId
from src.domain.ports.repositories.agentRepository import AgentRepository
from src.domain.ports.repositories.documentRepository import DocumentRepository
from src.domain.ports.services.fileStorage import FileStorage
from src.domain.exceptions.domainExceptions import AgentNotFoundException
import logging

logger = logging.getLogger(__name__)

class DeleteAgentCommand:
    """
    Caso de uso #3: Eliminar un agente y todos sus recursos asociados
    
    Este comando implementa la eliminación en cascada:
    1. Elimina todos los archivos de S3
    2. Elimina todos los documentos de la BD
    3. Elimina el agente
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
    
    async def execute(self, agent_id: str) -> bool:
        """
        Ejecuta la eliminación del agente
        
        Returns:
            True si se eliminó correctamente
        """
        logger.info(f"Deleting agent with ID: {agent_id}")
        
        agent_id_vo = AgentId(agent_id)
        
        # Verificar que el agente existe
        agent = await self.agent_repository.get_agent_by_id(agent_id_vo)
        if not agent:
            raise AgentNotFoundException(agent_id)
        
        # Obtener todos los documentos del agente
        documents = await self.document_repository.find_by_agent_id(agent_id_vo)
        
        # Eliminar archivos de S3
        if documents:
            logger.info(f"Deleting {len(documents)} files from storage")
            try:
                # Eliminar carpeta completa del agente
                folder_key = f"agents/{agent_id}/"
                deleted_count = await self.file_storage.delete_folder(folder_key)
                logger.info(f"Deleted {deleted_count} files from storage")
            except Exception as e:
                logger.error(f"Error deleting files from S3: {e}")
                # Continuar con la eliminación de BD aunque S3 falle
                # El admin puede limpiar S3 manualmente después
        else:
            # Si no hay documentos, intentar eliminar la carpeta vacía del agente
            try:
                folder_key = f"agents/{agent_id}/"
                await self.file_storage.delete_folder(folder_key)
                logger.info(f"Deleted empty agent folder: {folder_key}")
            except Exception as e:
                logger.warning(f"Could not delete empty agent folder {folder_key}: {e}")
        
        # Eliminar documentos de la BD
        doc_count = await self.document_repository.delete_by_agent_id(agent_id_vo)
        logger.info(f"Deleted {doc_count} documents from database")
        
        # Eliminar el agente
        result = await self.agent_repository.delete_agent(agent_id_vo)
        
        if result:
            logger.info(f"Agent {agent_id} deleted successfully")
        else:
            logger.error(f"Failed to delete agent {agent_id}")
        
        return result