import logging
from functools import wraps
from flask import request, jsonify, g
from extensions import get_supabase_client
from supabase import Client

logger = logging.getLogger(__name__)

def verify_supabase_token(token: str) -> dict:
    """
    Verify Supabase JWT token
    
    Args:
        token: JWT token from Authorization header
    
    Returns:
        User data if valid
    
    Raises:
        ValueError if token is invalid
    """
    try:
        client: Client = get_supabase_client()
        
        # Get user from token
        user = client.auth.get_user(token)
        
        if not user:
            raise ValueError('Invalid token')
        
        logger.info(f'Token verified successfully', extra={
            'extra_data': {
                'user_id': user.user.id if user.user else None
            }
        })
        
        return user.user.model_dump() if user.user else {}
        
    except Exception as e:
        logger.error(f'Token verification failed: {str(e)}')
        raise ValueError('Invalid or expired token')

def require_supabase_auth(f):
    """Decorator to require Supabase authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning('Missing or invalid Authorization header')
            return jsonify({'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            user_data = verify_supabase_token(token)
            g.user = user_data
            g.user_id = user_data.get('id')
            
            return f(*args, **kwargs)
            
        except ValueError as e:
            logger.warning(f'Authentication failed: {str(e)}')
            return jsonify({'error': 'Invalid or expired token'}), 401
    
    return decorated_function