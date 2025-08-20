import boto3
from botocore.exceptions import ClientError, EndpointConnectionError, SSLError
from botocore.config import Config
from typing import BinaryIO, Optional, Dict, Any, List
from io import BytesIO
import asyncio
from concurrent.futures import ThreadPoolExecutor
from src.domain.ports.services.fileStorage import FileStorage, FileMetadata
from src.infrastructure.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)

class S3FileStorage(FileStorage):
    """
    Implementación AWS S3 del almacenamiento de archivos
    
    Adapta la interfaz del dominio a las operaciones de S3
    """
    
    def __init__(self, bucket_name: str, region: str, access_key_id: str, secret_access_key: str):
        self.bucket_name = bucket_name
        self.region = region
        
        # Configuración robusta para S3 con manejo de SSL
        config = Config(
            region_name=self.region,
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            },
            read_timeout=60,
            connect_timeout=10,
            max_pool_connections=10,
            # Configuración SSL más robusta (use_ssl se maneja en el endpoint)
            signature_version='s3v4'
        )
        
        # Crear cliente S3 con HTTPS habilitado por defecto
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            config=config,
            use_ssl=True  # Asegurar que SSL está habilitado
        )
        
        # Thread pool executor para operaciones síncronas
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Verificar/crear bucket
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Verifica que el bucket existe, lo crea si no"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"S3 bucket '{self.bucket_name}' exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Crear el bucket
                try:
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    logger.info(f"S3 bucket '{self.bucket_name}' created")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
            else:
                logger.error(f"Error checking bucket: {e}")
                raise
    
    async def upload_file(
        self,
        file: BinaryIO,
        key: str,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FileMetadata:
        """Sube un archivo a S3"""
        def _upload_sync():
            try:
                # Preparar metadata
                extra_args = {
                    'ContentType': content_type,
                    'Metadata': metadata or {}
                }
                
                # Subir archivo
                self.s3_client.upload_fileobj(
                    file,
                    self.bucket_name,
                    key,
                    ExtraArgs=extra_args
                )
                
                # Generar URL pública
                url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
                
                # Obtener información del archivo
                response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
                
                logger.info(f"File uploaded to S3: {key}")
                
                return FileMetadata(
                    key=key,
                    url=url,
                    size=response['ContentLength'],
                    content_type=content_type,
                    etag=response.get('ETag', '').strip('"')
                )
                
            except (ClientError, SSLError, EndpointConnectionError) as e:
                logger.error(f"Error uploading file to S3: {e}")
                # Re-lanzar como StorageException para manejo consistente
                from src.domain.exceptions.domainExceptions import StorageException
                if "SSL" in str(e) or "EOF occurred in violation of protocol" in str(e):
                    raise StorageException(f"Error de conexión SSL con AWS S3: {str(e)}")
                elif "endpoint" in str(e).lower():
                    raise StorageException(f"Error de conectividad con AWS S3: {str(e)}")
                else:
                    raise StorageException(f"Error en AWS S3: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error uploading file to S3: {e}")
                from src.domain.exceptions.domainExceptions import StorageException
                raise StorageException(f"Error inesperado en S3: {str(e)}")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _upload_sync)
    
    async def download_file(self, key: str) -> BinaryIO:
        """Descarga un archivo de S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return BytesIO(response['Body'].read())
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {e}")
            raise
    
    async def delete_file(self, key: str) -> bool:
        """Elimina un archivo de S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"File deleted from S3: {key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting file from S3: {e}")
            return False
    
    async def delete_folder(self, prefix: str) -> int:
        """Elimina todos los archivos con un prefijo"""
        try:
            # Listar objetos con el prefijo
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
            
            delete_keys = []
            for page in pages:
                if 'Contents' in page:
                    delete_keys.extend([{'Key': obj['Key']} for obj in page['Contents']])
            
            if not delete_keys:
                return 0
            
            # Eliminar en lotes de 1000 (límite de S3)
            deleted_count = 0
            for i in range(0, len(delete_keys), 1000):
                batch = delete_keys[i:i+1000]
                response = self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': batch}
                )
                deleted_count += len(response.get('Deleted', []))
            
            logger.info(f"Deleted {deleted_count} files with prefix: {prefix}")
            return deleted_count
            
        except ClientError as e:
            logger.error(f"Error deleting folder from S3: {e}")
            raise Exception(f"Failed to delete S3 folder {prefix}: {str(e)}")
    
    async def file_exists(self, key: str) -> bool:
        """Verifica si existe un archivo"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False
    
    async def get_file_metadata(self, key: str) -> Optional[FileMetadata]:
        """Obtiene la metadata de un archivo"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
            
            return FileMetadata(
                key=key,
                url=url,
                size=response['ContentLength'],
                content_type=response.get('ContentType', 'application/octet-stream'),
                etag=response.get('ETag', '').strip('"')
            )
        except ClientError:
            return None
    
    async def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Genera una URL temporal"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
    
    async def list_files(self, prefix: str, max_keys: int = 100) -> List[FileMetadata]:
        """Lista archivos con un prefijo"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{obj['Key']}"
                    files.append(FileMetadata(
                        key=obj['Key'],
                        url=url,
                        size=obj['Size'],
                        content_type='application/octet-stream',
                        etag=obj.get('ETag', '').strip('"')
                    ))
            
            return files
            
        except ClientError as e:
            logger.error(f"Error listing files from S3: {e}")
            return []
    
    async def create_folder(self, folder_key: str) -> bool:
        """
        Crea una carpeta en S3 subiendo un objeto vacío con el prefijo
        
        En S3, las carpetas no existen realmente, pero se simulan creando
        un objeto vacío que termina en '/'
        """
        def _create_folder_sync():
            try:
                # Asegurar que la clave termine en '/'
                final_key = folder_key if folder_key.endswith('/') else folder_key + '/'
                
                # Crear un objeto vacío para representar la carpeta
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=final_key,
                    Body=b'',
                    ContentType='application/x-directory'
                )
                
                logger.info(f"Created folder in S3: {final_key}")
                return True
                
            except ClientError as e:
                logger.error(f"Error creating folder in S3: {e}")
                return False

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _create_folder_sync)