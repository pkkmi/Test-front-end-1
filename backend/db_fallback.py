"""
Enhanced fallback for database operations with MongoDB compatibility
"""

import logging
from datetime import datetime
import os
import uuid
import time
import json
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.warning("Using enhanced in-memory database fallback with MongoDB compatibility")

# Add thread locking for database operations
_db_lock = threading.Lock()

# Simple in-memory storage
_collections = {
    'users': {}
}

# MongoDB result objects
class InsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id
        self.acknowledged = True

class UpdateResult:
    def __init__(self, matched_count, modified_count):
        self.matched_count = matched_count
        self.modified_count = modified_count
        self.acknowledged = True

# Collection class to mimic MongoDB collections
class Collection:
    def __init__(self, name):
        self.name = name
        if name not in _collections:
            _collections[name] = {}
        self.data = _collections[name]
    
    def find_one(self, query):
        """Find a single document matching the query with retry logic"""
        with _db_lock:
            logger.info(f"Find one in {self.name}: {query}")
            
            # Log query details for debugging
            try:
                query_str = json.dumps(query)
                logger.info(f"Query details: {query_str}")
            except:
                pass
            
            # Log all existing keys for debugging
            keys_in_collection = list(self.data.keys())
            logger.info(f"Collection '{self.name}' contains keys: {keys_in_collection}")
            
            # Handle simple id query
            if '_id' in query and query['_id'] in self.data:
                return self.data[query['_id']]
            
            # Handle $or operator
            if '$or' in query:
                for condition in query['$or']:
                    for field, value in condition.items():
                        for doc_id, doc in self.data.items():
                            if field in doc and doc[field] == value:
                                return doc.copy()
                return None
            
            # Handle email query (for auth)
            if 'email' in query:
                email = query['email']
                logger.info(f"Searching for email: {email}")
                for doc_id, doc in self.data.items():
                    doc_email = doc.get('email')
                    if doc_email == email:
                        logger.info(f"Found user by email: {email}")
                        return doc.copy()  # Return a copy to avoid modification issues
            
            # Handle username query
            if 'username' in query:
                username = query['username']
                if username in self.data:
                    logger.info(f"Found user by username: {username}")
                    return self.data[username].copy()  # Return a copy to avoid modification issues
                for doc_id, doc in self.data.items():
                    if doc.get('username') == username:
                        return doc.copy()
            
            logger.info(f"No match found for query: {query}")
            return None
    
    def create_index(self, field_name, unique=False, sparse=False):
        """Create an index (simulated)"""
        logger.info(f"Creating index on {self.name}.{field_name} (unique={unique}, sparse={sparse})")
        return field_name
    
    def insert_one(self, document):
        """Insert a single document with retry logic"""
        with _db_lock:
            logger.info(f"Insert one in {self.name}: {document}")
            
            # Create ID if not provided
            if '_id' not in document:
                document['_id'] = str(uuid.uuid4())
                
            # For user documents, use username as key
            if self.name == 'users' and 'username' in document:
                doc_id = document['username']
            else:
                doc_id = document['_id']
                
            # Store a copy of the document to avoid modification issues
            self.data[doc_id] = document.copy()
            
            # Log success
            logger.info(f"Document inserted with id: {doc_id}")
            return InsertOneResult(document['_id'])
    
    def update_one(self, filter_query, update_query):
        """Update a single document with retry logic"""
        with _db_lock:
            logger.info(f"Update one in {self.name}: {filter_query} -> {update_query}")
            
            # Find the document to update
            doc_to_update = self.find_one(filter_query)
            if not doc_to_update:
                logger.info(f"No document found to update for query: {filter_query}")
                return UpdateResult(0, 0)
                
            # Get the document ID
            if self.name == 'users' and 'username' in doc_to_update:
                doc_id = doc_to_update['username']
            else:
                doc_id = doc_to_update['_id']
                
            # Handle $set operation
            if '$set' in update_query:
                for key, value in update_query['$set'].items():
                    doc_to_update[key] = value
                    
            # Handle $inc operation
            if '$inc' in update_query:
                for key, value in update_query['$inc'].items():
                    # Handle nested paths like 'usage.requests'
                    if '.' in key:
                        parts = key.split('.')
                        target = doc_to_update
                        for part in parts[:-1]:
                            if part not in target:
                                target[part] = {}
                            target = target[part]
                        target[parts[-1]] = target.get(parts[-1], 0) + value
                    else:
                        doc_to_update[key] = doc_to_update.get(key, 0) + value
            
            # Replace the document in storage
            self.data[doc_id] = doc_to_update
            logger.info(f"Document updated: {doc_id}")
            return UpdateResult(1, 1)
            
    def find(self, query=None, projection=None):
        """Find all documents matching the query"""
        with _db_lock:
            logger.info(f"Find in {self.name}: {query}")
            results = []
            
            # Return all documents if no query
            if not query:
                return list(self.data.values())
                
            # Filter documents based on query
            for doc in self.data.values():
                match = True
                for key, value in query.items():
                    if key not in doc or doc[key] != value:
                        match = False
                        break
                if match:
                    results.append(doc.copy())  # Return copies to avoid modification issues
                    
            return results

# Mock client and db for compatibility
class MockClient:
    def __init__(self):
        self.connected = True
    
    def close(self):
        self.connected = False

client = MockClient()

# Mock DB to mimic MongoDB db access
class MockDB:
    def __init__(self):
        self.collections = {}
    
    def __getitem__(self, name):
        """Allow dict-like access to collections"""
        return Collection(name)
        
    def command(self, cmd):
        """Mock MongoDB commands"""
        if cmd == 'ping':
            return {'ok': 1.0}
        return {'ok': 0.0}

db = MockDB()

# Database operation functions with retry logic
def init_db():
    """Initialize the in-memory database."""
    logger.info("Initializing fallback database")
    # Create test user
    users = Collection('users')
    if not users.find_one({"username": "demo"}):
        users.insert_one({
            "_id": "demo-id",
            "username": "demo",
            "email": "demo@example.com",
            "password_hash": "5f4dcc3b5aa765d61d8327deb882cf99",  # "password"
            "password_salt": "demo-salt",
            "created_at": datetime.now(),
            "usage": {
                "requests": 0,
                "total_words": 0,
                "monthly_words": 0,
                "last_request": None
            }
        })
    return True

def add_user(username, email, password_hash):
    """Add a new user with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            collection = Collection('users')
            
            # Check if user exists
            if collection.find_one({'username': username}):
                logger.info(f"User already exists: {username}")
                return False
            
            # Insert new user
            logger.info(f"Creating new user: {username}, {email}")
            collection.insert_one({
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'created_at': datetime.now(),
                'usage': {
                    'requests': 0,
                    'total_words': 0,
                    'monthly_words': 0,
                    'last_request': None
                }
            })
            
            logger.info(f"User created successfully: {username}")
            return True
        except Exception as e:
            logger.error(f"Error creating user (attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(0.5)  # Short delay before retry
            else:
                raise
    
    return False

def verify_user(username, password_hash):
    """Verify user credentials with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            collection = Collection('users')
            user = collection.find_one({'username': username})
            
            if not user:
                logger.info(f"User not found for verification: {username}")
                return False
            
            return user.get('password_hash') == password_hash
        except Exception as e:
            logger.error(f"Error verifying user (attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(0.5)  # Short delay before retry
            else:
                raise
    
    return False

def get_user(username):
    """Get user information with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            collection = Collection('users')
            logger.info(f"Getting user: {username}")
            user = collection.find_one({'username': username})
            if user:
                logger.info(f"User found: {username}")
            else:
                logger.info(f"User not found: {username}")
            return user
        except Exception as e:
            logger.error(f"Error getting user (attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(0.5)  # Short delay before retry
            else:
                raise
    
    return None

def update_user_usage(username, word_count):
    """Update user usage statistics with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            collection = Collection('users')
            result = collection.update_one(
                {'username': username},
                {
                    '$inc': {
                        'usage.requests': 1,
                        'usage.total_words': word_count,
                        'usage.monthly_words': word_count
                    },
                    '$set': {
                        'usage.last_request': datetime.now()
                    }
                }
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user usage (attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(0.5)  # Short delay before retry
            else:
                raise
    
    return False

# For debug purposes, print loaded status
logger.warning("Enhanced db_fallback.py loaded successfully with MongoDB compatibility and retry logic!")
