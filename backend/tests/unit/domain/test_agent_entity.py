"""
Pruebas unitarias para la entidad Agent
"""
import pytest
from datetime import datetime
from src.domain.entities.agent import Agent
from src.domain.value_objects.agentId import AgentId


@pytest.mark.unit
class TestAgentEntity:
    """Pruebas para la entidad Agent"""
    
    def test_create_agent_success(self):
        """Prueba creación exitosa de un agente"""
        # Arrange
        name = "Agente Test"
        prompt = "Este es un prompt de prueba con suficientes caracteres."
        
        # Act
        agent = Agent.create(name, prompt)
        
        # Assert
        assert agent.name == name
        assert agent.prompt == prompt
        assert agent.documents_count == 0
        assert isinstance(agent.id, AgentId)
        assert isinstance(agent.created_at, datetime)
        assert isinstance(agent.updated_at, datetime)
        assert agent.created_at == agent.updated_at
    
    def test_agent_name_validation_empty(self):
        """Prueba validación de nombre vacío"""
        # Arrange
        name = ""
        prompt = "Prompt válido con suficientes caracteres."
        
        # Act & Assert
        with pytest.raises(ValueError, match="Agent name cannot be empty"):
            Agent.create(name, prompt)
    
    def test_agent_name_validation_too_long(self):
        """Prueba validación de nombre demasiado largo"""
        # Arrange
        name = "A" * 31  # 31 caracteres
        prompt = "Prompt válido con suficientes caracteres."
        
        # Act & Assert
        with pytest.raises(ValueError, match="Agent name must be at most 30 characters"):
            Agent.create(name, prompt)
    
    def test_agent_prompt_validation_empty(self):
        """Prueba validación de prompt vacío"""
        # Arrange
        name = "Agente Test"
        prompt = ""
        
        # Act & Assert
        with pytest.raises(ValueError, match="Agent prompt cannot be empty"):
            Agent.create(name, prompt)
    
    def test_agent_prompt_validation_too_short(self):
        """Prueba validación de prompt demasiado corto"""
        # Arrange
        name = "Agente Test"
        prompt = "Corto"  # Menos de 10 caracteres
        
        # Act & Assert
        with pytest.raises(ValueError, match="Agent prompt must be at least 10 characters"):
            Agent.create(name, prompt)
    
    def test_agent_prompt_validation_too_long(self):
        """Prueba validación de prompt demasiado largo"""
        # Arrange
        name = "Agente Test"
        prompt = "A" * 2001  # Más de 2000 caracteres
        
        # Act & Assert
        with pytest.raises(ValueError, match="Agent prompt must be at most 2000 characters"):
            Agent.create(name, prompt)
    
    def test_agent_update_name(self, sample_agent):
        """Prueba actualización del nombre del agente"""
        # Arrange
        new_name = "Nuevo Nombre"
        original_updated_at = sample_agent.updated_at
        
        # Act
        sample_agent.update(name=new_name)
        
        # Assert
        assert sample_agent.name == new_name
        assert sample_agent.updated_at > original_updated_at
    
    def test_agent_update_prompt(self, sample_agent):
        """Prueba actualización del prompt del agente"""
        # Arrange
        new_prompt = "Este es un nuevo prompt con suficientes caracteres."
        original_updated_at = sample_agent.updated_at
        
        # Act
        sample_agent.update(prompt=new_prompt)
        
        # Assert
        assert sample_agent.prompt == new_prompt
        assert sample_agent.updated_at > original_updated_at
    
    def test_agent_update_both_fields(self, sample_agent):
        """Prueba actualización de ambos campos del agente"""
        # Arrange
        new_name = "Nuevo Nombre"
        new_prompt = "Este es un nuevo prompt con suficientes caracteres."
        original_updated_at = sample_agent.updated_at
        
        # Act
        sample_agent.update(name=new_name, prompt=new_prompt)
        
        # Assert
        assert sample_agent.name == new_name
        assert sample_agent.prompt == new_prompt
        assert sample_agent.updated_at > original_updated_at
    
    def test_agent_str_representation(self, sample_agent):
        """Prueba representación string del agente"""
        # Act
        agent_str = str(sample_agent.id)
        
        # Assert
        assert isinstance(agent_str, str)
        assert len(agent_str) > 0
    
    def test_agent_equality(self):
        """Prueba igualdad entre agentes"""
        # Arrange
        agent_id = AgentId.generate()
        name = "Agente Test"
        prompt = "Prompt de prueba con suficientes caracteres."
        created_at = datetime.now()
        
        agent1 = Agent(
            id=agent_id,
            name=name,
            prompt=prompt,
            created_at=created_at,
            updated_at=created_at,
            documents_count=0
        )
        
        agent2 = Agent(
            id=agent_id,
            name=name,
            prompt=prompt,
            created_at=created_at,
            updated_at=created_at,
            documents_count=0
        )
        
        # Act & Assert
        assert agent1.id == agent2.id
        assert agent1.name == agent2.name
        assert agent1.prompt == agent2.prompt
