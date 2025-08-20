from dataclasses import dataclass
from uuid import UUID, uuid4
from typing import Optional

@dataclass(frozen=True)
class AgentId:
    '''Representa un identificador único para un agente.'''
    value: str

    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Invalid Agent ID")

    @classmethod
    def generate(cls) -> "AgentId":
        """Genera un nuevo AgentId único."""
        return cls(value=str(uuid4()))
    
    def __str__(self) -> str:
        return self.value