from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.core.config import settings
from loguru import logger

# MongoDB connection
mongodb_client: Optional[AsyncIOMotorClient] = None
mongodb_database: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongodb():
    """Connect to MongoDB"""
    global mongodb_client, mongodb_database
    
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb_database = mongodb_client[settings.MONGODB_DB_NAME]
        
        # Test connection
        await mongodb_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


async def close_mongodb_connection():
    """Close MongoDB connection"""
    global mongodb_client
    
    if mongodb_client:
        mongodb_client.close()
        logger.info("Closed MongoDB connection")


async def create_indexes():
    """Create database indexes for better performance"""
    if mongodb_database:
        # Users collection indexes
        await mongodb_database.users.create_index("username", unique=True)
        await mongodb_database.users.create_index("email")
        
        # Tasks collection indexes
        await mongodb_database.tasks.create_index("created_by")
        await mongodb_database.tasks.create_index("task_type")
        await mongodb_database.tasks.create_index("enabled")
        
        # Task executions collection indexes
        await mongodb_database.task_executions.create_index("task_id")
        await mongodb_database.task_executions.create_index("status")
        await mongodb_database.task_executions.create_index("created_at")
        
        # Workflows collection indexes
        await mongodb_database.workflows.create_index("created_by")
        
        logger.info("Database indexes created successfully")


def get_database() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance"""
    return mongodb_database
