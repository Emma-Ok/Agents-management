from enum import Enum

class DocumentType(Enum):
    """Representa los tipos de documentos permitidos."""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    TXT = "txt"
    CSV = "csv"

    @classmethod
    def from_extension(cls, extension: str) -> "DocumentType":
        """Devuelve el tipo de documento correspondiente a una extensión dada."""
        extension = extension.lower().replace(".", "")
        for doc_type in cls:
            if doc_type.value == extension:
                return doc_type
        raise ValueError(f"Unsupported file extension: {extension}")
    
    @classmethod
    def is_valid_extension(cls, extension: str) -> bool:
        """Verifica si una extensión de archivo es un tipo de documento válido."""
        if extension is None:
            return False
        try:
            cls.from_extension(extension)
            return True
        except (ValueError, AttributeError):
            return False
    
    @classmethod
    def get_all_extensions(cls) -> list[str]:
        """Devuelve una lista de todas las extensiones soportadas."""
        return [doc_type.value for doc_type in cls]