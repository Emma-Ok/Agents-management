import boto3
from botocore.exceptions import ClientError
from typing import BinaryIO, Optional, Dict, Any, List
from io import BytesIO
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
        
        # Crear cliente S3
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=self.region
        )
        
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
            
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise
    
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
            return 0
    
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