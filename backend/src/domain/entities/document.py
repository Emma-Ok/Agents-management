from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid
from ..value_objects.agentId import AgentId
from ..value_objects.documentType import DocumentType

@dataclass
class Document:
    """
    Entidad Documento - Representa un documento asociado a un agente
    """
    id: str
    agent_id: AgentId
    filename: str
    document_type: DocumentType
    s3_url: str
    s3_key: str
    file_size: int
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        self._validate_filename()
        self._validate_file_size()

    def _validate_filename(self):
        """Valida que el nombre del archivo no esté vacío."""
        if not self.filename or not isinstance(self.filename, str):
            raise ValueError("File name cannot be empty and must be a string.")
        if len(self.filename) > 100:
            raise ValueError("File name must be at most 100 characters long.")
        self.filename = self.filename.strip()

    def _validate_file_size(self):
        """Valida que el tamaño del archivo sea positivo y <= 20MB."""
        MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
        if not isinstance(self.file_size, int) or self.file_size <= 0:
            raise ValueError("File size must be a positive integer.")
        if self.file_size > MAX_FILE_SIZE:
            raise ValueError(f"File size must not exceed {MAX_FILE_SIZE} bytes.")

    @classmethod
    def create(cls, agent_id: AgentId, filename: str, document_type: DocumentType, s3_url: str, s3_key: str, file_size: int) -> "Document":
        """Crea una nueva instancia de Document."""
        now = datetime.now()
        return cls(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            filename=filename,
            document_type=document_type,
            s3_url=s3_url,
            s3_key=s3_key,
            file_size=file_size,
            created_at=now,
            updated_at=now
        )

    def get_extension(self) -> str:
        """Obtiene la extensión del archivo."""
        return self.document_type.value

    def get_size(self) -> float:
        """Obtiene el tamaño del archivo en MB."""
        return round(self.file_size / (1024 * 1024), 2)
