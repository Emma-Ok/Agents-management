"""
Pruebas unitarias para MongoAgentRepository
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from src.infrastructure.adapters.persistence.mongodb.repositories.mongoAgentRepository import MongoAgentRepository
from src.domain.entities.agent import Agent
from src.domain.value_objects.agentId import AgentId


@pytest.mark.unit
class TestMongoAgentRepository:
    """Pruebas para MongoAgentRepository"""
    
    @pytest.fixture
    def mock_collection(self):
        """Mock de la colección MongoDB"""
        collection = MagicMock()
        
        # Configurar métodos async específicos
        collection.find_one = AsyncMock()
        collection.replace_one = AsyncMock()
        collection.delete_one = AsyncMock()
        collection.count_documents = AsyncMock()
        
        return collection
    
    @pytest.fixture
    def mock_database(self, mock_collection):
        """Mock de la base de datos MongoDB"""
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        return mock_db
    
    @pytest.fixture
    def repository(self, mock_database):
        """Repositorio con base de datos mock"""
        return MongoAgentRepository(mock_database)
    
    @pytest.fixture
    def agent_document_data(self):
        """Datos de documento MongoDB para un agente"""
        return {
            "_id": "test-agent-123",
            "name": "Agente Test",
            "prompt": "Este es un prompt de prueba.",
            "documents_count": 5,
            "created_at": datetime(2025, 1, 1, 10, 0, 0),
            "updated_at": datetime(2025, 1, 1, 11, 0, 0)
        }
    
    @pytest.mark.asyncio
    async def test_save_agent_success(self, repository, mock_collection, sample_agent):
        """Prueba guardado exitoso de agente"""
        # Arrange
        mock_collection.replace_one.return_value = AsyncMock(modified_count=1)
        
        # Act
        result = await repository.save_agent(sample_agent)
        
        # Assert
        assert result == sample_agent
        mock_collection.replace_one.assert_called_once()
        
        # Verificar argumentos de la llamada
        call_args = mock_collection.replace_one.call_args
        filter_dict = call_args[0][0]
        document_dict = call_args[0][1]
        
        assert filter_dict == {"_id": str(sample_agent.id)}
        assert document_dict["name"] == sample_agent.name
        assert document_dict["prompt"] == sample_agent.prompt
    
    @pytest.mark.asyncio
    async def test_get_agent_by_id_found(self, repository, mock_collection, agent_document_data):
        """Prueba obtener agente por ID cuando existe"""
        # Arrange
        agent_id = AgentId("test-agent-123")
        mock_collection.find_one.return_value = agent_document_data
        
        # Act
        result = await repository.get_agent_by_id(agent_id)
        
        # Assert
        assert result is not None
        assert result.name == "Agente Test"
        assert result.prompt == "Este es un prompt de prueba."
        assert result.documents_count == 5
        assert str(result.id) == "test-agent-123"
        
        mock_collection.find_one.assert_called_once_with({"_id": "test-agent-123"})
    
    @pytest.mark.asyncio
    async def test_get_agent_by_id_not_found(self, repository, mock_collection):
        """Prueba obtener agente por ID cuando no existe"""
        # Arrange
        agent_id = AgentId("nonexistent-agent")
        mock_collection.find_one.return_value = None
        
        # Act
        result = await repository.get_agent_by_id(agent_id)
        
        # Assert
        assert result is None
        mock_collection.find_one.assert_called_once_with({"_id": "nonexistent-agent"})
    
    @pytest.mark.asyncio
    async def test_get_agent_by_name_found(self, repository, mock_collection, agent_document_data):
        """Prueba obtener agente por nombre cuando existe"""
        # Arrange
        agent_name = "Agente Test"
        mock_collection.find_one.return_value = agent_document_data
        
        # Act
        result = await repository.get_agent_by_name(agent_name)
        
        # Assert
        assert result is not None
        assert result.name == agent_name
        mock_collection.find_one.assert_called_once_with({"name": agent_name})
    
    @pytest.mark.asyncio
    async def test_get_agent_by_name_not_found(self, repository, mock_collection):
        """Prueba obtener agente por nombre cuando no existe"""
        # Arrange
        agent_name = "Agente Inexistente"
        mock_collection.find_one.return_value = None
        
        # Act
        result = await repository.get_agent_by_name(agent_name)
        
        # Assert
        assert result is None
        mock_collection.find_one.assert_called_once_with({"name": agent_name})
    
    @pytest.mark.asyncio
    async def test_get_all_agents(self, repository, mock_collection, agent_document_data):
        """Prueba obtener todos los agentes con paginación"""
        # Arrange
        # Crear un mock cursor que soporte el chaining de métodos
        mock_cursor = MagicMock()
        
        # Configurar el chaining: find().skip().limit().sort()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        
        # Configurar el async iteration
        async def mock_async_iter(self):
            yield agent_document_data
        
        mock_cursor.__aiter__ = mock_async_iter
        mock_collection.find.return_value = mock_cursor
        
        # Act
        result = await repository.get_all(skip=0, limit=10)
        
        # Assert
        assert len(result) == 1
        assert result[0].name == "Agente Test"
        
        mock_collection.find.assert_called_once()
        mock_cursor.skip.assert_called_once_with(0)
        mock_cursor.limit.assert_called_once_with(10)
        mock_cursor.sort.assert_called_once_with("created_at", -1)
    
    @pytest.mark.asyncio
    async def test_delete_agent_success(self, repository, mock_collection):
        """Prueba eliminación exitosa de agente"""
        # Arrange
        agent_id = AgentId("test-agent-123")
        mock_collection.delete_one.return_value = AsyncMock(deleted_count=1)
        
        # Act
        result = await repository.delete_agent(agent_id)
        
        # Assert
        assert result is True
        mock_collection.delete_one.assert_called_once_with({"_id": "test-agent-123"})
    
    @pytest.mark.asyncio
    async def test_delete_agent_not_found(self, repository, mock_collection):
        """Prueba eliminación de agente que no existe"""
        # Arrange
        agent_id = AgentId("nonexistent-agent")
        mock_collection.delete_one.return_value = AsyncMock(deleted_count=0)
        
        # Act
        result = await repository.delete_agent(agent_id)
        
        # Assert
        assert result is False
        mock_collection.delete_one.assert_called_once_with({"_id": "nonexistent-agent"})
    
    @pytest.mark.asyncio
    async def test_exists_agent_true(self, repository, mock_collection):
        """Prueba verificación de existencia cuando el agente existe"""
        # Arrange
        agent_id = AgentId("test-agent-123")
        mock_collection.count_documents.return_value = 1
        
        # Act
        result = await repository.exists(agent_id)
        
        # Assert
        assert result is True
        mock_collection.count_documents.assert_called_once_with(
            {"_id": "test-agent-123"}, limit=1
        )
    
    @pytest.mark.asyncio
    async def test_exists_agent_false(self, repository, mock_collection):
        """Prueba verificación de existencia cuando el agente no existe"""
        # Arrange
        agent_id = AgentId("nonexistent-agent")
        mock_collection.count_documents.return_value = 0
        
        # Act
        result = await repository.exists(agent_id)
        
        # Assert
        assert result is False
        mock_collection.count_documents.assert_called_once_with(
            {"_id": "nonexistent-agent"}, limit=1
        )
    
    @pytest.mark.asyncio
    async def test_count_agents(self, repository, mock_collection):
        """Prueba contar total de agentes"""
        # Arrange
        mock_collection.count_documents.return_value = 42
        
        # Act
        result = await repository.count()
        
        # Assert
        assert result == 42
        mock_collection.count_documents.assert_called_once_with({})
    
    @pytest.mark.asyncio
    async def test_to_domain_conversion(self, repository, agent_document_data):
        """Prueba conversión de documento MongoDB a entidad de dominio"""
        # Act
        agent = repository._to_domain(agent_document_data)
        
        # Assert
        assert isinstance(agent, Agent)
        assert str(agent.id) == "test-agent-123"
        assert agent.name == "Agente Test"
        assert agent.prompt == "Este es un prompt de prueba."
        assert agent.documents_count == 5
    
    @pytest.mark.asyncio
    async def test_to_model_conversion(self, repository, sample_agent):
        """Prueba conversión de entidad de dominio a documento MongoDB"""
        # Act
        model = repository._to_model(sample_agent)
        
        # Assert
        assert model["_id"] == str(sample_agent.id)
        assert model["name"] == sample_agent.name
        assert model["prompt"] == sample_agent.prompt
        assert model["documents_count"] == sample_agent.documents_count
        assert model["created_at"] == sample_agent.created_at
        assert model["updated_at"] == sample_agent.updated_at
    
    def test_repository_initialization_error(self):
        """Prueba error en inicialización con base de datos None"""
        # Act & Assert
        with pytest.raises(Exception, match="Database cannot be None"):
            MongoAgentRepository(None)
