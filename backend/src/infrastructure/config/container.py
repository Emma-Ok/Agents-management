"""
Contenedor de inyección de dependencias usando el patrón Dependency Injection
"""
from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .settings import get_settings
from src.infrastructure.adapters.persistence.mongodb.connection import get_database
from src.infrastructure.adapters.persistence.mongodb.repositories.mongoAgentRepository import MongoAgentRepository
from src.infrastructure.adapters.persistence.mongodb.repositories.mongoDocumentRepository import MongoDocumentRepository
from src.infrastructure.adapters.storage.s3FileStorage import S3FileStorage

from src.domain.ports.repositories.agentRepository import AgentRepository
from src.domain.ports.repositories.documentRepository import DocumentRepository
from src.domain.ports.services.fileStorage import FileStorage

from src.application.commands.createAgent import CreateAgentCommand
from src.application.commands.updateAgent import UpdateAgentCommand
from src.application.commands.deleteAgent import DeleteAgentCommand
from src.application.commands.uploadDocument import UploadDocumentCommand
from src.application.commands.deleteDocument import DeleteDocumentCommand
from src.application.queries.listAgents import ListAgentsQuery
from src.application.queries.getAgentDetail import GetAgentDetailQuery


class Container:
    """Contenedor de dependencias de la aplicación"""
    
    def __init__(self):
        self.settings = get_settings()
        self._database: AsyncIOMotorDatabase = None
        self._agent_repository: AgentRepository = None
        self._document_repository: DocumentRepository = None
        self._file_storage: FileStorage = None
    
    @property
    async def database(self) -> AsyncIOMotorDatabase:
        """Obtiene la instancia de la base de datos MongoDB"""
        if self._database is None:
            self._database = await get_database()
        return self._database
    
    @property
    async def agent_repository(self) -> AgentRepository:
        """Obtiene el repositorio de agentes"""
        if self._agent_repository is None:
            db = await self.database
            self._agent_repository = MongoAgentRepository(db)
        return self._agent_repository
    
    @property
    async def document_repository(self) -> DocumentRepository:
        """Obtiene el repositorio de documentos"""
        if self._document_repository is None:
            db = await self.database
            self._document_repository = MongoDocumentRepository(db)
        return self._document_repository
    
    @property
    def file_storage(self) -> FileStorage:
        """Obtiene el servicio de almacenamiento de archivos"""
        if self._file_storage is None:
            self._file_storage = S3FileStorage(
                bucket_name=self.settings.aws_s3_bucket_name,
                region=self.settings.aws_s3_region,
                access_key_id=self.settings.aws_access_key_id,
                secret_access_key=self.settings.aws_secret_access_key
            )
        return self._file_storage
    
    # Command Handlers
    async def create_agent_command(self) -> CreateAgentCommand:
        """Obtiene el command handler para crear agentes"""
        agent_repo = await self.agent_repository
        return CreateAgentCommand(agent_repo)
    
    async def update_agent_command(self) -> UpdateAgentCommand:
        """Obtiene el command handler para actualizar agentes"""
        agent_repo = await self.agent_repository
        return UpdateAgentCommand(agent_repo)
    
    async def delete_agent_command(self) -> DeleteAgentCommand:
        """Obtiene el command handler para eliminar agentes"""
        agent_repo = await self.agent_repository
        document_repo = await self.document_repository
        file_storage = self.file_storage
        return DeleteAgentCommand(agent_repo, document_repo, file_storage)
    
    async def upload_document_command(self) -> UploadDocumentCommand:
        """Obtiene el command handler para subir documentos"""
        document_repo = await self.document_repository
        agent_repo = await self.agent_repository
        file_storage = self.file_storage
        return UploadDocumentCommand(document_repo, agent_repo, file_storage)
    
    async def delete_document_command(self) -> DeleteDocumentCommand:
        """Obtiene el command handler para eliminar documentos"""
        document_repo = await self.document_repository
        file_storage = self.file_storage
        return DeleteDocumentCommand(document_repo, file_storage)
    
    # Query Handlers
    async def list_agents_query(self) -> ListAgentsQuery:
        """Obtiene el query handler para listar agentes"""
        agent_repo = await self.agent_repository
        document_repo = await self.document_repository
        return ListAgentsQuery(agent_repo, document_repo)
    
    async def get_agent_detail_query(self) -> GetAgentDetailQuery:
        """Obtiene el query handler para obtener detalle de agente"""
        agent_repo = await self.agent_repository
        document_repo = await self.document_repository
        return GetAgentDetailQuery(agent_repo, document_repo)


# Singleton del contenedor
@lru_cache()
def get_container() -> Container:
    """Obtiene la instancia singleton del contenedor"""
    return Container()

