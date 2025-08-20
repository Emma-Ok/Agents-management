import os
from src.domain.entities.document import Document
from src.domain.value_objects.agentId import AgentId
from src.domain.value_objects.documentType import DocumentType
from src.domain.ports.repositories.agentRepository import AgentRepository
from src.domain.ports.repositories.documentRepository import DocumentRepository
from src.domain.ports.services.fileStorage import FileStorage
from src.domain.exceptions.domainExceptions import AgentNotFoundException, FileSizeExceededException, InvalidFileTypeException
from ..dto.documentDto import UploadDocumentDTO, DocumentResponseDTO
import logging

logger = logging.getLogger(__name__)

class UploadDocumentCommand:
    """
    Caso de uso #4: Subir un documento para un agente
    """
    
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
    
    def __init__(
        self,
        agent_repository: AgentRepository,
        document_repository: DocumentRepository,
        file_storage: FileStorage
    ):
        self.agent_repository = agent_repository
        self.document_repository = document_repository
        self.file_storage = file_storage
    
    async def execute(self, dto: UploadDocumentDTO) -> DocumentResponseDTO:
        """
        Ejecuta la subida del documento
        
        1. Valida el agente existe
        2. Valida el tipo de archivo
        3. Valida el tamaño
        4. Sube el archivo a S3
        5. Guarda el registro en BD
        6. Actualiza el contador del agente
        """
        logger.info(f"Uploading document '{dto.filename}' for agent {dto.agent_id}")
        
        # Validar que el agente existe
        agent_id_vo = AgentId(dto.agent_id)
        agent = await self.agent_repository.get_agent_by_id(agent_id_vo)
        if not agent:
            raise AgentNotFoundException(dto.agent_id)
        
        # Validar tipo de archivo
        extension = os.path.splitext(dto.filename)[1]
        if not DocumentType.is_valid_extension(extension):
            raise InvalidFileTypeException(extension)
        
        doc_type = DocumentType.from_extension(extension)
        
        # Validar tamaño
        if dto.file_size > self.MAX_FILE_SIZE:
            raise FileSizeExceededException(dto.file_size, self.MAX_FILE_SIZE)
        
        # Generar la clave S3 (path en el bucket)
        s3_key = f"agents/{dto.agent_id}/{dto.filename}"
        
        # Subir archivo a S3
        file_metadata = await self.file_storage.upload_file(
            file=dto.file,
            key=s3_key,
            content_type=dto.content_type,
            metadata={
                "agent_id": dto.agent_id,
                "original_filename": dto.filename
            }
        )
        
        # Crear entidad Document
        document = Document.create(
            agent_id=agent_id_vo,
            filename=dto.filename,
            document_type=doc_type,
            s3_url=file_metadata.url,
            s3_key=file_metadata.key,
            file_size=dto.file_size
        )
        
        # Guardar en BD
        saved_document = await self.document_repository.save(document)

        # Verificar que el documento fue guardado correctamente y tiene 'id'
        if not saved_document or not hasattr(saved_document, 'id'):
            logger.error("El documento no se guardó correctamente o no tiene atributo 'id'.")
            raise Exception("El documento no se guardó correctamente o no tiene atributo 'id'.")

        # Actualizar contador del agente
        agent.documents_count += 1
        await self.agent_repository.save_agent(agent)

        logger.info(f"Document '{dto.filename}' uploaded successfully with ID: {saved_document.id}")

        return DocumentResponseDTO(
            id=saved_document.id,
            agent_id=str(saved_document.agent_id),
            filename=saved_document.filename,
            document_type=saved_document.document_type.value,
            file_url=saved_document.s3_url,
            file_size=saved_document.file_size,
            file_size_mb=saved_document.get_size(),
            created_at=saved_document.created_at
        )