"""
Pruebas de integración para endpoints de agentes
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from datetime import datetime


@pytest.mark.api
@pytest.mark.integration
class TestAgentsAPI:
    """Pruebas de integración para API de agentes"""
    
    @pytest.fixture
    async def client(self):
        """Cliente HTTP para pruebas"""
        from httpx import ASGITransport
        from main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def mock_agent_data(self):
        """Datos de agente para mocks"""
        return {
            "id": "test-agent-123",
            "name": "Agente Test API",
            "prompt": "Este es un prompt de prueba para API.",
            "documents_count": 0,
            "created_at": datetime(2025, 1, 1, 10, 0, 0),
            "updated_at": datetime(2025, 1, 1, 10, 0, 0)
        }
    
    @patch('src.infrastructure.api.dependencies.get_create_agent_command')
    async def test_create_agent_success(self, mock_get_command, client):
        """Prueba creación exitosa de agente via API"""
        # Arrange
        mock_command = AsyncMock()
        mock_result = AsyncMock()
        mock_result.id = "test-agent-123"
        mock_result.name = "Agente Test API"
        mock_result.prompt = "Este es un prompt de prueba para API."
        mock_result.documents_count = 0
        mock_result.created_at = datetime(2025, 1, 1, 10, 0, 0)
        mock_result.updated_at = datetime(2025, 1, 1, 10, 0, 0)
        
        mock_command.execute.return_value = mock_result
        mock_get_command.return_value = mock_command
        
        # Act
        response = await client.post(
            "/api/v1/agents",
            json={
                "name": "Agente Test API",
                "prompt": "Este es un prompt de prueba para API."
            }
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Agente Test API"
        assert data["prompt"] == "Este es un prompt de prueba para API."
        assert data["documents_count"] == 0
        assert "id" in data
    
    @patch('src.infrastructure.api.dependencies.get_create_agent_command')
    async def test_create_agent_validation_error(self, mock_get_command, client):
        """Prueba error de validación en creación de agente"""
        # Arrange
        mock_command = AsyncMock()
        mock_get_command.return_value = mock_command
        
        # Act - nombre muy corto
        response = await client.post(
            "/api/v1/agents",
            json={
                "name": "A",  # Muy corto
                "prompt": "Este es un prompt de prueba para API."
            }
        )
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @patch('src.infrastructure.api.dependencies.get_agent_detail_query')
    async def test_get_agent_success(self, mock_get_query, client, mock_agent_data):
        """Prueba obtener agente existente via API"""
        # Arrange
        mock_query = AsyncMock()
        mock_result = {
            "agent": mock_agent_data,
            "documents": []
        }
        mock_query.execute.return_value = mock_result
        mock_get_query.return_value = mock_query
        
        agent_id = "test-agent-123"
        
        # Act
        response = await client.get(f"/api/v1/agents/{agent_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "agent" in data
        assert "documents" in data
        assert data["agent"]["id"] == agent_id
        assert data["agent"]["name"] == "Agente Test API"
    
    @patch('src.infrastructure.api.dependencies.get_agent_detail_query')
    async def test_get_agent_not_found(self, mock_get_query, client):
        """Prueba obtener agente que no existe"""
        # Arrange
        from src.domain.exceptions.domainExceptions import AgentNotFoundException
        mock_query = AsyncMock()
        mock_query.execute.side_effect = AgentNotFoundException("nonexistent-agent")
        mock_get_query.return_value = mock_query
        
        # Act
        response = await client.get("/api/v1/agents/nonexistent-agent")
        
        # Assert
        assert response.status_code == 404
    
    @patch('src.infrastructure.api.dependencies.get_update_agent_command')
    async def test_update_agent_success(self, mock_get_command, client, mock_agent_data):
        """Prueba actualización exitosa de agente"""
        # Arrange
        mock_command = AsyncMock()
        updated_agent = mock_agent_data.copy()
        updated_agent["name"] = "Agente Actualizado"
        mock_command.execute.return_value = updated_agent
        mock_get_command.return_value = mock_command
        
        agent_id = "test-agent-123"
        
        # Act
        response = await client.put(
            f"/api/v1/agents/{agent_id}",
            json={
                "name": "Agente Actualizado"
            }
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Agente Actualizado"
    
    @patch('src.infrastructure.api.dependencies.get_delete_agent_command')
    async def test_delete_agent_success(self, mock_get_command, client):
        """Prueba eliminación exitosa de agente"""
        # Arrange
        mock_command = AsyncMock()
        mock_command.execute.return_value = None
        mock_get_command.return_value = mock_command
        
        agent_id = "test-agent-123"
        
        # Act
        response = await client.delete(f"/api/v1/agents/{agent_id}")
        
        # Assert
        assert response.status_code == 204
    
    @patch('src.infrastructure.api.dependencies.get_list_agents_query')
    async def test_list_agents_success(self, mock_get_query, client, mock_agent_data):
        """Prueba listado de agentes"""
        # Arrange
        mock_query = AsyncMock()
        mock_result = {
            "agents": [mock_agent_data],
            "total": 1,
            "page": 1,
            "per_page": 20
        }
        mock_query.execute.return_value = mock_result
        mock_get_query.return_value = mock_query
        
        # Act
        response = await client.get("/api/v1/agents")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "total" in data
        assert len(data["agents"]) == 1
        assert data["agents"][0]["name"] == "Agente Test API"
    
    @patch('src.infrastructure.api.dependencies.get_list_agents_query')
    async def test_list_agents_with_pagination(self, mock_get_query, client):
        """Prueba listado de agentes con paginación"""
        # Arrange
        mock_query = AsyncMock()
        mock_result = {
            "agents": [],
            "total": 50,
            "page": 2,
            "per_page": 10
        }
        mock_query.execute.return_value = mock_result
        mock_get_query.return_value = mock_query
        
        # Act
        response = await client.get("/api/v1/agents?skip=10&limit=10")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 50
        assert data["page"] == 2
        assert data["per_page"] == 10
        
        # Verificar que se llamó con los parámetros correctos
        mock_query.execute.assert_called_once_with(skip=10, limit=10, search=None)
