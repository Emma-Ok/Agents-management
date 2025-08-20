from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from src.domain.exceptions.domainExceptions import (
    DomainException,
    AgentNotFoundException,
    DocumentNotFoundException,
    InvalidFileTypeException,
    FileSizeExceededException,
    DuplicateAgentNameException,
    StorageException
)
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)

def create_error_response(error_type: str, message: str, status_code: int, details: dict = None, path: str = None):
    """Crea una respuesta de error estandarizada con formato consistente"""
    error_content = {
        "success": False,
        "error": {
            "type": error_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "status_code": status_code
        }
    }
    
    if details:
        error_content["error"]["details"] = details
    
    if path:
        error_content["error"]["path"] = path
    
    return JSONResponse(
        status_code=status_code,
        content=error_content
    )

async def domain_exception_handler(request: Request, exc: DomainException):
    """
    Manejador global mejorado de excepciones del dominio
    
    Convierte las excepciones del dominio en respuestas HTTP apropiadas
    con mensajes claros y códigos de estado correctos
    """
    
    error_type = exc.__class__.__name__
    path = str(request.url)
    
    logger.error(f"Domain exception: {error_type} - {str(exc)}")
    
    # Mapeo específico de excepciones con mensajes claros
    if isinstance(exc, AgentNotFoundException):
        return create_error_response(
            error_type="AGENT_NOT_FOUND",
            message=f"El agente solicitado no existe: {str(exc)}",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": "agent", "action": "Verifica el ID del agente"},
            path=path
        )
    
    elif isinstance(exc, DocumentNotFoundException):
        return create_error_response(
            error_type="DOCUMENT_NOT_FOUND", 
            message=f"El documento solicitado no existe: {str(exc)}",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": "document", "action": "Verifica el ID del documento"},
            path=path
        )
    
    elif isinstance(exc, DuplicateAgentNameException):
        return create_error_response(
            error_type="DUPLICATE_AGENT_NAME",
            message=f"Ya existe un agente con este nombre: {str(exc)}",
            status_code=status.HTTP_409_CONFLICT,
            details={"resource": "agent", "field": "name", "action": "Usa un nombre diferente"},
            path=path
        )
    
    elif isinstance(exc, InvalidFileTypeException):
        return create_error_response(
            error_type="INVALID_FILE_TYPE",
            message=f"Tipo de archivo no soportado: {str(exc)}",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            details={
                "resource": "file", 
                "supported_types": ["pdf", "docx", "xlsx", "pptx", "txt", "csv"],
                "action": "Selecciona un archivo con formato válido"
            },
            path=path
        )
    
    elif isinstance(exc, FileSizeExceededException):
        return create_error_response(
            error_type="FILE_SIZE_EXCEEDED",
            message=f"El archivo excede el tamaño máximo permitido: {str(exc)}",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            details={"resource": "file", "limit": "10MB", "action": "Reduce el tamaño del archivo"},
            path=path
        )
    
    elif isinstance(exc, StorageException):
        return create_error_response(
            error_type="STORAGE_ERROR",
            message="Servicio de almacenamiento temporalmente no disponible. Inténtalo de nuevo en unos minutos.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"service": "storage", "action": "Reintentar en unos minutos"},
            path=path
        )
    
    # Excepción genérica del dominio
    logger.warning(f"Unhandled domain exception: {error_type}")
    return create_error_response(
        error_type="DOMAIN_ERROR",
        message=f"Error de dominio: {str(exc)}",
        status_code=status.HTTP_400_BAD_REQUEST,
        details={"action": "Verifica los datos enviados"},
        path=path
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejador mejorado de errores de validación"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:]) if len(error["loc"]) > 1 else "body"
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input", "N/A")
        })
    
    logger.warning(f"Validation error on {request.url}: {errors}")
    
    return create_error_response(
        error_type="VALIDATION_ERROR",
        message="Los datos enviados no son válidos. Verifica los campos marcados.",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={
            "errors": errors,
            "action": "Corrige los campos indicados y vuelve a intentar"
        },
        path=str(request.url)
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejador mejorado de excepciones HTTP"""
    logger.warning(f"HTTP exception on {request.url}: {exc.status_code} - {exc.detail}")
    
    # Mensajes más amigables para códigos comunes
    user_message = exc.detail
    action = "Inténtalo de nuevo"
    
    if exc.status_code == 404:
        user_message = "El recurso solicitado no se encontró"
        action = "Verifica la URL e inténtalo de nuevo"
    elif exc.status_code == 405:
        user_message = "Método no permitido para este endpoint"
        action = "Verifica el método HTTP utilizado"
    elif exc.status_code == 500:
        user_message = "Error interno del servidor"
        action = "Inténtalo de nuevo en unos minutos"
    
    return create_error_response(
        error_type="HTTP_ERROR",
        message=user_message,
        status_code=exc.status_code,
        details={"action": action},
        path=str(request.url)
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Manejador para excepciones no capturadas"""
    logger.error(f"Unhandled exception on {request.url}: {exc.__class__.__name__} - {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Manejo específico de errores SSL
    if "SSL" in str(exc) or "EOF occurred in violation of protocol" in str(exc):
        return create_error_response(
            error_type="SSL_CONNECTION_ERROR",
            message="Error de conexión SSL con el servicio de almacenamiento",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={
                "error": "Problema de conectividad con AWS S3",
                "action": "Inténtalo de nuevo en unos minutos. Si persiste, contacta al administrador."
            },
            path=str(request.url)
        )
    
    # Manejo específico de errores de carga de archivos
    if "upload" in str(request.url).lower():
        return create_error_response(
            error_type="UPLOAD_ERROR",
            message="Error durante la subida del archivo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={
                "error": str(exc) if len(str(exc)) < 200 else "Error interno del servidor durante la subida",
                "action": "Verifica el archivo y vuelve a intentar. Si persiste, usa un archivo diferente."
            },
            path=str(request.url)
        )
    
    return create_error_response(
        error_type="INTERNAL_ERROR",
        message="Ha ocurrido un error interno. Nuestro equipo ha sido notificado.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"action": "Inténtalo de nuevo en unos minutos"},
        path=str(request.url)
    )