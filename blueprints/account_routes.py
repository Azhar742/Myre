# --- Account Routes ---

from flask import Blueprint, request, jsonify

account_bp = Blueprint('account_bp', __name__)


@account_bp.route('/accounts', methods=['POST'])
def create_account_route():
    """Create new customer account"""
    data = request.get_json()
    
    account = create_account_service(data)
    
    return jsonify({'message': 'Account created', 'account_id': account.id}), 201


@account_bp.route('/accounts/<int:account_id>/fields', methods=['GET'])
def get_account_populated_fields_route(account_id):
    """Get all non-null field names for an account (useful for building filters)"""
    fields = get_account_filter_conditions(account_id)
    
    if fields is None:
        return jsonify({'message': 'Account not found'}), 404
    
    return jsonify({
        'account_id': account_id,
        'populated_fields': fields,
        'total_fields': len(fields)
    })


@account_bp.route('/accounts/<int:account_id>', methods=['GET'])
def get_account_route(account_id):
    """Get account details by ID"""
    account = get_account_service(account_id)
    
    if not account:
        return jsonify({'message': 'Account not found'}), 404

    return jsonify(serialize_account(account))


@account_bp.route('/accounts/<int:account_id>', methods=['PUT'])
def update_account_route(account_id):
    """Update account information by ID"""
    data = request.get_json()
    
    account = update_account_service(account_id, data)
    
    if not account:
        return jsonify({'message': 'Account not found'}), 404

    return jsonify({'message': 'Account updated'})


@account_bp.route('/accounts/<int:account_id>', methods=['DELETE'])
def delete_account_route(account_id):
    """Delete account by ID"""
    # Call controller service to handle business logic
    success = delete_account_service(account_id)
    
    if not success:
        return jsonify({'message': 'Account not found'}), 404

    return jsonify({'message': 'Account deleted'})

@account_bp.route('/account/<int:account_id>', methods=['GET'])
def get_account_details(account_id):
    """Get account details by ID"""
    account = Account.query.get(account_id)
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    return jsonify(serialize_account(account)), 200