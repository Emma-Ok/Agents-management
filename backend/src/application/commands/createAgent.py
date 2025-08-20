from src.domain.entities.agent import Agent
from src.domain.ports.repositories.agentRepository import AgentRepository
from src.domain.ports.services.fileStorage import FileStorage
from src.domain.exceptions.domainExceptions import DuplicateAgentNameException
from ..dto.agentDto import CreateAgentDTO, AgentResponseDTO
import logging

logger = logging.getLogger(__name__)

class CreateAgentCommand:
    """
    Caso de uso #1: Crear un nuevo agente

    Siguiendo la arquitectura hexagonal, este comando encapsula la lógica de negocio
    para crear un nuevo agente. Incluye la validación de datos y la interacción con
    el repositorio de agentes.
    """

    def __init__(self, agent_repository: AgentRepository, file_storage: FileStorage):
        self.agent_repository = agent_repository
        self.file_storage = file_storage

    async def execute(self, create_agent_dto: CreateAgentDTO) -> AgentResponseDTO:
        """
        Siguiendo el comando para la creación del agente
        1. Verifica que no exista un agente con el mismo nombre
        2. Crea la entidad Agent del dominio
        3. Persiste el agente
        4. Retorna el DTO de respuesta
        """


        logger.info("Ejecutando CreateAgentCommand con datos: %s", create_agent_dto)

        # Verificar que no exista un agente con el mismo nombre
        existing_agent = await self.agent_repository.get_agent_by_name(create_agent_dto.name)
        if existing_agent:
            logger.warning(f"Agent with name '{create_agent_dto.name}' already exists")
            raise DuplicateAgentNameException(create_agent_dto.name)
        
        #Crear la entidad del dominio

        agent = Agent.create(
            name=create_agent_dto.name,
            prompt=create_agent_dto.prompt
        )

        #Persistencia del agente
        saved_agent = await self.agent_repository.save_agent(agent)

        #Verificar que el agente fue guardado correctamente
        if saved_agent is None:
            logger.error("Failed to save agent.")
            raise Exception("Failed to save agent.")

        # Crear carpeta en S3 para el agente (operación opcional)
        agent_folder_key = f"agents/{saved_agent.id}/"
        try:
            folder_created = await self.file_storage.create_folder(agent_folder_key)
            if folder_created:
                logger.info(f"✅ Created S3 folder for agent: {agent_folder_key}")
            else:
                logger.warning(f"⚠️ Could not create S3 folder for agent: {agent_folder_key}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create S3 folder for agent {saved_agent.id}: {e}")
            # La carpeta se creará automáticamente cuando se suba el primer documento

        #Retornar el DTO de respuesta
        logger.info(f"Agent created successfully with ID: {saved_agent.id}")

        return AgentResponseDTO(
            id=str(saved_agent.id),
            name=saved_agent.name,
            prompt=saved_agent.prompt,
            documents_count=saved_agent.documents_count,
            created_at=saved_agent.created_at,
            updated_at=saved_agent.updated_at
            )
        
