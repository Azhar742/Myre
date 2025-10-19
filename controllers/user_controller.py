from models.user_model import db, User
from datetime import datetime


def create_user_service(user_data):
    """
    Business logic for creating a new user.
    
    Args:
        user_data: Dictionary containing user information
        
    Returns:
        Created user object
    """
    user = User(
        user_name=user_data['user_name'],
        user_email=user_data['user_email'],
        user_password=user_data['user_password'],  # Hash in production!
        user_role=user_data.get('user_role', 'user'),
        user_status=user_data.get('user_status', 'active'),
        company_name=user_data.get('company_name'),
        company_id=user_data.get('company_id')
    )
    
    db.session.add(user)
    db.session.commit()
    
    return user


def get_user_service(user_id):
    """
    Business logic for retrieving a user by ID.
    
    Args:
        user_id: ID of the user to retrieve
        
    Returns:
        User object if found and not deleted, None otherwise
    """
    user = User.query.get(user_id)
    if not user or user.user_deleted_at:
        return None
    return user


def update_user_service(user_id, user_data):
    """
    Business logic for updating a user.
    
    Args:
        user_id: ID of the user to update
        user_data: Dictionary containing updated user information
        
    Returns:
        Updated user object if found, None otherwise
    """
    user = User.query.get(user_id)
    if not user or user.user_deleted_at:
        return None
    
    user.user_name = user_data.get('user_name', user.user_name)
    user.user_email = user_data.get('user_email', user.user_email)
    if 'user_password' in user_data:
        user.user_password = user_data['user_password']  # Hash in production!
    user.user_role = user_data.get('user_role', user.user_role)
    user.user_status = user_data.get('user_status', user.user_status)
    user.company_name = user_data.get('company_name', user.company_name)
    user.company_id = user_data.get('company_id', user.company_id)
    
    db.session.commit()
    
    return user


def delete_user_service(user_id):
    """
    Business logic for soft deleting a user.
    
    Args:
        user_id: ID of the user to delete
        
    Returns:
        True if user was deleted, False if user not found
    """
    user = User.query.get(user_id)
    if not user or user.user_deleted_at:
        return False
    
    user.user_deleted_at = datetime.utcnow()
    db.session.commit()
    
    return True
