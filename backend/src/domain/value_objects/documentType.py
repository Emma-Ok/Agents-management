from enum import Enum

class DocumentType(Enum):
    """Representa los tipos de documentos permitidos."""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"

    @classmethod
    def from_extension(cls, extension: str) -> "DocumentType":
        """Devuelve el tipo de documento correspondiente a una extensión dada."""
        extension = extension.lower().replace(".", "")
        for doc_type in cls:
            if doc_type.value == extension:
                return doc_type
        raise ValueError(f"Unknown document type for extension: {extension}")
    
    @classmethod
    def is_valid_extension(cls, extension: str) -> bool:
        """Verifica si una extensión de archivo es un tipo de documento válido."""
        try:
            cls.from_extension(extension)
            return True
        except ValueError:
            return False