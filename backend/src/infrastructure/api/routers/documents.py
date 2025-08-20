from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional
import os
from src.application.commands.uploadDocument import UploadDocumentCommand
from src.application.commands.deleteDocument import DeleteDocumentCommand
from src.application.dto.documentDto import UploadDocumentDTO
from src.domain.value_objects.documentType import DocumentType
from src.domain.exceptions.domainExceptions import InvalidFileTypeException
from src.infrastructure.api.dependencies import (
    get_upload_document_command,
    get_delete_document_command
)
from src.infrastructure.config.settings import get_settings

router = APIRouter(prefix="/documents", tags=["documents"])

settings = get_settings()

@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    description="Upload a document for a specific agent"
)
async def upload_document(
    agent_id: str = Form(..., description="ID of the agent"),
    file: UploadFile = File(..., description="Document to upload"),
    command: UploadDocumentCommand = Depends(get_upload_document_command)
):
    """
    Upload a document for an agent.
    
    Supported formats: PDF, DOCX, XLSX, PPTX
    Maximum file size: 10MB
    """
    # Validar extensión
    extension = os.path.splitext(file.filename)[1]
    if not DocumentType.is_valid_extension(extension):
        raise InvalidFileTypeException(extension)
    
    # Validar tamaño
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > settings.max_file_size_bytes:
        raise InvalidFileTypeException(f"File too large: {file_size} bytes")
    
    # Resetear el archivo para lectura
    await file.seek(0)
    
    dto = UploadDocumentDTO(
        agent_id=agent_id,
        filename=file.filename,
        file=file.file,
        content_type=file.content_type or "application/octet-stream",
        file_size=file_size
    )
    
    result = await command.execute(dto)
    return result

@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
    description="Delete a specific document"
)
async def delete_document(
    document_id: str,
    command: DeleteDocumentCommand = Depends(get_delete_document_command)
):
    """
    Delete a document.
    
    This will remove the document from both the database and S3 storage.
    """
    await command.execute(document_id)
    return None