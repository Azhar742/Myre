# --- Priority Condition Routes ---

from flask import Blueprint, request, jsonify
from models.priority_condition_model import PriorityCondition
from controllers.priority_condition_controller import (
    get_priority_conditions_by_user_service,
    create_priority_condition_service,
    get_priority_accounts_service,
    delete_priority_condition_service
)
from utils.utils import serialize_account
from decorators import login_required

priority_account_bp = Blueprint('priority_account_bp', __name__)

@priority_account_bp.route('/priority_conditions/<int:user_id>', methods=['GET'])
def get_priority_condition_accounts_by_user_route(user_id):
    """Get all priority rules created by a specific user"""
    
    conditions = get_priority_conditions_by_user_service(user_id)
    
    if not conditions:
        return jsonify({
            'user_id': user_id,
            'total_conditions': 0,
            'conditions': []
        }), 200
    
    # Serialize conditions
    result = {
        'user_id': user_id,
        'total_conditions': len(conditions),
        'conditions': [condition.to_dict() for condition in conditions]
    }
    
    return jsonify(result)

@priority_account_bp.route('/priority_conditions_all', methods=['GET'])
def get_all_priority_conditions_route():
    """Get all priority rules across all users"""
    conditions = PriorityCondition.query.all()
    
    result = [condition.to_dict() for condition in conditions]
    
    return jsonify({
        'total_conditions': len(result),
        'conditions': result
    })


@priority_account_bp.route('/priority_condition/<int:account_id>', methods=['GET'])
def get_priority_condition_fields_route(account_id):
    """Get available filter fields for an account (same as /accounts/<id>/fields)"""
    fields = get_account_filter_conditions(account_id)
    
    if fields is None:
        return jsonify({'message': 'Account not found'}), 404
    
    return jsonify({
        'account_id': account_id,
        'available_filter_fields': fields,
    })
    
@priority_account_bp.route('/priority_conditions', methods=['POST'])
@login_required
def create_priority_condition_route():
    """Create a new priority condition with the filter conditions (requires: condition_name, filter_conditions, created_by)"""
    data = request.get_json()
    
    if not data.get('filter_conditions'):
        return jsonify({'error': 'filter_conditions is required'}), 400
    
    # Use account_id=0 as placeholder since this endpoint doesn't require it
    priority_condition = create_priority_condition_service(0, data)
    
    if priority_condition is None:
        return jsonify({'error': 'Failed to create priority condition'}), 400
    
    return jsonify({
        'message': 'Priority condition created successfully',
        'priority_condition': priority_condition.to_dict()
    }), 201


@priority_account_bp.route('/priority_conditions/<int:condition_id>', methods=['DELETE'])
@login_required
def delete_priority_condition_route(condition_id):
    """Delete a priority condition"""
    condition = PriorityCondition.query.get(condition_id)
    if not condition:
        return jsonify({'error': 'Priority condition not found'}), 404
    
    db.session.delete(condition)
    db.session.commit()
    
    return jsonify({'message': 'Priority condition deleted successfully'}), 200


@priority_account_bp.route('/priority_condition/<int:account_id>', methods=['POST'])
@login_required
def create_priority_condition_legacy_route(account_id):
    """Create priority rule using account_id as reference (legacy endpoint)"""
    data = request.get_json()
    
    priority_condition = create_priority_condition_service(account_id, data)
    
    if priority_condition is None:
        return jsonify({'message': 'filter_conditions is required'}), 400
    
    return jsonify({
        'message': 'Priority condition created',
        'priority_condition_id': priority_condition.id,
        'condition_name': priority_condition.condition_name,
        'filter_conditions': priority_condition.get_filter_conditions()
    }), 201


@priority_account_bp.route('/priority_accounts/<int:condition_id>', methods=['GET'])
def get_priority_accounts_route(condition_id):
    """Get all accounts matching a priority rule's filter conditions"""
    accounts = get_priority_accounts_service(condition_id)
    
    if accounts is None:
        return jsonify({'message': 'Priority condition not found'}), 404
    
    return jsonify({
        'condition_id': condition_id,
        'total_accounts': len(accounts),
        'accounts': [serialize_account(account) for account in accounts]
    })

