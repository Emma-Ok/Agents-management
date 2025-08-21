"""
Pruebas unitarias para CreateAgentCommand
"""
import pytest
from unittest.mock import AsyncMock
from src.application.commands.createAgent import CreateAgentCommand
from src.application.dto.agentDto import CreateAgentDTO
from src.domain.entities.agent import Agent
from src.domain.exceptions.domainExceptions import DuplicateAgentNameException


@pytest.mark.unit
class TestCreateAgentCommand:
    """Pruebas para el comando CreateAgent"""
    
    @pytest.fixture
    def command(self, mock_agent_repository, mock_file_storage):
        """Comando con repositorio y file storage mock"""
        return CreateAgentCommand(mock_agent_repository, mock_file_storage)
    
    @pytest.fixture
    def valid_create_dto(self):
        """DTO válido para crear agente"""
        return CreateAgentDTO(
            name="Agente Test",
            prompt="Este es un prompt de prueba con suficientes caracteres."
        )
    
    async def test_create_agent_success(self, command, mock_agent_repository, valid_create_dto, sample_agent):
        """Prueba creación exitosa de agente"""
        # Arrange
        mock_agent_repository.get_agent_by_name.return_value = None  # No existe
        
        # Crear un agente que simule el resultado del guardado
        saved_agent = Agent.create(
            name=valid_create_dto.name,
            prompt=valid_create_dto.prompt
        )
        mock_agent_repository.save_agent.return_value = saved_agent
        
        # Act
        result = await command.execute(valid_create_dto)
        
        # Assert
        assert result.name == valid_create_dto.name
        assert result.prompt == valid_create_dto.prompt
        assert result.documents_count == 0
        assert result.id is not None
        
        # Verificar llamadas al repositorio
        mock_agent_repository.get_agent_by_name.assert_called_once_with(valid_create_dto.name)
        mock_agent_repository.save_agent.assert_called_once()
    
    async def test_create_agent_already_exists(self, command, mock_agent_repository, valid_create_dto, sample_agent):
        """Prueba error cuando el agente ya existe"""
        # Arrange
        mock_agent_repository.get_agent_by_name.return_value = sample_agent  # Ya existe
        
        # Act & Assert
        with pytest.raises(DuplicateAgentNameException, match="already exists"):
            await command.execute(valid_create_dto)
        
        # Verificar que no se intentó guardar
        mock_agent_repository.get_agent_by_name.assert_called_once_with(valid_create_dto.name)
        mock_agent_repository.save_agent.assert_not_called()
    
    async def test_create_agent_with_whitespace_name(self, command, mock_agent_repository):
        """Prueba creación con nombre que tiene espacios en blanco"""
        # Arrange
        dto = CreateAgentDTO(
            name="  Agente con espacios  ",
            prompt="Este es un prompt de prueba con suficientes caracteres."
        )
        mock_agent_repository.get_agent_by_name.return_value = None
        
        # Crear un agente que simule el resultado del guardado
        saved_agent = Agent.create(
            name=dto.name.strip(),  # El nombre se limpia de espacios
            prompt=dto.prompt
        )
        mock_agent_repository.save_agent.return_value = saved_agent
        
        # Act
        result = await command.execute(dto)
        
        # Assert
        # El nombre debe haberse limpiado de espacios
        assert result.name == "Agente con espacios"
        mock_agent_repository.get_agent_by_name.assert_called_once_with("  Agente con espacios  ")
    
    async def test_create_agent_invalid_name_empty(self, command, mock_agent_repository):
        """Prueba error con nombre vacío"""
        # Arrange
        dto = CreateAgentDTO(
            name="",
            prompt="Este es un prompt de prueba con suficientes caracteres."
        )
        mock_agent_repository.get_agent_by_name.return_value = None  # No existe
        
        # Act & Assert
        # El comando verifica duplicados primero, luego Agent.create lanza ValueError por nombre vacío
        with pytest.raises(ValueError, match="Agent name cannot be empty"):
            await command.execute(dto)
        
        # Se verifica nombre duplicado pero no se guarda
        mock_agent_repository.get_agent_by_name.assert_called_once_with("")
        mock_agent_repository.save_agent.assert_not_called()
    
    async def test_create_agent_invalid_prompt_too_short(self, command, mock_agent_repository):
        """Prueba error con prompt demasiado corto"""
        # Arrange
        dto = CreateAgentDTO(
            name="Agente Test Unique",  # Nombre único para evitar conflicto con otros tests
            prompt="Corto"  # Menos de 10 caracteres
        )
        mock_agent_repository.get_agent_by_name.return_value = None  # No existe
        
        # Act & Assert
        # El comando verifica duplicados primero, luego Agent.create lanza ValueError por prompt corto
        with pytest.raises(ValueError, match="Agent prompt must be at least 10 characters"):
            await command.execute(dto)
        
        # Se verifica nombre duplicado pero no se guarda
        mock_agent_repository.get_agent_by_name.assert_called_once_with("Agente Test Unique")
        mock_agent_repository.save_agent.assert_not_called()
    
    async def test_create_agent_repository_error(self, command, mock_agent_repository, valid_create_dto):
        """Prueba manejo de error del repositorio"""
        # Arrange
        mock_agent_repository.get_agent_by_name.return_value = None
        mock_agent_repository.save_agent.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await command.execute(valid_create_dto)
        
        # Verificar que se intentó guardar
        mock_agent_repository.save_agent.assert_called_once()
    
    async def test_create_agent_check_name_error(self, command, mock_agent_repository, valid_create_dto):
        """Prueba manejo de error al verificar nombre existente"""
        # Arrange
        mock_agent_repository.get_agent_by_name.side_effect = Exception("Database connection error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database connection error"):
            await command.execute(valid_create_dto)
        
        # No debe intentar guardar si falla la verificación
        mock_agent_repository.save_agent.assert_not_called()
    
    async def test_create_agent_dto_validation(self, command, mock_agent_repository):
        """Prueba validación del DTO"""
        # Arrange
        mock_agent_repository.get_agent_by_name.return_value = None
        
        # DTO con datos en el límite
        dto = CreateAgentDTO(
            name="A" * 30,  # Máximo permitido
            prompt="X" * 10  # Mínimo permitido
        )
        
        # Crear un agente que simule el resultado del guardado
        saved_agent = Agent.create(
            name=dto.name,
            prompt=dto.prompt
        )
        mock_agent_repository.save_agent.return_value = saved_agent
        
        # Act
        result = await command.execute(dto)
        
        # Assert
        assert result.name == "A" * 30
        assert result.prompt == "X" * 10
        mock_agent_repository.save_agent.assert_called_once()
    
    async def test_create_agent_generates_unique_id(self, command, mock_agent_repository, valid_create_dto):
        """Prueba que se genera un ID único para cada agente"""
        # Arrange
        mock_agent_repository.get_agent_by_name.return_value = None
        
        # Función para simular que cada save devuelve un agente con ID único
        def create_unique_agent(*args, **kwargs):
            return Agent.create(
                name=valid_create_dto.name,
                prompt=valid_create_dto.prompt
            )
        
        mock_agent_repository.save_agent.side_effect = create_unique_agent
        
        # Act
        result1 = await command.execute(valid_create_dto)
        result2 = await command.execute(valid_create_dto)
        
        # Assert
        assert result1.id != result2.id
        assert str(result1.id) != str(result2.id)
        
        # Verificar que se guardaron ambos
        assert mock_agent_repository.save_agent.call_count == 2
