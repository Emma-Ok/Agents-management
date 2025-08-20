"""
Validadores para archivos y datos de entrada
"""
from typing import List, Tuple
from fastapi import UploadFile, HTTPException
import magic
import os

class FileValidator:
    """Validador de archivos subidos"""
    
    # Tipos de archivo permitidos con sus MIME types
    ALLOWED_TYPES = {
        'pdf': ['application/pdf'],
        'docx': [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-word.document.macroEnabled.12',
            'application/zip',  # DOCX son archivos ZIP
            'application/x-zip-compressed'  # Variante de ZIP
        ],
        'xlsx': [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel.sheet.macroEnabled.12',
            'application/zip',  # XLSX son archivos ZIP
            'application/x-zip-compressed'  # Variante de ZIP
        ],
        'pptx': [
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.ms-powerpoint.presentation.macroEnabled.12',
            'application/zip',  # PPTX son archivos ZIP
            'application/x-zip-compressed'  # Variante de ZIP
        ],
        'txt': ['text/plain'],
        'csv': ['text/csv', 'application/csv']
    }
    
    # Extensiones permitidas
    ALLOWED_EXTENSIONS = list(ALLOWED_TYPES.keys())
    
    # Tamaño máximo por defecto (10MB)
    DEFAULT_MAX_SIZE = 10 * 1024 * 1024
    
    @classmethod
    def validate_file(
        cls, 
        file: UploadFile, 
        max_size_mb: int = 10,
        allowed_extensions: List[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Valida un archivo subido
        
        Returns:
            Tuple[is_valid, file_type, error_message]
        """
        if allowed_extensions is None:
            allowed_extensions = cls.ALLOWED_EXTENSIONS
            
        max_size_bytes = max_size_mb * 1024 * 1024
        
        # 1. Validar que el archivo no esté vacío
        if not file.filename:
            return False, '', "No se proporcionó un archivo"
        
        # 2. Validar extensión del archivo
        file_extension = cls._get_file_extension(file.filename)
        if file_extension not in allowed_extensions:
            return False, '', f"Tipo de archivo no permitido. Permitidos: {', '.join(allowed_extensions)}"
        
        # 3. Validar MIME type si está disponible
        if file.content_type:
            if not cls._is_valid_mime_type(file.content_type, file_extension):
                return False, '', f"Tipo MIME no coincide con la extensión del archivo"
        
        # 4. Validar tamaño del archivo
        if file.size and file.size > max_size_bytes:
            return False, '', f"Archivo demasiado grande. Máximo permitido: {max_size_mb}MB"
        
        return True, file_extension, ""
    
    @classmethod
    def _get_file_extension(cls, filename: str) -> str:
        """Extrae la extensión del archivo"""
        return filename.lower().split('.')[-1] if '.' in filename else ''
    
    @classmethod
    def _is_valid_mime_type(cls, mime_type: str, file_extension: str) -> bool:
        """Verifica si el MIME type coincide con la extensión"""
        if file_extension not in cls.ALLOWED_TYPES:
            return False
        
        return mime_type.lower() in [mt.lower() for mt in cls.ALLOWED_TYPES[file_extension]]
    
    @classmethod
    def validate_file_content(cls, file_content: bytes, filename: str) -> Tuple[bool, str]:
        """
        Valida el contenido del archivo usando python-magic
        
        Args:
            file_content: Contenido del archivo en bytes
            filename: Nombre del archivo
            
        Returns:
            Tuple[is_valid, error_message]
        """
        try:
            # Detectar MIME type real del contenido
            mime_type = magic.from_buffer(file_content, mime=True)
            file_extension = cls._get_file_extension(filename)
            
            if not cls._is_valid_mime_type(mime_type, file_extension):
                # Mensaje más claro y específico
                expected_types = cls.ALLOWED_TYPES.get(file_extension, [])
                expected_str = ', '.join(expected_types)
                
                return False, (
                    f"El archivo '{filename}' parece estar dañado o tener formato incorrecto. "
                    f"Detectado: {mime_type}, esperado: {expected_str}. "
                    f"Intenta convertir el archivo al formato correcto o usar un archivo diferente."
                )
            
            return True, ""
            
        except Exception as e:
            # Si python-magic no está disponible o falla, hacer validación más permisiva
            # Solo validar que el archivo no esté completamente vacío
            if len(file_content) == 0:
                return False, "El archivo está vacío"
            
            # Para archivos pequeños (< 100 bytes), ser más estricto
            if len(file_content) < 100:
                return False, "El archivo parece estar incompleto o dañado"
            
            # Para otros casos, permitir el archivo con advertencia en logs
            import logging
            logging.warning(f"No se pudo validar contenido de {filename}: {str(e)}")
            return True, ""

class AgentValidator:
    """Validador para datos de agentes"""
    
    MIN_NAME_LENGTH = 3
    MAX_NAME_LENGTH = 100
    MIN_PROMPT_LENGTH = 10
    MAX_PROMPT_LENGTH = 5000
    
    @classmethod
    def validate_agent_name(cls, name: str) -> Tuple[bool, str]:
        """Valida el nombre del agente"""
        if not name or not name.strip():
            return False, "El nombre del agente es requerido"
        
        name = name.strip()
        
        if len(name) < cls.MIN_NAME_LENGTH:
            return False, f"El nombre debe tener al menos {cls.MIN_NAME_LENGTH} caracteres"
        
        if len(name) > cls.MAX_NAME_LENGTH:
            return False, f"El nombre no puede exceder {cls.MAX_NAME_LENGTH} caracteres"
        
        # Verificar caracteres válidos (letras, números, espacios, guiones)
        if not all(c.isalnum() or c.isspace() or c in '-_' for c in name):
            return False, "El nombre solo puede contener letras, números, espacios y guiones"
        
        return True, ""
    
    @classmethod
    def validate_agent_prompt(cls, prompt: str) -> Tuple[bool, str]:
        """Valida el prompt del agente"""
        if not prompt or not prompt.strip():
            return False, "El prompt del agente es requerido"
        
        prompt = prompt.strip()
        
        if len(prompt) < cls.MIN_PROMPT_LENGTH:
            return False, f"El prompt debe tener al menos {cls.MIN_PROMPT_LENGTH} caracteres"
        
        if len(prompt) > cls.MAX_PROMPT_LENGTH:
            return False, f"El prompt no puede exceder {cls.MAX_PROMPT_LENGTH} caracteres"
        
        return True, ""

class DocumentValidator:
    """Validador para metadata de documentos"""
    
    @classmethod
    def validate_agent_id(cls, agent_id: str) -> Tuple[bool, str]:
        """Valida el ID del agente"""
        if not agent_id or not agent_id.strip():
            return False, "El ID del agente es requerido"
        
        # Verificar formato UUID básico
        agent_id = agent_id.strip()
        if len(agent_id) < 10:  # UUID mínimo
            return False, "ID del agente inválido"
        
        return True, ""
    
    @classmethod
    def generate_document_key(cls, agent_id: str, filename: str) -> str:
        """Genera la clave S3 para un documento"""
        # Limpiar el nombre del archivo
        clean_filename = "".join(c for c in filename if c.isalnum() or c in '.-_').rstrip()
        
        # Generar clave con estructura organizada
        return f"agents/{agent_id}/documents/{clean_filename}"
    
    @classmethod
    def validate_document_metadata(cls, metadata: dict) -> Tuple[bool, str]:
        """Valida metadata adicional del documento"""
        if not isinstance(metadata, dict):
            return False, "Metadata debe ser un diccionario"
        
        # Verificar que las claves sean strings válidos
        for key, value in metadata.items():
            if not isinstance(key, str) or len(key) > 50:
                return False, f"Clave de metadata inválida: {key}"
            
            if not isinstance(value, (str, int, float, bool)):
                return False, f"Valor de metadata inválido para {key}"
        
        return True, ""
