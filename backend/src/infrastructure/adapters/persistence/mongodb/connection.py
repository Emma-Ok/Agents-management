import motor.motor_asyncio
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from typing import Optional
import logging
from ....config.settings import get_settings

logger = logging.getLogger(__name__)

class MongoDBConnection:
    """
    Maneja la conexión a MongoDB Atlas usando Motor (async MongoDB driver)
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.database = None
    
    async def connect(self):
        """Establece la conexión con MongoDB Atlas"""
        try:
            # Crear cliente usando Motor para async operations con configuración SSL mejorada
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                self.settings.mongodb_url,
                server_api=ServerApi('1'),
                maxPoolSize=self.settings.mongodb_max_pool_size,
                minPoolSize=self.settings.mongodb_min_pool_size,
                # Configuración SSL/TLS mejorada
               tls=True,  # Usar TLS en lugar de ssl=True
                tlsAllowInvalidCertificates=False,  # Validar certificados
                serverSelectionTimeoutMS=30000,  # 30 segundos timeout
                connectTimeoutMS=30000,  # 30 segundos timeout de conexión
                socketTimeoutMS=30000,  # 30 segundos timeout de socket
                heartbeatFrequencyMS=10000,  # Heartbeat cada 10 segundos
                retryWrites=True # 10 segundos timeout de socket
            )
            
            # Ping para verificar la conexión
            await self.client.admin.command('ping')
            
            self.database = self.client[self.settings.mongodb_db_name]
            logger.info(f"Successfully connected to MongoDB Atlas database: {self.settings.mongodb_db_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB Atlas: {e}")
            # Limpiar el cliente si la conexión falló
            self.client = None
            self.database = None
            raise
    
    def test_sync_connection(self):
        """Prueba de conexión síncrona para verificar credenciales"""
        try:
            sync_client = MongoClient(self.settings.mongodb_url, server_api=ServerApi('1'))
            sync_client.admin.command('ping')
            logger.info("Sync ping successful - MongoDB Atlas connection verified")
            sync_client.close()
            return True
        except Exception as e:
            logger.error(f"Sync connection test failed: {e}")
            return False
    
    async def disconnect(self):
        """Cierra la conexión con MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def create_indexes(self):
        """Crea los índices necesarios en las colecciones"""
        if self.database is None:
            raise Exception("Database not connected")
        
        try:
            # Índices para la colección de agentes
            agents_collection = self.database.agents
            
            # Índice único en el nombre del agente
            await agents_collection.create_index("name", unique=True)
            
            # Índice en fecha de creación para ordenamiento
            await agents_collection.create_index([("created_at", -1)])
            
            # Índice en fecha de actualización
            await agents_collection.create_index("updated_at")
            
            # Índice compuesto para búsquedas por nombre (case-insensitive)
            await agents_collection.create_index([("name", "text")])
            
            logger.info("Agents collection indexes created")
            
            # Índices para la colección de documentos
            documents_collection = self.database.documents
            
            # Índice en agent_id para queries por agente (más importante)
            await documents_collection.create_index("agent_id")
            
            # Índice único en s3_key para evitar duplicados
            await documents_collection.create_index("s3_key", unique=True)
            
            # Índice en fecha de creación para ordenamiento
            await documents_collection.create_index([("created_at", -1)])
            
            # Índice en filename para búsquedas de texto
            await documents_collection.create_index([("filename", "text")])
            
            # Índice en tipo de documento
            await documents_collection.create_index("document_type")
            
            # Índice compuesto para queries complejas (agent_id + created_at)
            await documents_collection.create_index([
                ("agent_id", 1),
                ("created_at", -1)
            ])
            
            # Índice compuesto para búsquedas por agente y tipo
            await documents_collection.create_index([
                ("agent_id", 1),
                ("document_type", 1)
            ])
            
            logger.info("Documents collection indexes created")
            logger.info("All database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise

# Instancia global de la conexión (será inicializada al usarse)
_mongodb_connection: Optional[MongoDBConnection] = None

async def get_mongodb() -> MongoDBConnection:
    """Retorna la instancia de conexión MongoDB"""
    global _mongodb_connection
    if _mongodb_connection is None:
        _mongodb_connection = MongoDBConnection()
    
    if not _mongodb_connection.client:
        await _mongodb_connection.connect()
    return _mongodb_connection


async def get_database():
    """Función para obtener la base de datos - requerida por container.py"""
    try:
        mongodb = await get_mongodb()
        if mongodb.database is None:
            raise Exception("Database connection failed - database is None")
        return mongodb.database
    except Exception as e:
        logger.error(f"Failed to get database: {e}")
        raise Exception(f"Cannot initialize database connection: {e}")


async def close_mongodb():
    """Cierra la conexión MongoDB"""
    global _mongodb_connection
    if _mongodb_connection:
        await _mongodb_connection.disconnect()
