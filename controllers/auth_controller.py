from flask import Blueprint, request, jsonify
from extensions import get_supabase_client
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register new user with Supabase"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        client = get_supabase_client()
        
        # Sign up user
        response = client.auth.sign_up({
            'email': email,
            'password': password
        })
        
        logger.info(f'User signed up successfully', extra={
            'extra_data': {
                'email': email,
                'user_id': response.user.id if response.user else None
            }
        })
        
        return jsonify({
            'message': 'User created successfully',
            'user': response.user.model_dump() if response.user else {},
            'session': response.session.model_dump() if response.session else {}
        }), 201
        
    except Exception as e:
        logger.error(f'Signup error: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with Supabase"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        client = get_supabase_client()
        
        # Sign in user
        response = client.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        
        logger.info(f'User logged in successfully', extra={
            'extra_data': {
                'email': email,
                'user_id': response.user.id if response.user else None
            }
        })
        
        return jsonify({
            'message': 'Login successful',
            'user': response.user.model_dump() if response.user else {},
            'session': response.session.model_dump() if response.session else {},
            'access_token': response.session.access_token if response.session else None
        }), 200
        
    except Exception as e:
        logger.error(f'Login error: {str(e)}', exc_info=True)
        return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        client = get_supabase_client()
        client.auth.sign_out()
        
        logger.info('User logged out successfully')
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        logger.error(f'Logout error: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 400