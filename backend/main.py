from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))	
from src.infrastructure.config.settings import get_settings
from src.infrastructure.adapters.persistence.mongodb.connection import get_mongodb
from src.infrastructure.api.middleware.errorHandler import (
    domain_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler
)
from src.infrastructure.api.routers import agents, documents
from src.domain.exceptions.domainExceptions import DomainException

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Inicializar MongoDB y crear índices
    try:
        mongodb = await get_mongodb()
        await mongodb.create_indexes()
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # No raise para permitir que la app inicie sin MongoDB en desarrollo
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    try:
        from src.infrastructure.adapters.persistence.mongodb.connection import close_mongodb
        await close_mongodb()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Agents Manager - Gestión de agentes de IA y su base de conocimiento",
    lifespan=lifespan,
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar middleware de base de datos
from src.infrastructure.api.middleware.databaseErrorHandler import DatabaseErrorMiddleware

# Agregar middleware de base de datos
app.add_middleware(DatabaseErrorMiddleware)

# Registrar exception handlers (orden importante: más específico a más genérico)
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Registrar routers
app.include_router(agents.router, prefix=settings.api_prefix)
app.include_router(documents.router, prefix=settings.api_prefix)

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Endpoint de health check
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }

@app.get("/")
async def root():
    """
    Endpoint raíz
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": f"{settings.api_prefix}/docs"
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )