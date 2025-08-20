"""
Configuración global de pruebas con fixtures comunes
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient
import sys
import os

# Agregar src al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.domain.entities.agent import Agent
from src.domain.entities.document import Document
from src.domain.value_objects.agentId import AgentId
from src.domain.value_objects.documentType import DocumentType
from src.domain.ports.services.fileStorage import FileMetadata


@pytest.fixture(scope="session")
def event_loop():
    """Crea un event loop para toda la sesión de pruebas"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_agent_id():
    """Fixture que proporciona un AgentId de prueba"""
    return AgentId.generate()


@pytest.fixture
def sample_agent(sample_agent_id):
    """Fixture que proporciona un Agent de prueba"""
    return Agent(
        id=sample_agent_id,
        name="Agente Test",
        prompt="Este es un prompt de prueba para el agente.",
        created_at=datetime(2025, 1, 1, 10, 0, 0),
        updated_at=datetime(2025, 1, 1, 10, 0, 0),
        documents_count=0
    )


@pytest.fixture
def sample_document(sample_agent_id):
    """Fixture que proporciona un Document de prueba"""
    return Document(
        id="doc-123",
        agent_id=sample_agent_id,
        filename="test_document.pdf",
        document_type=DocumentType.PDF,
        s3_url="https://bucket.s3.region.amazonaws.com/agents/agent-id/test_document.pdf",
        s3_key="agents/agent-id/test_document.pdf",
        file_size=1024,
        created_at=datetime(2025, 1, 1, 10, 0, 0),
        updated_at=datetime(2025, 1, 1, 10, 0, 0)
    )


@pytest.fixture
def sample_file_metadata():
    """Fixture que proporciona FileMetadata de prueba"""
    return FileMetadata(
        key="agents/test-agent/test.pdf",
        url="https://bucket.s3.amazonaws.com/agents/test-agent/test.pdf",
        size=1024,
        content_type="application/pdf",
        etag="abc123"
    )


@pytest.fixture
def mock_agent_repository():
    """Mock del repositorio de agentes"""
    return AsyncMock()


@pytest.fixture
def mock_document_repository():
    """Mock del repositorio de documentos"""
    return AsyncMock()


@pytest.fixture
def mock_file_storage():
    """Mock del servicio de almacenamiento de archivos"""
    return AsyncMock()


@pytest.fixture
def mock_database():
    """Mock de la base de datos MongoDB"""
    mock_db = MagicMock()
    mock_collection = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection
    return mock_db


@pytest.fixture
async def test_client():
    """Cliente HTTP de prueba para endpoints"""
    from main import app
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Fixtures para datos de prueba comunes
@pytest.fixture
def valid_agent_data():
    """Datos válidos para crear un agente"""
    return {
        "name": "Agente de Prueba",
        "prompt": "Este es un prompt de prueba con más de 10 caracteres."
    }


@pytest.fixture
def invalid_agent_data():
    """Datos inválidos para pruebas de validación"""
    return {
        "name": "A",  # Muy corto
        "prompt": "Corto"  # Muy corto
    }


@pytest.fixture
def valid_document_data():
    """Datos válidos para subir un documento"""
    return {
        "filename": "test_document.pdf",
        "content_type": "application/pdf",
        "file_size": 1024,
        "agent_id": "test-agent-id"
    }


@pytest.fixture
def mock_file_upload():
    """Mock de un archivo subido"""
    from io import BytesIO
    mock_file = MagicMock()
    mock_file.filename = "test.pdf"
    mock_file.content_type = "application/pdf"
    mock_file.file = BytesIO(b"test content")
    return mock_file


# Configuración para mocks de AWS S3
@pytest.fixture
def mock_s3_client():
    """Mock del cliente S3"""
    return MagicMock()


# Fixtures para casos de error
@pytest.fixture
def database_error():
    """Simula un error de base de datos"""
    return Exception("Database connection failed")


@pytest.fixture
def s3_error():
    """Simula un error de S3"""
    from botocore.exceptions import ClientError
    return ClientError(
        error_response={
            'Error': {
                'Code': 'NoSuchBucket',
                'Message': 'The specified bucket does not exist'
            }
        },
        operation_name='PutObject'
    )


# Fixtures para configuración de pruebas
@pytest.fixture
def test_settings():
    """Configuración de prueba"""
    from src.infrastructure.config.settings import Settings
    return Settings(
        app_name="AI Agents Test",
        debug=True,
        environment="test",
        mongodb_url="mongodb://localhost:27017/test_db",
        aws_access_key_id="test_key",
        aws_secret_access_key="test_secret",
        aws_s3_bucket_name="test-bucket"
    )
