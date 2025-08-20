from abc import ABC, abstractmethod
from typing import List, Optional
from ...entities.document import Document
from ...value_objects.agentId import AgentId

class DocumentRepository(ABC):
    """
    Puerto de salida para el repositorio de documentos

    Define las operaciones que se pueden realizar sobre los documentos.
    """

    @abstractmethod
    async def save_document(self, document: Document) -> None:
        """Agrega un nuevo documento."""
        pass

    @abstractmethod
    async def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """Obtiene un documento por su ID."""
        pass

    @abstractmethod
    async def get_all_documents(self, skip: int = 0, limit: int = 10) -> List[Document]:
        """Obtiene todos los documentos con paginación."""
        pass

    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Elimina un documento por su ID."""
        pass

    @abstractmethod
    async def delete_by_agent_id(self, agent_id: AgentId) -> int:
        """Elimina todos los documentos de un agente. Retorna cantidad eliminada"""
        pass

    @abstractmethod
    async def count_documents(self) -> int:
        """Cuenta el total de documentos."""
        pass

    @abstractmethod
    async def find_by_agent_id(self, agent_id: AgentId) -> List[Document]:
        """Obtiene todos los documentos de un agente"""
        pass

    @abstractmethod
    async def exists(self, document_id: str) -> bool:
        """Verifica si existe un documento"""
        pass