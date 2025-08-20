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
import logging  

logger = logging.getLogger(__name__)

async def domain_exception_handler(request: Request, exc: DomainException):
    """
    Manejador global de excepciones del dominio
    
    Convierte las excepciones del dominio en respuestas HTTP apropiadas
    """
    
    # Mapeo de excepciones a códigos HTTP
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = str(exc)
    error_type = exc.__class__.__name__
    
    if isinstance(exc, AgentNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, DocumentNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, DuplicateAgentNameException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, InvalidFileTypeException):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, FileSizeExceededException):
        status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    elif isinstance(exc, StorageException):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        detail = "Storage service temporarily unavailable"
    
    logger.error(f"Domain exception: {error_type} - {detail}")
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": error_type,
                "message": detail,
                "path": str(request.url)
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejador de errores de validación"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"][1:]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "ValidationError",
                "message": "Invalid request data",
                "details": errors,
                "path": str(request.url)
            }
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejador de excepciones HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "message": exc.detail,
                "path": str(request.url)
            }
        }
    )