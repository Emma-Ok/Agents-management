"""
Excepciones específicas de reglas de negocio
"""

from .domainExceptions import DomainException

class BusinessRuleException(DomainException):
    """Excepción base para violaciones de reglas de negocio"""
    pass

class MaxDocumentsPerAgentExceededException(BusinessRuleException):
    """Se excedió el límite máximo de documentos por agente"""
    
    def __init__(self, agent_id: str, current_count: int, max_allowed: int):
        self.agent_id = agent_id
        self.current_count = current_count
        self.max_allowed = max_allowed
        super().__init__(
            f"El agente {agent_id} ya tiene {current_count} documentos. "
            f"El límite máximo es {max_allowed} documentos por agente."
        )

class DuplicateDocumentException(BusinessRuleException):
    """Ya existe un documento con el mismo nombre para este agente"""
    
    def __init__(self, agent_id: str, filename: str):
        self.agent_id = agent_id
        self.filename = filename
        super().__init__(
            f"Ya existe un documento con el nombre '{filename}' para el agente {agent_id}"
        )

class AgentHasDocumentsException(BusinessRuleException):
    """No se puede eliminar un agente que tiene documentos asociados"""
    
    def __init__(self, agent_id: str, documents_count: int):
        self.agent_id = agent_id
        self.documents_count = documents_count
        super().__init__(
            f"No se puede eliminar el agente {agent_id} porque tiene {documents_count} "
            f"documento(s) asociado(s). Elimine los documentos primero."
        )

class S3StorageException(BusinessRuleException):
    """Error en el almacenamiento S3"""
    
    def __init__(self, operation: str, details: str):
        self.operation = operation
        self.details = details
        super().__init__(f"Error en S3 durante {operation}: {details}")

class DocumentSizeExceededException(BusinessRuleException):
    """El tamaño del documento excede el límite permitido"""
    
    def __init__(self, filename: str, size_mb: float, max_size_mb: int):
        self.filename = filename
        self.size_mb = size_mb
        self.max_size_mb = max_size_mb
        super().__init__(
            f"El documento '{filename}' ({size_mb:.2f}MB) excede el tamaño máximo "
            f"permitido de {max_size_mb}MB"
        )

class UnsupportedFileTypeException(BusinessRuleException):
    """Tipo de archivo no soportado"""
    
    def __init__(self, filename: str, file_type: str, supported_types: list):
        self.filename = filename
        self.file_type = file_type
        self.supported_types = supported_types
        super().__init__(
            f"El tipo de archivo '{file_type}' del documento '{filename}' no está "
            f"soportado. Tipos soportados: {', '.join(supported_types)}"
        )
