from dataclasses import dataclass
from datetime import datetime
from typing import BinaryIO

@dataclass
class UploadDocumentDTO:
    """
    Data Transfer Object para la subida de un documento
    """
    agent_id: str
    filename: str
    file: BinaryIO
    content_type: str
    file_size: int

@dataclass
class DocumentResponseDTO:
    """DTO de respuesta para un documento"""
    id: str
    agent_id: str
    filename: str
    document_type: str
    file_url: str
    file_size: int
    file_size_mb: float
    created_at: datetime