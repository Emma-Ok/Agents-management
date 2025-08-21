"""
Pruebas unitarias para la entidad Document
"""
import pytest
from datetime import datetime
from src.domain.entities.document import Document
from src.domain.value_objects.agentId import AgentId
from src.domain.value_objects.documentType import DocumentType


@pytest.mark.unit
class TestDocumentEntity:
    """Pruebas para la entidad Document"""
    
    def test_create_document_success(self, sample_agent_id):
        """Prueba creación exitosa de un documento"""
        # Arrange
        filename = "test_document.pdf"
        document_type = DocumentType.PDF
        s3_url = "https://bucket.s3.amazonaws.com/agents/agent-id/test.pdf"
        s3_key = "agents/agent-id/test.pdf"
        file_size = 1024
        
        # Act
        document = Document.create(
            agent_id=sample_agent_id,
            filename=filename,
            document_type=document_type,
            s3_url=s3_url,
            s3_key=s3_key,
            file_size=file_size
        )
        
        # Assert
        assert document.agent_id == sample_agent_id
        assert document.filename == filename
        assert document.document_type == document_type
        assert document.s3_url == s3_url
        assert document.s3_key == s3_key
        assert document.file_size == file_size
        assert isinstance(document.id, str)
        assert isinstance(document.created_at, datetime)
        assert isinstance(document.updated_at, datetime)
        assert document.created_at == document.updated_at
    
    def test_document_filename_validation_empty(self, sample_agent_id):
        """Prueba validación de filename vacío"""
        # Arrange
        filename = ""
        
        # Act & Assert
        with pytest.raises(ValueError, match="File name cannot be empty"):
            Document.create(
                agent_id=sample_agent_id,
                filename=filename,
                document_type=DocumentType.PDF,
                s3_url="https://test.com/file.pdf",
                s3_key="test/file.pdf",
                file_size=1024
            )
    
    def test_document_filename_validation_too_long(self, sample_agent_id):
        """Prueba validación de filename demasiado largo"""
        # Arrange
        filename = "A" * 101  # Más de 100 caracteres
        
        # Act & Assert
        with pytest.raises(ValueError, match="File name must be at most 100 characters"):
            Document.create(
                agent_id=sample_agent_id,
                filename=filename,
                document_type=DocumentType.PDF,
                s3_url="https://test.com/file.pdf",
                s3_key="test/file.pdf",
                file_size=1024
            )
    
    def test_document_file_size_validation_zero(self, sample_agent_id):
        """Prueba validación de tamaño de archivo cero"""
        # Arrange
        file_size = 0
        
        # Act & Assert
        with pytest.raises(ValueError, match="File size must be a positive integer"):
            Document.create(
                agent_id=sample_agent_id,
                filename="test.pdf",
                document_type=DocumentType.PDF,
                s3_url="https://test.com/file.pdf",
                s3_key="test/file.pdf",
                file_size=file_size
            )
    
    def test_document_file_size_validation_negative(self, sample_agent_id):
        """Prueba validación de tamaño de archivo negativo"""
        # Arrange
        file_size = -100
        
        # Act & Assert
        with pytest.raises(ValueError, match="File size must be a positive integer"):
            Document.create(
                agent_id=sample_agent_id,
                filename="test.pdf",
                document_type=DocumentType.PDF,
                s3_url="https://test.com/file.pdf",
                s3_key="test/file.pdf",
                file_size=file_size
            )
    
    def test_document_file_size_validation_too_large(self, sample_agent_id):
        """Prueba validación de tamaño de archivo demasiado grande"""
        # Arrange
        file_size = 21 * 1024 * 1024  # 21 MB (más del límite de 20MB)
        
        # Act & Assert
        with pytest.raises(ValueError, match="File size must not exceed"):
            Document.create(
                agent_id=sample_agent_id,
                filename="test.pdf",
                document_type=DocumentType.PDF,
                s3_url="https://test.com/file.pdf",
                s3_key="test/file.pdf",
                file_size=file_size
            )
    
    def test_get_extension(self, sample_document):
        """Prueba obtener extensión del archivo"""
        # Act
        extension = sample_document.get_extension()
        
        # Assert
        assert extension == "pdf"
    
    def test_get_size_in_mb(self, sample_document):
        """Prueba obtener tamaño en MB"""
        # Act
        size_mb = sample_document.get_size()
        
        # Assert
        assert size_mb == 0.0  # 1024 bytes = 0.00 MB (redondeado)
    
    def test_get_size_larger_file(self, sample_agent_id):
        """Prueba obtener tamaño en MB para archivo más grande"""
        # Arrange
        file_size = 5 * 1024 * 1024  # 5 MB
        document = Document.create(
            agent_id=sample_agent_id,
            filename="large_file.pdf",
            document_type=DocumentType.PDF,
            s3_url="https://test.com/large_file.pdf",
            s3_key="test/large_file.pdf",
            file_size=file_size
        )
        
        # Act
        size_mb = document.get_size()
        
        # Assert
        assert size_mb == 5.0
    
    def test_document_with_different_types(self, sample_agent_id):
        """Prueba creación de documentos con diferentes tipos"""
        # Arrange & Act
        pdf_doc = Document.create(
            agent_id=sample_agent_id,
            filename="test.pdf",
            document_type=DocumentType.PDF,
            s3_url="https://test.com/test.pdf",
            s3_key="test/test.pdf",
            file_size=1024
        )
        
        docx_doc = Document.create(
            agent_id=sample_agent_id,
            filename="test.docx",
            document_type=DocumentType.DOCX,
            s3_url="https://test.com/test.docx",
            s3_key="test/test.docx",
            file_size=2048
        )
        
        # Assert
        assert pdf_doc.document_type == DocumentType.PDF
        assert docx_doc.document_type == DocumentType.DOCX
        assert pdf_doc.get_extension() == "pdf"
        assert docx_doc.get_extension() == "docx"
    
    def test_document_equality(self, sample_agent_id):
        """Prueba igualdad entre documentos"""
        # Arrange
        doc_id = "test-doc-123"
        filename = "test.pdf"
        
        doc1 = Document(
            id=doc_id,
            agent_id=sample_agent_id,
            filename=filename,
            document_type=DocumentType.PDF,
            s3_url="https://test.com/test.pdf",
            s3_key="test/test.pdf",
            file_size=1024,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        doc2 = Document(
            id=doc_id,
            agent_id=sample_agent_id,
            filename=filename,
            document_type=DocumentType.PDF,
            s3_url="https://test.com/test.pdf",
            s3_key="test/test.pdf",
            file_size=1024,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Act & Assert
        assert doc1.id == doc2.id
        assert doc1.filename == doc2.filename
        assert doc1.agent_id == doc2.agent_id
