"""
Utilidades para formatear datos y respuestas
"""
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

class FileFormatter:
    """Formateador para archivos y documentos"""
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Convierte bytes a formato legible"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """Genera un nombre único para el archivo"""
        timestamp = datetime.utc().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        name, extension = original_filename.rsplit('.', 1) if '.' in original_filename else (original_filename, '')
        
        # Limpiar nombre del archivo
        clean_name = "".join(c for c in name if c.isalnum() or c in '-_').rstrip()[:50]
        
        if extension:
            return f"{clean_name}_{timestamp}_{unique_id}.{extension}"
        else:
            return f"{clean_name}_{timestamp}_{unique_id}"
    
    @staticmethod
    def extract_file_info(filename: str, file_size: int, content_type: str) -> Dict[str, Any]:
        """Extrae información del archivo"""
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        return {
            "original_name": filename,
            "extension": extension,
            "size_bytes": file_size,
            "size_formatted": FileFormatter.format_file_size(file_size),
            "content_type": content_type,
            "upload_timestamp": datetime.utc().isoformat()
        }

class ResponseFormatter:
    """Formateador para respuestas de API"""
    
    @staticmethod
    def success_response(
        data: Any = None, 
        message: str = "Operación exitosa",
        meta: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Formatea respuesta exitosa"""
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.utc().isoformat()
        }
        
        if data is not None:
            response["data"] = data
            
        if meta:
            response["meta"] = meta
            
        return response
    
    @staticmethod
    def error_response(
        error_message: str,
        error_code: str = "GENERAL_ERROR",
        details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Formatea respuesta de error"""
        response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": error_message,
                "timestamp": datetime.utc().isoformat()
            }
        }
        
        if details:
            response["error"]["details"] = details
            
        return response
    
    @staticmethod
    def paginated_response(
        data: list,
        total: int,
        page: int = 1,
        per_page: int = 20,
        message: str = "Datos obtenidos exitosamente"
    ) -> Dict[str, Any]:
        """Formatea respuesta paginada"""
        total_pages = (total + per_page - 1) // per_page
        
        return ResponseFormatter.success_response(
            data=data,
            message=message,
            meta={
                "pagination": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
        )

class URLFormatter:
    """Formateador para URLs y paths"""
    
    @staticmethod
    def generate_s3_url(bucket_name: str, key: str, region: str = "us-east-1") -> str:
        """Genera URL de S3"""
        return f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"
    
    @staticmethod
    def generate_document_url(agent_id: str, document_id: str, base_url: str = "") -> str:
        """Genera URL para acceder a un documento"""
        if base_url:
            return f"{base_url}/api/v1/agents/{agent_id}/documents/{document_id}"
        return f"/api/v1/agents/{agent_id}/documents/{document_id}"

class AgentFormatter:
    """Formateador para datos de agentes"""
    
    @staticmethod
    def format_agent_summary(
        agent_id: str,
        name: str,
        document_count: int = 0,
        created_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Formatea resumen de agente"""
        return {
            "id": agent_id,
            "name": name,
            "document_count": document_count,
            "status": "active" if document_count > 0 else "pending_documents",
            "created_at": created_at.isoformat() if created_at else None
        }
    
    @staticmethod
    def format_agent_detail(
        agent_id: str,
        name: str,
        prompt: str,
        documents: list = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Formatea detalle completo del agente"""
        documents = documents or []
        
        return {
            "id": agent_id,
            "name": name,
            "prompt": prompt,
            "document_count": len(documents),
            "documents": documents,
            "status": "active" if documents else "pending_documents",
            "created_at": created_at.isoformat() if created_at else None,
            "updated_at": updated_at.isoformat() if updated_at else None,
            "storage_info": {
                "total_documents": len(documents),
                "total_size": sum(doc.get("size_bytes", 0) for doc in documents),
                "total_size_formatted": FileFormatter.format_file_size(
                    sum(doc.get("size_bytes", 0) for doc in documents)
                )
            }
        }
