from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse, RedirectResponse
from typing import Optional, List
import os
import logging
from src.application.commands.uploadDocument import UploadDocumentCommand
from src.application.commands.deleteDocument import DeleteDocumentCommand
from src.application.queries.getDocument import GetDocumentQuery
from src.application.queries.listDocuments import ListDocumentsQuery
from src.application.dto.documentDto import UploadDocumentDTO
from src.domain.value_objects.documentType import DocumentType
from src.domain.exceptions.domainExceptions import InvalidFileTypeException, DocumentNotFoundException, AgentNotFoundException
from src.infrastructure.api.dependencies import (
    get_upload_document_command,
    get_delete_document_command,
    get_document_query,
    get_list_documents_query
)
from src.infrastructure.config.container import get_container
from src.infrastructure.config.settings import get_settings
from src.shared.utils.validators import FileValidator, DocumentValidator
from src.shared.utils.formatter import ResponseFormatter, FileFormatter

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)
settings = get_settings()

@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document to an agent",
    description="Upload a document (PDF, DOCX, XLSX, PPTX, TXT, CSV) for a specific agent"
)
async def upload_document(
    agent_id: str = Form(..., description="ID of the agent"),
    file: UploadFile = File(..., description="Document file to upload"),
    description: Optional[str] = Form(None, description="Optional description for the document"),
    command: UploadDocumentCommand = Depends(get_upload_document_command)
):
    """
    Upload a document for an agent.
    
    **Supported formats:** PDF, DOCX, XLSX, PPTX, TXT, CSV
    **Maximum file size:** 10MB
    
    **Process:**
    1. Validates file type and size
    2. Uploads to S3 storage
    3. Saves metadata to MongoDB
    4. Returns document information with URLs
    """
    try:
        logger.info(f"Starting document upload for agent {agent_id}: {file.filename}")
        
        # 1. Validar Agent ID
        is_valid, error_msg = DocumentValidator.validate_agent_id(agent_id)
        if not is_valid:
            logger.warning(f"Invalid agent ID: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ResponseFormatter.error_response(
                    error_message=error_msg,
                    error_code="INVALID_AGENT_ID"
                )
            )
        
        # 2. Validar archivo
        is_valid, file_type, error_msg = FileValidator.validate_file(
            file=file,
            max_size_mb=settings.max_file_size_mb,
            allowed_extensions=settings.allowed_extensions
        )
        
        if not is_valid:
            logger.warning(f"File validation failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ResponseFormatter.error_response(
                    error_message=error_msg,
                    error_code="INVALID_FILE",
                    details={
                        "filename": file.filename,
                        "content_type": file.content_type,
                        "max_size_mb": settings.max_file_size_mb,
                        "allowed_extensions": settings.allowed_extensions
                    }
                )
            )
        
        # 3. Leer contenido del archivo para validaciones adicionales
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validar contenido si es posible
        content_valid, content_error = FileValidator.validate_file_content(file_content, file.filename)
        if not content_valid:
            logger.warning(f"File content validation failed: {content_error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ResponseFormatter.error_response(
                    error_message=content_error,
                    error_code="INVALID_FILE_CONTENT"
                )
            )
        
        # 4. Resetear el archivo para lectura en el comando
        await file.seek(0)
        
        # 5. Preparar metadata adicional
        metadata = {
            "description": description or "",
            "original_size": file_size,
            "content_type": file.content_type or "application/octet-stream"
        }
        
        # Validar metadata
        metadata_valid, metadata_error = DocumentValidator.validate_document_metadata(metadata)
        if not metadata_valid:
            logger.warning(f"Metadata validation failed: {metadata_error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ResponseFormatter.error_response(
                    error_message=metadata_error,
                    error_code="INVALID_METADATA"
                )
            )
        
        # 6. Crear DTO para el comando
        dto = UploadDocumentDTO(
            agent_id=agent_id,
            filename=file.filename,
            file=file.file,
            content_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            metadata=metadata
        )
        
        # 7. Ejecutar comando de upload
        logger.info(f"Executing upload command for {file.filename}")
        result = await command.execute(dto)
        
        # 8. Formatear respuesta exitosa
        file_info = FileFormatter.extract_file_info(
            filename=file.filename,
            file_size=file_size,
            content_type=file.content_type or "application/octet-stream"
        )
        
        response_data = {
            "document": result,
            "file_info": file_info,
            "upload_status": "completed"
        }
        
        logger.info(f"Document uploaded successfully: {result.id}")
        return ResponseFormatter.success_response(
            data=response_data,
            message=f"Documento '{file.filename}' subido exitosamente"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except AgentNotFoundException as e:
        logger.error(f"Agent not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseFormatter.error_response(
                error_message=str(e),
                error_code="AGENT_NOT_FOUND"
            )
        )
    except InvalidFileTypeException as e:
        logger.error(f"Invalid file type: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseFormatter.error_response(
                error_message=str(e),
                error_code="INVALID_FILE_TYPE"
            )
        )
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseFormatter.error_response(
                error_message="Error interno del servidor durante la subida",
                error_code="UPLOAD_ERROR",
                details={"error": str(e)}
            )
        )

@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a document",
    description="Delete a specific document from storage and database"
)
async def delete_document(
    document_id: str,
    command: DeleteDocumentCommand = Depends(get_delete_document_command)
):
    """
    Delete a document.
    
    **Process:**
    1. Validates document exists
    2. Removes file from S3 storage
    3. Removes metadata from MongoDB
    
    Returns confirmation of deletion.
    """
    try:
        logger.info(f"Starting document deletion: {document_id}")
        
        # Ejecutar comando de eliminación
        success = await command.execute(document_id)
        
        if success:
            logger.info(f"Document deleted successfully: {document_id}")
            return ResponseFormatter.success_response(
                data={"document_id": document_id, "deleted": True},
                message="Documento eliminado exitosamente"
            )
        else:
            logger.warning(f"Document deletion failed: {document_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ResponseFormatter.error_response(
                    error_message="No se pudo eliminar el documento",
                    error_code="DELETION_FAILED"
                )
            )
            
    except DocumentNotFoundException as e:
        logger.error(f"Document not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseFormatter.error_response(
                error_message=str(e),
                error_code="DOCUMENT_NOT_FOUND"
            )
        )
    except Exception as e:
        logger.error(f"Unexpected error during deletion: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseFormatter.error_response(
                error_message="Error interno del servidor durante la eliminación",
                error_code="DELETION_ERROR",
                details={"error": str(e)}
            )
        )

@router.get(
    "/{document_id}",
    summary="Get document information",
    description="Get detailed information about a specific document"
)
async def get_document_info(
    document_id: str,
    query: GetDocumentQuery = Depends(get_document_query)
):
    """
    Get detailed information about a document.
    
    Returns document metadata, S3 URL, and other relevant information.
    """
    try:
        logger.info(f"Getting document info: {document_id}")
        
        # Ejecutar query para obtener documento
        document = await query.execute(document_id)
        
        return ResponseFormatter.success_response(
            data={"document": document},
            message="Información del documento obtenida exitosamente"
        )
        
    except DocumentNotFoundException as e:
        logger.error(f"Document not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseFormatter.error_response(
                error_message=str(e),
                error_code="DOCUMENT_NOT_FOUND"
            )
        )
    except Exception as e:
        logger.error(f"Unexpected error getting document info: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseFormatter.error_response(
                error_message="Error interno del servidor",
                error_code="GET_DOCUMENT_ERROR",
                details={"error": str(e)}
            )
        )

@router.get(
    "/{document_id}/download",
    summary="Download document",
    description="Generate a presigned URL to download the document file"
)
async def download_document(
    document_id: str,
    query: GetDocumentQuery = Depends(get_document_query)
):
    """
    Download a document file.
    
    **Process:**
    1. Validates document exists
    2. Generates presigned URL for secure download
    3. Redirects to download URL
    
    Returns a redirect to the secure download URL.
    """
    try:
        logger.info(f"Starting document download: {document_id}")
        
        # Obtener información del documento
        document = await query.execute(document_id)
        
        # Obtener servicio de almacenamiento desde el container
        container = get_container()
        file_storage = container.file_storage
        
        # Usar la clave S3 directamente del documento
        s3_key = document.s3_key
        
        # Generar URL presignada (válida por 1 hora)
        presigned_url = await file_storage.generate_presigned_url(s3_key, expiration=3600)
        
        logger.info(f"Generated presigned URL for document: {document_id}")
        
        # Redirigir directamente a la URL de descarga
        return RedirectResponse(url=presigned_url, status_code=307)
        
    except DocumentNotFoundException as e:
        logger.error(f"Document not found for download: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseFormatter.error_response(
                error_message=str(e),
                error_code="DOCUMENT_NOT_FOUND"
            )
        )
    except Exception as e:
        logger.error(f"Unexpected error during download: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseFormatter.error_response(
                error_message="Error interno del servidor durante la descarga",
                error_code="DOWNLOAD_ERROR",
                details={"error": str(e)}
            )
        )

@router.get(
    "/",
    summary="List documents",
    description="List all documents with optional filtering"
)
async def list_documents(
    agent_id: Optional[str] = Query(None, description="Filter by specific agent"),
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of documents to return"),
    search: Optional[str] = Query(None, description="Search term for filename"),
    query: ListDocumentsQuery = Depends(get_list_documents_query)
):
    """
    List documents with optional filtering by agent.
    
    **Parameters:**
    - agent_id: Filter by specific agent (optional)
    - skip: Number of documents to skip (pagination)
    - limit: Maximum number of documents to return
    - search: Search term for filename (optional)
    """
    try:
        logger.info(f"Listing documents: agent_id={agent_id}, skip={skip}, limit={limit}, search={search}")
        
        # Ejecutar query para listar documentos
        result = await query.execute(
            agent_id=agent_id,
            skip=skip,
            limit=limit,
            search=search
        )
        
        return ResponseFormatter.success_response(
            data=result,
            message="Lista de documentos obtenida exitosamente"
        )
        
    except AgentNotFoundException as e:
        logger.error(f"Agent not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ResponseFormatter.error_response(
                error_message=str(e),
                error_code="AGENT_NOT_FOUND"
            )
        )
    except Exception as e:
        logger.error(f"Unexpected error listing documents: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseFormatter.error_response(
                error_message="Error interno del servidor",
                error_code="LIST_DOCUMENTS_ERROR",
                details={"error": str(e)}
            )
        )