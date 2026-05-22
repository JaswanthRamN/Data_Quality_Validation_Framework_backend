"""
CRUD operations for User model.
Handles user creation, retrieval, update, and deletion.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.core.security import PasswordManager
from app.utils.logger import logger
from datetime import datetime


def create_user(
    db: Session, 
    username: str, 
    email: str, 
    password: str,
    full_name: str = None,
    is_admin: bool = False
) -> User:
    """
    Create a new user.
    
    Args:
        db: Database session
        username: Username
        email: User email
        password: Plain text password (will be hashed)
        full_name: User's full name (optional)
        is_admin: Whether user is admin (default False)
        
    Returns:
        Created User object
        
    Raises:
        ValueError: If username or email already exists
    """
    try:
        hashed_password = PasswordManager.hash_password(password)
        db_user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            is_admin=is_admin
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User created successfully: {username}")
        return db_user
    except IntegrityError as e:
        db.rollback()
        logger.error(f"User creation failed - duplicate entry: {str(e)}")
        raise ValueError("Username or email already exists")
    except Exception as e:
        db.rollback()
        logger.error(f"User creation error: {str(e)}")
        raise


def get_user_by_username(db: Session, username: str) -> User | None:
    """
    Get user by username.
    
    Args:
        db: Database session
        username: Username to search
        
    Returns:
        User object or None
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Get user by email.
    
    Args:
        db: Database session
        email: Email to search
        
    Returns:
        User object or None
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Get user by ID.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User object or None
    """
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, **kwargs) -> User | None:
    """
    Update user fields.
    
    Args:
        db: Database session
        user_id: User ID
        **kwargs: Fields to update (username, email, full_name, is_active, is_admin)
        
    Returns:
        Updated User object or None
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    allowed_fields = {"full_name", "is_active", "is_admin"}
    for key, value in kwargs.items():
        if key in allowed_fields:
            setattr(db_user, key, value)
    
    try:
        db.commit()
        db.refresh(db_user)
        logger.info(f"User updated: {user_id}")
        return db_user
    except Exception as e:
        db.rollback()
        logger.error(f"User update error: {str(e)}")
        raise


def update_password(db: Session, user_id: int, new_password: str) -> bool:
    """
    Update user password.
    
    Args:
        db: Database session
        user_id: User ID
        new_password: New plain text password
        
    Returns:
        True if successful
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db_user.hashed_password = PasswordManager.hash_password(new_password)
    
    try:
        db.commit()
        logger.info(f"Password updated for user: {user_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Password update error: {str(e)}")
        return False


def update_last_login(db: Session, user_id: int) -> bool:
    """
    Update user's last login timestamp.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        True if successful
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db_user.last_login = datetime.utcnow()
    
    try:
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Last login update error: {str(e)}")
        return False


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        True if successful
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    try:
        db.delete(db_user)
        db.commit()
        logger.info(f"User deleted: {user_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"User deletion error: {str(e)}")
        return False


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list:
    """
    Get all users with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum records to return
        
    Returns:
        List of User objects
    """
    return db.query(User).offset(skip).limit(limit).all()
