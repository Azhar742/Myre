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
        is_active=data.get('is_active', True),
        created_by=data.get('created_by')
    )
    
    # Set filter conditions from dictionary
    condition.set_filter_conditions(data['filter_conditions'])
    
    db.session.add(condition)
    db.session.commit()
    
    return condition


def delete_priority_condition_service(condition_id):
    """Delete a priority condition"""
    condition = PriorityCondition.query.get(condition_id)
    if not condition:
        return False
    
    db.session.delete(condition)
    db.session.commit()
    return True


def get_priority_accounts_service(condition_id):
    """
    Get all accounts that match the filter conditions of a priority condition.
    
    Args:
        condition_id: ID of the priority condition
        
    Returns:
        List of Account objects matching all conditions, or None if condition not found
    """
    condition = PriorityCondition.query.get(condition_id)
    if not condition:
        return None
    
    # Get the filter conditions
    filter_conditions = condition.get_filter_conditions()
    
    # Start with all accounts
    query = Account.query
    
    # Apply each filter condition
    for field_name, condition_rule in filter_conditions.items():
        if not hasattr(Account, field_name):
            continue
        
        column = getattr(Account, field_name)
        operator = condition_rule.get('operator', '==')
        value = condition_rule.get('value')
        
        # Apply the operator
        if operator == '==':
            query = query.filter(column == value)
        elif operator == '!=':
            query = query.filter(column != value)
        elif operator == '>':
            query = query.filter(column > value)
        elif operator == '>=':
            query = query.filter(column >= value)
        elif operator == '<':
            query = query.filter(column < value)
        elif operator == '<=':
            query = query.filter(column <= value)
        elif operator == 'like':
            query = query.filter(column.like(f"%{value}%"))
        elif operator == 'in':
            query = query.filter(column.in_(value))
        elif operator == 'not_in':
            query = query.filter(~column.in_(value))
    
    return query.all()
