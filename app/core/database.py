import ssl
import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import get_settings

settings = get_settings()


class Database:
    """Async MongoDB connection manager for scalability."""
    
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None
    connected: bool = False


db_instance = Database()


async def connect_to_mongo():
    """Create MongoDB connection pool (optional - skips if no URI configured)."""
    if not settings.mongodb_uri or settings.mongodb_uri == "mongodb://localhost:27017":
        print("MongoDB not configured - running without database (in-memory mode)")
        db_instance.connected = False
        return
    
    try:
        # Create SSL context with relaxed settings for cloud compatibility
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE  # Allow self-signed certs
        
        # Connection settings optimized for cloud deployment
        db_instance.client = AsyncIOMotorClient(
            settings.mongodb_uri,
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=5000,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=30000,
            retryWrites=True,
            retryReads=True,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
        )
        db_instance.db = db_instance.client[settings.database_name]
        
        # Verify connection
        await db_instance.client.admin.command("ping")
        db_instance.connected = True
        print(f"Connected to MongoDB: {settings.database_name}")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        print("Running without database (in-memory mode)")
        db_instance.connected = False


async def close_mongo_connection():
    """Close MongoDB connection."""
    if db_instance.client:
        db_instance.client.close()
        print("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance for dependency injection."""
    if not db_instance.connected:
        return None
    return db_instance.db


def is_db_connected() -> bool:
    """Check if database is connected."""
    return db_instance.connected
