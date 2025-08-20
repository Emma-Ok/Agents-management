from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.domain.entities.document import Document
from src.domain.value_objects.agentId import AgentId
from src.domain.value_objects.documentType import DocumentType
from src.domain.ports.repositories.documentRepository import DocumentRepository
import logging

logger = logging.getLogger(__name__)

class MongoDocumentRepository(DocumentRepository):
    """
    Implementación MongoDB del repositorio de documentos
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        if database is None:
            raise Exception("Database cannot be None - MongoDB connection failed")
        self.collection = database["documents"]
    
    def _to_domain(self, model: dict) -> Document:
        """Convierte un documento MongoDB a entidad del dominio"""
        return Document(
            id=model["_id"],
            agent_id=AgentId(model["agent_id"]),
            filename=model["filename"],
            document_type=DocumentType(model["document_type"]),
            s3_url=model["s3_url"],
            s3_key=model["s3_key"],
            file_size=model["file_size"],
            created_at=model["created_at"],
            updated_at=model["updated_at"]
        )
    
    def _to_model(self, entity: Document) -> dict:
        """Convierte una entidad del dominio a documento MongoDB"""
        return {
            "_id": entity.id,
            "agent_id": str(entity.agent_id),
            "filename": entity.filename,
            "document_type": entity.document_type.value,
            "s3_url": entity.s3_url,
            "s3_key": entity.s3_key,
            "file_size": entity.file_size,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at
        }
    
    async def save(self, document: Document) -> Document:
        """Guarda un documento"""
        model = self._to_model(document)
        
        result = await self.collection.replace_one(
            {"_id": model["_id"]},
            model,
            upsert=True
        )
        
        logger.debug(f"Document saved: {document.id}")
        return document
    
    async def find_by_id(self, document_id: str) -> Optional[Document]:
        """Busca un documento por ID"""
        doc = await self.collection.find_one({"_id": document_id})
        
        if doc:
            return self._to_domain(doc)
        return None
    
    async def find_by_agent_id(self, agent_id: AgentId) -> List[Document]:
        """Obtiene todos los documentos de un agente"""
        cursor = self.collection.find(
            {"agent_id": str(agent_id)}
        ).sort("created_at", -1)
        
        documents = []
        async for doc in cursor:
            documents.append(self._to_domain(doc))
        
        return documents
    
    async def delete(self, document_id: str) -> bool:
        """Elimina un documento"""
        result = await self.collection.delete_one({"_id": document_id})
        return result.deleted_count > 0
    
    async def delete_by_agent_id(self, agent_id: AgentId) -> int:
        """Elimina todos los documentos de un agente"""
        result = await self.collection.delete_many({"agent_id": str(agent_id)})
        return result.deleted_count
    
    async def count_by_agent_id(self, agent_id: AgentId) -> int:
        """Cuenta los documentos de un agente"""
        return await self.collection.count_documents({"agent_id": str(agent_id)})
    
    async def exists(self, document_id: str) -> bool:
        """Verifica si existe un documento"""
        count = await self.collection.count_documents(
            {"_id": document_id},
            limit=1
        )
        return count > 0
