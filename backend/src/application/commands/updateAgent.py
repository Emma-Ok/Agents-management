from src.domain.value_objects.agentId import AgentId
from src.domain.ports.repositories.agentRepository import AgentRepository
from src.domain.exceptions.domainExceptions import AgentNotFoundException, DuplicateAgentNameException
from src.application.dto.agentDto import UpdateAgentDTO, AgentResponseDTO
import logging

logger = logging.getLogger(__name__)

class UpdateAgentCommand:
    """
    Caso de uso #2: Actualizar un agente existente

    Este comando encapsula la lógica de negocio
    para actualizar un agente existente. Incluye la validación de datos y la interacción con
    el repositorio de agentes.
    """

    def __init__(self, agent_repository: AgentRepository):
        self.agent_repository = agent_repository

    async def execute(self, agent_id: str, update_agent_dto: UpdateAgentDTO) -> AgentResponseDTO:
        """
        Ejecuta el comando para actualizar un agente existente
        1. Verifica que el agente exista
        2. Actualiza los datos del agente
        3. Persiste los cambios
        4. Retorna el DTO de respuesta
        """

        logger.info("Ejecutando UpdateAgentCommand con ID:{agent_id}")

        # Verificar que el agente exista
        existing_agent = await self.agent_repository.get_agent_by_id(AgentId(agent_id))
        if not existing_agent:
            raise AgentNotFoundException(agent_id)

        if update_agent_dto.name and update_agent_dto.name != existing_agent.name:
            # Verificar que no exista otro agente con el mismo nombre
            existing = await self.agent_repository.get_agent_by_name(update_agent_dto.name)
            if existing:
                raise DuplicateAgentNameException(update_agent_dto.name)
            
        # Actualizar el agente
        existing_agent.update(name=update_agent_dto.name, prompt=update_agent_dto.prompt)

        # Persistir cambios
        updated_agent = await self.agent_repository.save_agent(existing_agent)
        # Retornar el DTO de respuesta
        logger.info(f"Agent updated successfully with ID: {existing_agent.id}")

        return AgentResponseDTO(
            id=str(update_agent_dto.name),
            name=existing_agent.name,
            prompt=existing_agent.prompt,
            documents_count=existing_agent.documents_count,
            created_at=existing_agent.created_at,
            updated_at=existing_agent.updated_at
        )