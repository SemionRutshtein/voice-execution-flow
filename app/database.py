import logging
from typing import Optional, List
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId
from datetime import datetime

from .config import settings
from .models import VoiceActionInDB, VoiceActionCreate

logger = logging.getLogger(__name__)


class MongoDB:
    client: Optional[MongoClient] = None
    database: Optional[Database] = None


db = MongoDB()


async def connect_to_mongo():
    """Create database connection"""
    try:
        db.client = MongoClient(settings.MONGODB_URL)
        db.database = db.client[settings.DATABASE_NAME]
        
        # Create indexes for better performance
        collection = db.database[settings.COLLECTION_NAME]
        collection.create_index([("userId", ASCENDING)])
        collection.create_index([("timestamp", ASCENDING)])
        
        # Test the connection
        db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")


def get_collection() -> Collection:
    """Get the voice actions collection"""
    if db.database is None:
        raise Exception("Database not initialized")
    return db.database[settings.COLLECTION_NAME]


async def create_voice_action(voice_action: VoiceActionCreate) -> VoiceActionInDB:
    """Create a new voice action record"""
    collection = get_collection()
    
    voice_action_dict = voice_action.model_dump()
    voice_action_dict["timestamp"] = datetime.utcnow()
    
    result = collection.insert_one(voice_action_dict)
    
    created_record = collection.find_one({"_id": result.inserted_id})
    return VoiceActionInDB(**created_record)


async def get_voice_action_by_id(action_id: str) -> Optional[VoiceActionInDB]:
    """Get a voice action by ID"""
    collection = get_collection()
    
    try:
        record = collection.find_one({"_id": ObjectId(action_id)})
        if record:
            return VoiceActionInDB(**record)
    except Exception as e:
        logger.error(f"Error fetching voice action: {e}")
    
    return None


async def get_voice_actions_by_user(user_id: str, limit: int = 100) -> List[VoiceActionInDB]:
    """Get all voice actions for a specific user"""
    collection = get_collection()
    
    cursor = collection.find({"userId": user_id}).sort("timestamp", -1).limit(limit)
    
    return [VoiceActionInDB(**record) for record in cursor]


async def update_voice_action_processed(action_id: str, processed: bool = True) -> bool:
    """Mark a voice action as processed"""
    collection = get_collection()
    
    try:
        result = collection.update_one(
            {"_id": ObjectId(action_id)},
            {"$set": {"processed": processed}}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating voice action: {e}")
        return False