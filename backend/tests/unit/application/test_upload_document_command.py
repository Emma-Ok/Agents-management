"""
Pruebas unitarias para UploadDocumentCommand
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from io import BytesIO
from src.application.commands.uploadDocument import UploadDocumentCommand
from src.application.dto.documentDto import UploadDocumentDTO
from src.domain.entities.agent import Agent
from src.domain.entities.document import Document
from src.domain.value_objects.agentId import AgentId
from src.domain.value_objects.documentType import DocumentType
from src.domain.exceptions.domainExceptions import AgentNotFoundException, FileSizeExceededException, InvalidFileTypeException
from src.domain.ports.services.fileStorage import FileMetadata


@pytest.mark.unit
class TestUploadDocumentCommand:
    """Pruebas para el comando UploadDocument"""
    
    @pytest.fixture
    def command(self, mock_agent_repository, mock_document_repository, mock_file_storage):
        """Comando con repositorios y storage mock"""
        return UploadDocumentCommand(
            mock_agent_repository, 
            mock_document_repository, 
            mock_file_storage
        )
    
    @pytest.fixture
    def valid_upload_dto(self, sample_agent_id):
        """DTO válido para subir documento"""
        test_file = BytesIO(b"test content")
        return UploadDocumentDTO(
            agent_id=str(sample_agent_id),
            filename="test_document.pdf",
            file=test_file,
            content_type="application/pdf",
            file_size=1024
        )
    
    @pytest.fixture
    def mock_file_metadata(self, sample_agent_id):
        """Mock de metadata de archivo subido"""
        return FileMetadata(
            key=f"agents/{sample_agent_id}/test_document.pdf",
            url=f"https://bucket.s3.amazonaws.com/agents/{sample_agent_id}/test_document.pdf",
            size=1024,
            content_type="application/pdf",
            etag="abc123"
        )
    
    async def test_upload_document_success(
        self, 
        command, 
        mock_agent_repository, 
        mock_document_repository, 
        mock_file_storage,
        valid_upload_dto, 
        sample_agent, 
        mock_file_metadata
    ):
        """Prueba subida exitosa de documento"""
        # Arrange
        mock_agent_repository.get_agent_by_id.return_value = sample_agent
        mock_file_storage.upload_file.return_value = mock_file_metadata
        
        # Mock del documento guardado
        saved_document = MagicMock()
        saved_document.id = "doc-123"
        saved_document.filename = valid_upload_dto.filename
        saved_document.s3_url = mock_file_metadata.url
        saved_document.file_size = valid_upload_dto.file_size
        saved_document.get_size.return_value = 0.0
        saved_document.document_type.value = "pdf"
        saved_document.created_at = sample_agent.created_at
        saved_document.agent_id = sample_agent.id
        
        mock_document_repository.save.return_value = saved_document
        mock_agent_repository.save_agent.return_value = sample_agent
        
        # Act
        result = await command.execute(valid_upload_dto)
        
        # Assert
        assert result.filename == valid_upload_dto.filename
        assert result.file_url == mock_file_metadata.url
        assert result.id == "doc-123"
        
        # Verificar llamadas
        mock_agent_repository.get_agent_by_id.assert_called_once()
        mock_file_storage.upload_file.assert_called_once()
        mock_document_repository.save.assert_called_once()
        mock_agent_repository.save_agent.assert_called_once()
    
    async def test_upload_document_agent_not_found(
        self, 
        command, 
        mock_agent_repository,
        valid_upload_dto
    ):
        """Prueba error cuando el agente no existe"""
        # Arrange
        mock_agent_repository.get_agent_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(AgentNotFoundException):
            await command.execute(valid_upload_dto)
        
        # Verificar que no se intentó subir archivo
        mock_agent_repository.get_agent_by_id.assert_called_once()
    
    async def test_upload_document_invalid_file_type(
        self, 
        command, 
        mock_agent_repository, 
        sample_agent
    ):
        """Prueba error con tipo de archivo inválido"""
        # Arrange
        mock_agent_repository.get_agent_by_id.return_value = sample_agent
        
        invalid_dto = UploadDocumentDTO(
            agent_id=str(sample_agent.id),
            filename="test_document.exe",  # Extensión inválida
            file=BytesIO(b"test content"),
            content_type="application/x-executable",
            file_size=1024
        )
        
        # Act & Assert
        with pytest.raises(InvalidFileTypeException):
            await command.execute(invalid_dto)
    
    async def test_upload_document_file_too_large(
        self, 
        command, 
        mock_agent_repository, 
        sample_agent
    ):
        """Prueba error con archivo demasiado grande"""
        # Arrange
        mock_agent_repository.get_agent_by_id.return_value = sample_agent
        
        large_file_dto = UploadDocumentDTO(
            agent_id=str(sample_agent.id),
            filename="large_file.pdf",
            file=BytesIO(b"test content"),
            content_type="application/pdf",
            file_size=25 * 1024 * 1024  # 25 MB (más del límite)
        )
        
        # Act & Assert
        with pytest.raises(FileSizeExceededException):
            await command.execute(large_file_dto)
    
    async def test_upload_document_s3_error(
        self, 
        command, 
        mock_agent_repository, 
        mock_file_storage,
        valid_upload_dto, 
        sample_agent
    ):
        """Prueba manejo de error de S3"""
        # Arrange
        mock_agent_repository.get_agent_by_id.return_value = sample_agent
        mock_file_storage.upload_file.side_effect = Exception("S3 error")
        
        # Act & Assert
        with pytest.raises(Exception, match="S3 error"):
            await command.execute(valid_upload_dto)
        
        # Verificar que se intentó subir pero falló
        mock_file_storage.upload_file.assert_called_once()
    
    async def test_upload_document_generates_correct_s3_key(
        self, 
        command, 
        mock_agent_repository, 
        mock_document_repository,
        mock_file_storage,
        valid_upload_dto, 
        sample_agent, 
        mock_file_metadata
    ):
        """Prueba que se genera la clave S3 correcta"""
        # Arrange
        mock_agent_repository.get_agent_by_id.return_value = sample_agent
        mock_file_storage.upload_file.return_value = mock_file_metadata
        
        saved_document = MagicMock()
        saved_document.id = "doc-123"
        saved_document.filename = valid_upload_dto.filename
        saved_document.s3_url = mock_file_metadata.url
        saved_document.file_size = valid_upload_dto.file_size
        saved_document.get_size.return_value = 0.0
        saved_document.document_type.value = "pdf"
        saved_document.created_at = sample_agent.created_at
        saved_document.agent_id = sample_agent.id
        
        mock_document_repository.save.return_value = saved_document
        mock_agent_repository.save_agent.return_value = sample_agent
        
        # Act
        await command.execute(valid_upload_dto)
        
        # Assert
        # Verificar que se llamó upload_file con la clave correcta
        call_args = mock_file_storage.upload_file.call_args
        expected_key = f"agents/{sample_agent.id}/{valid_upload_dto.filename}"
        assert call_args[1]['key'] == expected_key
    
    async def test_upload_document_updates_agent_counter(
        self, 
        command, 
        mock_agent_repository, 
        mock_document_repository, 
        mock_file_storage,
        valid_upload_dto, 
        sample_agent, 
        mock_file_metadata
    ):
        """Prueba que se actualiza el contador de documentos del agente"""
        # Arrange
        initial_count = sample_agent.documents_count
        mock_agent_repository.get_agent_by_id.return_value = sample_agent
        mock_file_storage.upload_file.return_value = mock_file_metadata
        
        saved_document = MagicMock()
        saved_document.id = "doc-123"
        saved_document.filename = valid_upload_dto.filename
        saved_document.s3_url = mock_file_metadata.url
        saved_document.file_size = valid_upload_dto.file_size
        saved_document.get_size.return_value = 0.0
        saved_document.document_type.value = "pdf"
        saved_document.created_at = sample_agent.created_at
        saved_document.agent_id = sample_agent.id
        
        mock_document_repository.save.return_value = saved_document
        mock_agent_repository.save_agent.return_value = sample_agent
        
        # Act
        await command.execute(valid_upload_dto)
        
        # Assert
        assert sample_agent.documents_count == initial_count + 1
        mock_agent_repository.save_agent.assert_called_once_with(sample_agent)
    
    async def test_upload_document_save_error(
        self, 
        command, 
        mock_agent_repository, 
        mock_document_repository, 
        mock_file_storage,
        valid_upload_dto, 
        sample_agent, 
        mock_file_metadata
    ):
        """Prueba manejo de error al guardar documento"""
        # Arrange
        mock_agent_repository.get_agent_by_id.return_value = sample_agent
        mock_file_storage.upload_file.return_value = mock_file_metadata
        mock_document_repository.save.return_value = None  # Error: no se guardó
        
        # Act & Assert
        with pytest.raises(Exception, match="no se guardó correctamente"):
            await command.execute(valid_upload_dto)
