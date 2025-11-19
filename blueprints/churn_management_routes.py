# --- Churn Management Routes ---

from flask import Blueprint, request, jsonify
from models.churn_condition_model import ChurnCondition
from controllers.churn_condition_controller import (
    get_churn_conditions_by_user_service,
    create_churn_condition_service,
    delete_churn_condition_service
)
from utils.utils import serialize_account
from decorators import login_required, validate_user_access

churn_management_bp = Blueprint('churn_management_bp', __name__)

@churn_management_bp.route('/churn_management/<int:user_id>', methods=['GET'])
@validate_user_access
def churn_management_dashboard(user_id):
    """Render churn management dashboard for user"""
    result = get_accounts_by_user_churn_conditions_service(user_id)
    
    if result is None:
        result = {
            'user_id': user_id,
            'total_conditions': 0,
            'conditions': [],
            'total_unique_accounts': 0,
            'accounts': []
        }
    
    accounts = [serialize_account(account) for account in result.get('accounts', [])]
    
    return render_template('html/churn_management.html',
                         user_id=user_id,
                         accounts=accounts,
                         conditions=result.get('conditions', []),
                         total_conditions=result.get('total_conditions', 0),
                         total_accounts=result.get('total_unique_accounts', 0),
                         active_section='churn')

@churn_management_bp.route('/churn_conditions/<int:user_id>', methods=['GET'])
def get_churn_conditions_by_user_route(user_id):
    """Get all churn rules created by a specific user"""
    conditions = get_churn_conditions_by_user_service(user_id)
    
    # Convert to dict format for JSON response
    return jsonify([c.to_dict() for c in conditions]), 200

@churn_management_bp.route('/churn_conditions', methods=['POST'])
@login_required
def create_churn_condition_route():
    """Create a new churn condition"""
    data = request.json
    
    # Convert old format to new unified format
    if 'field_name' in data and 'operator' in data and 'field_value' in data:
        # Old format - convert to new format
        unified_data = {
            'condition_name': data.get('condition_name'),
            'description': data.get('condition_description', ''),
            'filter_conditions': {
                data['field_name']: {
                    'operator': data['operator'],
                    'value': data['field_value']
                }
            },
            'created_by': data.get('user_id')
        }
    else:
        # Already in new format
        unified_data = data
    
    condition = create_churn_condition_service(unified_data)
    
    if condition is None:
        return jsonify({'error': 'Failed to create churn condition', 'success': False}), 400
    
    return jsonify({
        'success': True,
        'message': 'Churn condition created successfully',
        'condition': condition.to_dict()
    }), 201

@churn_management_bp.route('/churn_conditions/<int:condition_id>', methods=['DELETE'])
@login_required
def delete_churn_condition_route(condition_id):
    """Delete a churn condition"""
    success = delete_churn_condition_service(condition_id)
    
    if success:
        return jsonify({'message': 'Churn condition deleted successfully'}), 200
    else:
        return jsonify({'error': 'Churn condition not found'}), 404

