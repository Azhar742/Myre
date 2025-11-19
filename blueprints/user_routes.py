from flask import Blueprint, request, jsonify
from controllers.user_controller import create_user_service, get_user_service, update_user_service, delete_user_service

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/users', methods=['POST'])
def create_user():
    """Create new user via API"""
    data = request.get_json()
    
    # Call controller service to handle business logic
    user = create_user_service(data)
    
    return jsonify({'message': 'User created', 'user_id': user.id}), 201


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details by ID"""
    # Call controller service to handle business logic
    user = get_user_service(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'user_name': user.user_name,
        'user_email': user.user_email,
        'user_role': user.user_role,
        'user_status': user.user_status,
        'company_id': user.company_id
    })


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user information by ID"""
    data = request.get_json()
    
    # Call controller service to handle business logic
    user = update_user_service(user_id, data)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({'message': 'User updated'})


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Soft delete user by ID"""
    # Call controller service to handle business logic
    success = delete_user_service(user_id)
    
    if not success:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({'message': 'User deleted (soft delete)'})

