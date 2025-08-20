from abc import ABC, abstractmethod

from typing import BinaryIO, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class FileMetadata:
    """Metadata de un archivo almacenado"""
    key: str
    url: str
    size: int
    content_type: str
    etag: Optional[str] = None

class FileStorage(ABC):
    """
    Puerto de salida para el almacenamiento de archivos
    
    Define el contrato para cualquier servicio de almacenamiento
    (AWS S3, Azure Blob Storage, sistema de archivos local, etc.)
    """
    
    @abstractmethod
    async def upload_file(
        self,
        file: BinaryIO,
        key: str,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FileMetadata:
        """
        Sube un archivo al almacenamiento
        
        Args:
            file: Archivo a subir
            key: Clave/ruta donde se almacenará
            content_type: Tipo MIME del archivo
            metadata: Metadata adicional
        
        Returns:
            FileMetadata con la información del archivo subido
        """
        pass
    
    @abstractmethod
    async def download_file(self, key: str) -> BinaryIO:
        """
        Descarga un archivo del almacenamiento
        
        Args:
            key: Clave del archivo
        
        Returns:
            Stream del archivo
        """
        pass
    
    @abstractmethod
    async def delete_file(self, key: str) -> bool:
        """
        Elimina un archivo del almacenamiento
        
        Args:
            key: Clave del archivo
        
        Returns:
            True si se eliminó correctamente
        """
        pass
    
    @abstractmethod
    async def delete_folder(self, prefix: str) -> int:
        """
        Elimina todos los archivos con un prefijo (carpeta)
        
        Args:
            prefix: Prefijo de los archivos a eliminar
        
        Returns:
            Número de archivos eliminados
        """
        pass
    
    @abstractmethod
    async def file_exists(self, key: str) -> bool:
        """
        Verifica si existe un archivo
        
        Args:
            key: Clave del archivo
        
        Returns:
            True si el archivo existe
        """
        pass
    
    @abstractmethod
    async def get_file_metadata(self, key: str) -> Optional[FileMetadata]:
        """
        Obtiene la metadata de un archivo
        
        Args:
            key: Clave del archivo
        
        Returns:
            FileMetadata o None si no existe
        """
        pass
    
    @abstractmethod
    async def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600
    ) -> str:
        """
        Genera una URL temporal para acceder al archivo
        
        Args:
            key: Clave del archivo
            expiration: Tiempo de expiración en segundos
        
        Returns:
            URL temporal
        """
        pass
    
    @abstractmethod
    async def list_files(
        self,
        prefix: str,
        max_keys: int = 100
    ) -> list[FileMetadata]:
        """
        Lista archivos con un prefijo
        
        Args:
            prefix: Prefijo para filtrar
            max_keys: Número máximo de resultados
        
        Returns:
            Lista de FileMetadata
        """
        pass