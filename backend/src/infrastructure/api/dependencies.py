"""
Inyección de dependencias para FastAPI usando el container
"""
from fastapi import Depends
from src.infrastructure.config.container import get_container, Container
from src.application.commands.createAgent import CreateAgentCommand
from src.application.commands.updateAgent import UpdateAgentCommand
from src.application.commands.deleteAgent import DeleteAgentCommand
from src.application.commands.uploadDocument import UploadDocumentCommand
from src.application.commands.deleteDocument import DeleteDocumentCommand
from src.application.queries.listAgents import ListAgentsQuery
from src.application.queries.getAgentDetail import GetAgentDetailQuery

# Obtener container
def get_app_container() -> Container:
    """Retorna el container de la aplicación"""
    return get_container()

# Comandos
async def get_create_agent_command(
    container: Container = Depends(get_app_container)
) -> CreateAgentCommand:
    """Inyecta el comando para crear agentes"""
    return await container.create_agent_command()

async def get_update_agent_command(
    container: Container = Depends(get_app_container)
) -> UpdateAgentCommand:
    """Inyecta el comando para actualizar agentes"""
    return await container.update_agent_command()

async def get_delete_agent_command(
    container: Container = Depends(get_app_container)
) -> DeleteAgentCommand:
    """Inyecta el comando para eliminar agentes"""
    return await container.delete_agent_command()

async def get_upload_document_command(
    container: Container = Depends(get_app_container)
) -> UploadDocumentCommand:
    """Inyecta el comando para subir documentos"""
    return await container.upload_document_command()

async def get_delete_document_command(
    container: Container = Depends(get_app_container)
) -> DeleteDocumentCommand:
    """Inyecta el comando para eliminar documentos"""
    return await container.delete_document_command()

# Queries
async def get_list_agents_query(
    container: Container = Depends(get_app_container)
) -> ListAgentsQuery:
    """Inyecta la query para listar agentes"""
    return await container.list_agents_query()

async def get_agent_detail_query(
    container: Container = Depends(get_app_container)
) -> GetAgentDetailQuery:
    """Inyecta la query para obtener detalle de agente"""
    return await container.get_agent_detail_query()