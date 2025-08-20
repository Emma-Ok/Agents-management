from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class CreateAgentDTO:
    """
    Data Transfer Object para la creación de un nuevo agente
    """
    name: str
    prompt: str

@dataclass
class UpdateAgentDTO:
    """
    Data Transfer Object para la actualización de un agente existente
    """
    name: Optional[str] = None
    prompt: Optional[str] = None

@dataclass
class AgentResponseDTO:
    """
    Data Transfer Object para la respuesta de un agente
    """
    id: str
    name: str
    prompt: str
    documents_count: int
    created_at: datetime
    updated_at: datetime

@dataclass
class AgentListItemDTO:
    """
    Data Transfer Object para un elemento de la lista de agentes
    """
    id: str
    documents_count: int
    created_at: datetime