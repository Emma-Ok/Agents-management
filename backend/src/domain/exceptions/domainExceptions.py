class DomainException(Exception):
    """Clase base para todas las excepciones del dominio."""
    pass

class AgentNotFoundException(DomainException):
    """Excepción lanzada cuando no se encuentra un agente."""
    def __init__(self, agent_id: str):
        super().__init__(f"Agent with ID '{agent_id}' not found.")
        self.agent_id = agent_id

class DocumentNotFoundException(DomainException):
    """Excepción lanzada cuando no se encuentra un documento."""
    def __init__(self, document_id: str):
        super().__init__(f"Document with ID '{document_id}' not found.")
        self.document_id = document_id

class FileNotFoundException(DomainException):
    """Excepción lanzada cuando no se encuentra un archivo."""
    def __init__(self, file_id: str):
        super().__init__(f"File with ID '{file_id}' not found.")
        self.file_id = file_id

class FileSizeExceededException(DomainException):
    """Excepción lanzada cuando el tamaño del archivo excede el límite permitido."""
    def __init__(self, size: int, max_size: int):
        super().__init__(f"File size {size} exceeds maximum allowed size {max_size}")
        self.size = size
        self.max_size = max_size

class InvalidFileTypeException(DomainException):
    """Se lanza cuando el tipo de archivo no es válido"""
    def __init__(self, file_type: str):
        super().__init__(f"File type {file_type} is not supported")
        self.file_type = file_type

class StorageException(DomainException):
    """Excepción lanzada para errores de almacenamiento."""
    def __init__(self, message: str):
        super().__init__(message)

class DuplicateAgentNameException(DomainException):
    """Se lanza cuando ya existe un agente con el mismo nombre"""
    def __init__(self, name: str):
        super().__init__(f"Agent with name '{name}' already exists")
        self.name = name

class AgentAlreadyExistsException(DomainException):
    """Excepción lanzada cuando se intenta crear un agente que ya existe."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        super().__init__(f"Agent with name '{agent_name}' already exists")