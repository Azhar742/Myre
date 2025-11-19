
from flask import Blueprint, request, jsonify, session, redirect, url_for
from models.user_model import User
from controllers.user_controller import create_user_service

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user with email and password"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Find user by email
    user = User.query.filter_by(user_email=email).first()
    
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check password (in production, use hashed passwords)
    if user.user_password != password:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Set session - user is now logged in
    session['user_id'] = user.id
    session['user_email'] = user.user_email
    session['user_role'] = user.user_role
    
    # Return user data
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'name': user.user_name,
            'email': user.user_email,
            'role': user.user_role,
            'organization_id': user.organization_id,
            'is_org_admin': user.is_org_admin
        }
    }), 200


@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """Logout user (clear session)"""
    # Clear the session
    session.clear()
    
    if request.method == 'POST':
        response = jsonify({'message': 'Logged out successfully'})
        response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage"'
        return response, 200
    else:
        # Redirect to home page for GET requests
        response = redirect(url_for('home'))
        response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage"'
        return response


@auth_bp.route('/session', methods=['GET'])
def get_session():
    """Get current session info (for testing/debugging)"""
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user_id': session.get('user_id'),
            'user_email': session.get('user_email'),
            'user_role': session.get('user_role')
        }), 200
    else:
        return jsonify({'logged_in': False}), 200


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Create new user account with default CSM role"""
    data = request.get_json()
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    company_name = data.get('company_name')
    company_domain = data.get('company_domain') or email.split('@')[-1] if email else None
    
    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(user_email=email).first()
    if existing_user:
        return jsonify({'error': 'An account with this email already exists'}), 409
    
    # Extract domain from email if not explicitly provided
    email_domain = email.split('@')[-1]
    
    # Check if company/organization already exists by matching domain with organization email
    from models.organization_model import Organization
    org = None
    
    # Try to find organization by domain match
    orgs = Organization.query.filter(
        Organization.deleted_at.is_(None),
        Organization.org_status == 'active'
    ).all()
    
    for organization in orgs:
        org_domain = organization.org_email.split('@')[-1] if organization.org_email else None
        if org_domain and org_domain == email_domain:
            org = organization
            break
    
    if not org:
        # No matching organization found
        return jsonify({
            'error': 'Your organization is not registered. Please use the organization signup flow first.',
            'redirect_to': '/organization/signup'
        }), 403
    
    # Create new user with organization association
    user_data = {
        'user_name': name,
        'user_email': email,
        'user_password': password,  # In production, hash this password
        'user_role': 'csm',  # Default role
        'organization_id': org.id,
        'is_org_admin': False
    }
    
    new_user = create_user_service(user_data)
    
    if not new_user:
        return jsonify({'error': 'Failed to create user account'}), 500
    
    return jsonify({
        'message': 'Account created successfully',
        'user': {
            'id': new_user.id,
            'name': new_user.user_name,
            'email': new_user.user_email,
            'role': new_user.user_role,
            'organization_id': new_user.organization_id
        }
    }), 201
