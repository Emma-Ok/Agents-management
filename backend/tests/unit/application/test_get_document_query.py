"""
Pruebas unitarias para GetDocumentQuery
"""
import pytest
from unittest.mock import AsyncMock
from src.application.queries.getDocument import GetDocumentQuery
from src.domain.exceptions.domainExceptions import DocumentNotFoundException


@pytest.mark.unit
class TestGetDocumentQuery:
    """Pruebas para la query GetDocument"""
    
    @pytest.fixture
    def query(self, mock_document_repository):
        """Query con repositorio mock"""
        return GetDocumentQuery(mock_document_repository)
    
    async def test_get_document_success(self, query, mock_document_repository, sample_document):
        """Prueba obtener documento existente"""
        # Arrange
        document_id = "doc-123"
        mock_document_repository.find_by_id.return_value = sample_document
        
        # Act
        result = await query.execute(document_id)
        
        # Assert
        assert result.id == sample_document.id
        assert result.filename == sample_document.filename
        assert result.agent_id == str(sample_document.agent_id)
        assert result.document_type == sample_document.document_type.value
        assert result.file_url == sample_document.s3_url
        assert result.file_size == sample_document.file_size
        assert result.file_size_mb == sample_document.get_size()
        
        mock_document_repository.find_by_id.assert_called_once_with(document_id)
    
    async def test_get_document_not_found(self, query, mock_document_repository):
        """Prueba error cuando el documento no existe"""
        # Arrange
        document_id = "nonexistent-doc"
        mock_document_repository.find_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(DocumentNotFoundException, match=document_id):
            await query.execute(document_id)
        
        mock_document_repository.find_by_id.assert_called_once_with(document_id)
    
    async def test_get_document_repository_error(self, query, mock_document_repository):
        """Prueba manejo de error del repositorio"""
        # Arrange
        document_id = "doc-123"
        mock_document_repository.find_by_id.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await query.execute(document_id)
        
        mock_document_repository.find_by_id.assert_called_once_with(document_id)
