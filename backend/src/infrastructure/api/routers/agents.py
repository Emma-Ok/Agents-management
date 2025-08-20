from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from src.application.commands.createAgent import CreateAgentCommand
from src.application.commands.updateAgent import UpdateAgentCommand
from src.application.commands.deleteAgent import DeleteAgentCommand
from src.application.queries.listAgents import ListAgentsQuery
from src.application.queries.getAgentDetail import GetAgentDetailQuery
from src.application.dto.agentDto import AgentResponseDTO, AgentListItemDTO, CreateAgentDTO, UpdateAgentDTO
from src.infrastructure.api.dependencies import (
    get_create_agent_command,
    get_update_agent_command,
    get_delete_agent_command,
    get_list_agents_query,
    get_agent_detail_query
)

router = APIRouter(prefix="/agents", tags=["agents"])

# Modelos Pydantic para requests/responses
class CreateAgentRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Agent name")
    prompt: str = Field(..., min_length=10, max_length=5000, description="Agent prompt")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Customer Support Agent",
                "prompt": "You are a helpful customer support agent..."
            }
        }

class UpdateAgentRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    prompt: Optional[str] = Field(None, min_length=10, max_length=5000)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new agent",
    description="Creates a new AI agent with the specified name and prompt"
)
async def create_agent(
    request: CreateAgentRequest,
    command: CreateAgentCommand = Depends(get_create_agent_command)
):
    """
    Create a new AI agent.
    
    - **name**: Unique name for the agent (3-100 characters)
    - **prompt**: System prompt that defines the agent's behavior (10-5000 characters)
    """
    dto = CreateAgentDTO(name=request.name, prompt=request.prompt)
    result = await command.execute(dto)
    return result

@router.get(
    "",
    summary="List all agents",
    description="Returns a paginated list of all agents"
)
async def list_agents(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    search: Optional[str] = Query(None, description="Search term"),
    query: ListAgentsQuery = Depends(get_list_agents_query)
):
    """
    List all agents with pagination.
    
    Returns agents sorted by creation date (newest first).
    """
    result = await query.execute(skip=skip, limit=limit, search=search)
    return result

@router.get(
    "/{agent_id}",
    summary="Get agent details",
    description="Returns detailed information about an agent including its documents"
)
async def get_agent(
    agent_id: str,
    query: GetAgentDetailQuery = Depends(get_agent_detail_query)
):
    """
    Get detailed information about a specific agent.
    
    Returns the agent data along with all associated documents.
    """
    result = await query.execute(agent_id)
    return result

@router.put(
    "/{agent_id}",
    summary="Update an agent",
    description="Updates the name and/or prompt of an existing agent"
)
async def update_agent(
    agent_id: str,
    request: UpdateAgentRequest,
    command: UpdateAgentCommand = Depends(get_update_agent_command)
):
    """
    Update an existing agent.
    
    Only the provided fields will be updated.
    """
    dto = UpdateAgentDTO(name=request.name, prompt=request.prompt)
    result = await command.execute(agent_id, dto)
    return result

@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an agent",
    description="Deletes an agent and all its associated documents"
)
async def delete_agent(
    agent_id: str,
    command: DeleteAgentCommand = Depends(get_delete_agent_command)
):
    """
    Delete an agent.
    
    This will also delete all documents associated with the agent
    from both the database and S3 storage.
    """
    await command.execute(agent_id)
    return None