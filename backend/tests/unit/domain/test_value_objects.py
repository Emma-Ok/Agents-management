"""
Pruebas unitarias para Value Objects
"""
import pytest
from src.domain.value_objects.agentId import AgentId
from src.domain.value_objects.documentType import DocumentType


@pytest.mark.unit
class TestAgentId:
    """Pruebas para el Value Object AgentId"""
    
    def test_generate_agent_id(self):
        """Prueba generación de AgentId"""
        # Act
        agent_id = AgentId.generate()
        
        # Assert
        assert isinstance(agent_id, AgentId)
        assert isinstance(str(agent_id), str)
        assert len(str(agent_id)) > 0
    
    def test_agent_id_from_string(self):
        """Prueba creación de AgentId desde string"""
        # Arrange
        id_string = "test-agent-123"
        
        # Act
        agent_id = AgentId(id_string)
        
        # Assert
        assert str(agent_id) == id_string
    
    def test_agent_id_equality(self):
        """Prueba igualdad entre AgentIds"""
        # Arrange
        id_string = "test-agent-123"
        agent_id1 = AgentId(id_string)
        agent_id2 = AgentId(id_string)
        
        # Act & Assert
        assert agent_id1 == agent_id2
        assert str(agent_id1) == str(agent_id2)
    
    def test_agent_id_inequality(self):
        """Prueba desigualdad entre AgentIds diferentes"""
        # Arrange
        agent_id1 = AgentId.generate()
        agent_id2 = AgentId.generate()
        
        # Act & Assert
        assert agent_id1 != agent_id2
        assert str(agent_id1) != str(agent_id2)
    
    def test_agent_id_hash(self):
        """Prueba que AgentId es hasheable"""
        # Arrange
        agent_id = AgentId.generate()
        
        # Act & Assert
        hash_value = hash(agent_id)
        assert isinstance(hash_value, int)
        
        # Debe poder usarse en sets y diccionarios
        agent_set = {agent_id}
        assert agent_id in agent_set


@pytest.mark.unit
class TestDocumentType:
    """Pruebas para el Value Object DocumentType"""
    
    def test_document_type_values(self):
        """Prueba que todos los tipos de documento están disponibles"""
        # Act & Assert
        assert DocumentType.PDF.value == "pdf"
        assert DocumentType.DOCX.value == "docx"
        assert DocumentType.XLSX.value == "xlsx"
        assert DocumentType.PPTX.value == "pptx"
        assert DocumentType.TXT.value == "txt"
        assert DocumentType.CSV.value == "csv"
    
    def test_from_extension_valid(self):
        """Prueba creación desde extensión válida"""
        # Arrange & Act & Assert
        assert DocumentType.from_extension(".pdf") == DocumentType.PDF
        assert DocumentType.from_extension("pdf") == DocumentType.PDF
        assert DocumentType.from_extension(".DOCX") == DocumentType.DOCX
        assert DocumentType.from_extension("txt") == DocumentType.TXT
    
    def test_from_extension_invalid(self):
        """Prueba creación desde extensión inválida"""
        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported file extension"):
            DocumentType.from_extension(".exe")
        
        with pytest.raises(ValueError, match="Unsupported file extension"):
            DocumentType.from_extension("unknown")
        
        with pytest.raises(ValueError, match="Unsupported file extension"):
            DocumentType.from_extension("")
    
    def test_is_valid_extension_true(self):
        """Prueba validación de extensiones válidas"""
        # Act & Assert
        assert DocumentType.is_valid_extension(".pdf") is True
        assert DocumentType.is_valid_extension("docx") is True
        assert DocumentType.is_valid_extension(".XLSX") is True
        assert DocumentType.is_valid_extension("TXT") is True
    
    def test_is_valid_extension_false(self):
        """Prueba validación de extensiones inválidas"""
        # Act & Assert
        assert DocumentType.is_valid_extension(".exe") is False
        assert DocumentType.is_valid_extension("unknown") is False
        assert DocumentType.is_valid_extension("") is False
        assert DocumentType.is_valid_extension(None) is False
    
    def test_get_all_extensions(self):
        """Prueba obtener todas las extensiones soportadas"""
        # Act
        extensions = DocumentType.get_all_extensions()
        
        # Assert
        expected_extensions = ["pdf", "docx", "xlsx", "pptx", "txt", "csv"]
        assert set(extensions) == set(expected_extensions)
        assert len(extensions) == len(expected_extensions)
    
    def test_document_type_string_representation(self):
        """Prueba representación string de DocumentType"""
        # Act & Assert
        assert str(DocumentType.PDF) == "DocumentType.PDF"
        assert DocumentType.PDF.value == "pdf"
    
    def test_document_type_equality(self):
        """Prueba igualdad entre DocumentTypes"""
        # Arrange
        pdf1 = DocumentType.PDF
        pdf2 = DocumentType.PDF
        docx = DocumentType.DOCX
        
        # Act & Assert
        assert pdf1 == pdf2
        assert pdf1 != docx
    
    def test_document_type_in_collection(self):
        """Prueba que DocumentType funciona en colecciones"""
        # Arrange
        doc_types = [DocumentType.PDF, DocumentType.DOCX, DocumentType.TXT]
        
        # Act & Assert
        assert DocumentType.PDF in doc_types
        assert DocumentType.XLSX not in doc_types
        
        # Test en set
        doc_set = {DocumentType.PDF, DocumentType.DOCX}
        assert DocumentType.PDF in doc_set
        assert len(doc_set) == 2
