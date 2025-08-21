"""
Middleware para manejar errores de conexión de base de datos
"""
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

logger = logging.getLogger(__name__)

class DatabaseErrorMiddleware(BaseHTTPMiddleware):
    """
    Middleware que captura errores de base de datos y devuelve respuestas más útiles
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Detectar errores relacionados con MongoDB/Database
            error_message = str(exc).lower()
            
            if any(keyword in error_message for keyword in [
                "database connection failed",
                "database cannot be none",
                "nonetype object is not subscriptable",
                "ssl handshake failed",
                "failed to connect to mongodb",
                "cannot initialize database connection"
            ]):
                logger.error(f"Database connection error intercepted: {exc}")
                
                return JSONResponse(
                    status_code=503,  # Service Unavailable
                    content={
                        "error": "Database Unavailable",
                        "message": "No se puede conectar a la base de datos MongoDB. Verifica tu conexión de red y las credenciales de MongoDB Atlas.",
                        "details": {
                            "type": "DATABASE_CONNECTION_ERROR",
                            "suggestions": [
                                "Verifica que MongoDB Atlas esté disponible",
                                "Confirma que las credenciales en .env sean correctas", 
                                "Asegúrate de que tu IP esté en la whitelist de MongoDB Atlas",
                                "Revisa la configuración de red/firewall"
                            ]
                        },
                        "service": "AI Agents Manager",
                        "timestamp": str(exc)  # Para debugging
                    }
                )
            
            # Si no es un error de base de datos, re-lanzar la excepción
            raise exc
