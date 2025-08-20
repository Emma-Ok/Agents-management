from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from ..value_objects.agentId import AgentId

@dataclass
class Agent:
    """
    Entidad Agente - Representa un agente de IA
    
    Esta es la entidad principal del dominio. Un agente tiene:
    - Un identificador único
    - Un nombre descriptivo
    - Un prompt que define su comportamiento
    - Timestamps de auditoría
    """

    id: AgentId
    name: str
    prompt: str
    created_at: datetime
    updated_at: datetime
    documents_count: int = 0
    
    def __post_init__(self):
        """Método llamado después de la inicialización del dataclass."""
        self._validate_name()
        self._validate_prompt()

    def _validate_name(self):
        """Valida que el nombre del agente no esté vacío."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Agent name cannot be empty and must be a string.")
        if len(self.name) > 30:
            raise ValueError("Agent name must be at most 30 characters long.")

    def _validate_prompt(self):
        """Valida que el prompt del agente no esté vacío."""
        if not self.prompt or not isinstance(self.prompt, str):
            raise ValueError("Agent prompt cannot be empty and must be a string.")
        if len(self.prompt) < 10:
            raise ValueError("Agent prompt must be at least 10 characters long.")
        if len(self.prompt) > 2000:
            raise ValueError("Agent prompt must be at most 2000 characters long.")
        self.prompt = self.prompt.strip()

    def update(self, name: Optional[str] = None, prompt: Optional[str] = None) -> None:
        """Actualiza los atributos del agente con validación previa."""
        if name is not None:
            self._validate_name()
            self.name = name.strip()
        if prompt is not None:
            self._validate_prompt()
            self.prompt = prompt.strip()

        self.updated_at = datetime.now()


    @classmethod
    def create(cls, name: str, prompt: str) -> "Agent":
        """Crea una nueva instancia de Agent.
           Encapsula la lógica de creación y validación.
        """
        now = datetime.now()
        return cls(
            id=AgentId.generate(),
            name=name,  
            prompt=prompt,
            created_at=now,
            updated_at=now,
            documents_count=0  # Inicialmente sin documentos
        )
