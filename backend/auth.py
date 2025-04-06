"""
Manual Authentication Module

Provides user registration, login, and authentication functionality
without relying on Google OAuth.
"""

import os
import logging
import time
from datetime import datetime
import re
import hashlib
import secrets
import traceback
from flask import url_for, session, redirect, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_auth(app, db):
    """Initialize authentication module"""
    logger.info("Initializing auth module")
    # Create collections and indexes if needed
    try:
        # Ensure user collection has required indexes
        db['users'].create_index("email", unique=True)
        db['users'].create_index("username", unique=True)
        db['users'].create_index("phone", sparse=True)
        logger.info("Auth module initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing auth module: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def hash_password(password, salt=None):
    """Hash password with salt using SHA-256"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Combine password and salt, then hash
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    # Return hash and salt
    return password_hash, salt

def validate_password(password, correct_hash, salt):
    """Validate a password against a stored hash"""
    password_hash, _ = hash_password(password, salt)
    return password_hash == correct_hash

def validate_email(email):
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def validate_phone(phone):
    """Validate phone number format"""
    # Allow common phone formats with optional country codes
    phone_pattern = r'^\+?[0-9]{7,15}$'
    return bool(re.match(phone_pattern, phone))

def register_user(db, username, email, password, phone=None):
    """Register a new user with username, email, and password"""
    # Validate inputs
    if not username or not email or not password:
        logger.warning("Registration failed: Missing required fields")
        return False, "All fields are required"
    
    if not validate_email(email):
        logger.warning(f"Registration failed: Invalid email format - {email}")
        return False, "Invalid email format"
    
    if phone and not validate_phone(phone):
        logger.warning(f"Registration failed: Invalid phone format - {phone}")
        return False, "Invalid phone number format"
    
    if len(password) < 8:
        logger.warning("Registration failed: Password too short")
        return False, "Password must be at least 8 characters"
    
    # Check if username or email already exists
    try:
        users_collection = db['users']
        existing_user = users_collection.find_one({"$or": [
            {"username": username},
            {"email": email}
        ]})
        
        if existing_user:
            if existing_user.get('email') == email:
                logger.warning(f"Registration failed: Email already exists - {email}")
                return False, "Email already registered"
            else:
                logger.warning(f"Registration failed: Username already exists - {username}")
                return False, "Username already taken"
        
        # Hash password
        password_hash, salt = hash_password(password)
        
        # Create new user
        new_user = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "password_salt": salt,
            "phone": phone,
            "created_at": datetime.now(),
            "last_login": None,
            "profile_picture": "",  # No picture for manual registration
            "usage": {
                "requests": 0,
                "total_words": 0,
                "monthly_words": 0,
                "last_request": None
            }
        }
        
        # Insert user into database
        result = users_collection.insert_one(new_user)
        
        if result.inserted_id:
            logger.info(f"User registered successfully: {username}")
            return True, "Registration successful"
        else:
            logger.error(f"Failed to insert new user: {username}")
            return False, "Registration failed due to database error"
            
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        logger.error(traceback.format_exc())
        return False, "Registration failed: Internal error"

def login_user(db, email_or_username, password):
    """Login a user with email/username and password"""
    try:
        users_collection = db['users']
        
        # Find user by email or username
        user = users_collection.find_one({
            "$or": [
                {"email": email_or_username},
                {"username": email_or_username}
            ]
        })
        
        if not user:
            logger.warning(f"Login failed: User not found - {email_or_username}")
            return None, "Invalid email/username or password"
        
        # Validate password
        if not validate_password(password, user['password_hash'], user['password_salt']):
            logger.warning(f"Login failed: Invalid password for user - {email_or_username}")
            return None, "Invalid email/username or password"
        
        # Update last login time
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.now()}}
        )
        
        # Return user info
        logger.info(f"User logged in successfully: {user['username']}")
        return user, "Login successful"
        
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        logger.error(traceback.format_exc())
        return None, "Login failed: Internal error"

def get_user_by_id(db, user_id):
    """Get user information by user ID"""
    try:
        users_collection = db['users']
        user = users_collection.find_one({"username": user_id})
        return user
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return None

def update_user_password(db, user_id, current_password, new_password):
    """Update user password"""
    try:
        users_collection = db['users']
        user = users_collection.find_one({"username": user_id})
        
        if not user:
            return False, "User not found"
        
        # Validate current password
        if not validate_password(current_password, user['password_hash'], user['password_salt']):
            return False, "Current password is incorrect"
        
        # Validate new password
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters"
        
        # Hash new password
        new_hash, new_salt = hash_password(new_password)
        
        # Update password
        result = users_collection.update_one(
            {"username": user_id},
            {"$set": {
                "password_hash": new_hash,
                "password_salt": new_salt
            }}
        )
        
        if result.modified_count > 0:
            return True, "Password updated successfully"
        else:
            return False, "Failed to update password"
            
    except Exception as e:
        logger.error(f"Error updating password: {str(e)}")
        return False, "Failed to update password: Internal error"

def update_user_profile(db, user_id, email=None, phone=None):
    """Update user profile information"""
    try:
        users_collection = db['users']
        
        # Build update document
        update_doc = {}
        
        if email:
            if not validate_email(email):
                return False, "Invalid email format"
                
            # Check if email is already taken by another user
            existing = users_collection.find_one({"email": email, "username": {"$ne": user_id}})
            if existing:
                return False, "Email is already registered to another account"
                
            update_doc["email"] = email
            
        if phone:
            if not validate_phone(phone):
                return False, "Invalid phone number format"
            update_doc["phone"] = phone
            
        if not update_doc:
            return False, "No changes provided"
            
        # Update user
        result = users_collection.update_one(
            {"username": user_id},
            {"$set": update_doc}
        )
        
        if result.modified_count > 0:
            return True, "Profile updated successfully"
        else:
            return False, "No changes made"
            
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return False, "Failed to update profile: Internal error"
