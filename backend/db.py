"""
MongoDB database module for Andikar AI application.
"""

import os
import logging
from datetime import datetime
from pymongo import MongoClient
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGODB_URI = os.environ.get("MONGODB_URI")

if not MONGODB_URI:
    logger.warning("MONGODB_URI environment variable not set. Database operations will fail.")

try:
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    db = client.get_database('andikar')  # Use andikar database
    
    # Test connection
    db.command('ping')
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    logger.error(traceback.format_exc())
    raise

def init_db():
    """Initialize database - create collections and indexes if needed."""
    try:
        # Create collections if they don't exist
        if 'users' not in db.list_collection_names():
            db.create_collection('users')
            logger.info("Created users collection")
        
        # Create indexes
        db.users.create_index("username", unique=True)
        db.users.create_index("email", unique=True)
        db.users.create_index("phone", sparse=True)
        
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def add_user(username, email, password_hash):
    """Add a new user to the database."""
    try:
        # Check if user already exists
        existing_user = db.users.find_one({
            "$or": [
                {"username": username},
                {"email": email}
            ]
        })
        
        if existing_user:
            logger.warning(f"User already exists: {username}")
            return False
        
        # Create new user document
        user = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.now(),
            "usage": {
                "requests": 0,
                "total_words": 0,
                "monthly_words": 0,
                "last_request": None
            }
        }
        
        # Insert user into database
        result = db.users.insert_one(user)
        
        logger.info(f"User created successfully: {username}")
        return bool(result.inserted_id)
    except Exception as e:
        logger.error(f"Error adding user: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def verify_user(username, password_hash):
    """Verify user credentials."""
    try:
        # Find user by username
        user = db.users.find_one({"username": username})
        
        if not user:
            logger.warning(f"User not found: {username}")
            return False
        
        # Verify password
        return user.get('password_hash') == password_hash
    except Exception as e:
        logger.error(f"Error verifying user: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def get_user(username):
    """Get user information by username."""
    try:
        # Find user by username
        user = db.users.find_one({"username": username})
        
        if not user:
            logger.warning(f"User not found: {username}")
            return None
        
        return user
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def update_user_usage(username, word_count):
    """Update user usage statistics."""
    try:
        # Update usage statistics
        result = db.users.update_one(
            {"username": username},
            {
                "$inc": {
                    "usage.requests": 1,
                    "usage.total_words": word_count,
                    "usage.monthly_words": word_count
                },
                "$set": {
                    "usage.last_request": datetime.now()
                }
            }
        )
        
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating user usage: {str(e)}")
        logger.error(traceback.format_exc())
        return False
