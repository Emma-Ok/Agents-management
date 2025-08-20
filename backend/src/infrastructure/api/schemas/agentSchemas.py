from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AgentCreateSchema(BaseModel):
    name: str = Field(..., max_length=30, description="Nombre del agente")
    prompt: str = Field(..., min_length=10, max_length=2000, description="Prompt del agente")

class AgentUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=30)
    prompt: Optional[str] = Field(None, min_length=10, max_length=2000)

class AgentResponseSchema(BaseModel):
    id: str
    name: str
    prompt: str
    created_at: datetime
    updated_at: datetime
    documents_count: int
