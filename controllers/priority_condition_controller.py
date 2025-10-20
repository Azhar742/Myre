from models.user_model import db
from models.priority_condition_model import PriorityCondition
from models.account_model import Account
from datetime import datetime


def get_account_filter_conditions(account_id):
    """
    Get all column names that have non-null values for a specific account.
    
    Args:
        account_id: ID of the account to check
        
    Returns:
        List of column names that have values, or None if account not found
    """
    account = Account.query.get(account_id)
    
    if not account:
        return None
    
    # Get all column names from the Account model
    columns = Account.__table__.columns.keys()
    
    # Build list of columns with non-null values
    populated_fields = []
    
    for column_name in columns:
        value = getattr(account, column_name, None)
        
        # Include the field if it has a value (not None and not empty string)
        if value is not None and value != '':
            populated_fields.append(column_name)
    
    return populated_fields


def create_priority_condition_service(account_id, data):
    """
    Create a priority condition with filter rules.
    
    Args:
        account_id: Reference account ID (optional, for context)
        data: Dictionary containing:
            - condition_name: Name of the condition
            - description: Optional description
            - filter_conditions: Dictionary of filter rules
              Example: {
                "account_status": {"operator": "==", "value": "active"},
                "last_paid_bill_amount": {"operator": ">", "value": 100}
              }
            - created_by: User ID who created this
    
    Returns:
        Created PriorityCondition object
    """
    if 'filter_conditions' not in data:
        return None
    
    condition = PriorityCondition(
        condition_name=data['condition_name'],
        description=data.get('description'),
        reference_account_id=account_id,
        client_account_id=data.get('client_account_id', account_id),
        is_active=data.get('is_active', True),
        created_by=data.get('created_by')
    )
    
    # Set filter conditions from dictionary
    condition.set_filter_conditions(data['filter_conditions'])
    
    db.session.add(condition)
    db.session.commit()
    
    return condition


def get_all_priority_conditions_service():
    """
    Get all priority conditions.
    
    Returns:
        List of all PriorityCondition objects
    """
    return PriorityCondition.query.all()


def get_priority_conditions_by_user_service(user_id):
    """
    Get all priority conditions created by a specific user.
    
    Args:
        user_id: ID of the user who created the conditions
        
    Returns:
        List of PriorityCondition objects created by the user
    """
    return PriorityCondition.query.filter_by(created_by=user_id, is_active=True).all()


def get_accounts_by_user_priority_conditions_service(user_id):
    """
    Get all accounts that match ANY priority condition created by a specific user.
    Only returns accounts assigned to this CSM user.
    
    Args:
        user_id: ID of the CSM user who created the conditions
        
    Returns:
        Dictionary with conditions and their matching accounts
    """
    # Get all priority conditions created by this user
    conditions = get_priority_conditions_by_user_service(user_id)
    
    if not conditions:
        return None
    
    # Collect all matching accounts for each condition
    result = {
        'user_id': user_id,
        'total_conditions': len(conditions),
        'conditions': []
    }
    
    all_account_ids = set()
    
    for condition in conditions:
        # Get accounts matching this condition AND assigned to this user
        accounts = get_priority_accounts_service(condition.id, user_id)
        
        if accounts:
            account_ids = [acc.id for acc in accounts]
            all_account_ids.update(account_ids)
            
            result['conditions'].append({
                'condition_id': condition.id,
                'condition_name': condition.condition_name,
                'description': condition.description,
                'filter_conditions': condition.get_filter_conditions(),
                'matching_accounts_count': len(accounts),
                'matching_account_ids': account_ids
            })
    
    # Get unique accounts assigned to this user
    unique_accounts = Account.query.filter(
        Account.id.in_(all_account_ids),
        Account.csm_user_id == user_id
    ).all() if all_account_ids else []
    
    result['total_unique_accounts'] = len(unique_accounts)
    result['accounts'] = unique_accounts
    
    return result


def delete_priority_condition_service(condition_id):
    """Delete a priority condition"""
    condition = PriorityCondition.query.get(condition_id)
    if not condition:
        return False
    
    db.session.delete(condition)
    db.session.commit()
    return True


def get_priority_accounts_service(condition_id, user_id=None):
    """
    Get all accounts that match the filter conditions of a priority condition.
    
    Args:
        condition_id: ID of the priority condition
        user_id: Optional - filter accounts by CSM user ID
        
    Returns:
        List of Account objects matching all conditions, or None if condition not found
    """
    condition = PriorityCondition.query.get(condition_id)
    if not condition:
        return None
    
    # Get the filter conditions
    filter_conditions = condition.get_filter_conditions()
    
    # Start with all accounts, optionally filtered by user
    query = Account.query
    if user_id is not None:
        query = query.filter(Account.csm_user_id == user_id)
    
    # Apply each filter condition
    for field_name, condition_rule in filter_conditions.items():
        if not hasattr(Account, field_name):
            continue
        
        column = getattr(Account, field_name)
        operator = condition_rule.get('operator', '==')
        value = condition_rule.get('value')
        
        # Convert value to appropriate type if needed
        if value is not None:
            try:
                # Try to convert to float for numeric comparisons
                if operator in ['>', '>=', '<', '<=']:
                    value = float(value)
            except (ValueError, TypeError):
                pass
        
        # Apply the operator with null handling
        if operator == '==':
            query = query.filter(column == value)
        elif operator == '!=':
            query = query.filter(column != value)
        elif operator == '>':
            query = query.filter(column != None).filter(column > value)
        elif operator == '>=':
            query = query.filter(column != None).filter(column >= value)
        elif operator == '<':
            query = query.filter(column != None).filter(column < value)
        elif operator == '<=':
            query = query.filter(column != None).filter(column <= value)
        elif operator == 'like':
            query = query.filter(column != None).filter(column.like(f"%{value}%"))
        elif operator == 'in':
            query = query.filter(column.in_(value))
        elif operator == 'not_in':
            query = query.filter(~column.in_(value))
    
    return query.all()
