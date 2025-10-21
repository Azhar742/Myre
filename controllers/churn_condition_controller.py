from models.churn_condition_model import ChurnCondition
from models.account_model import Account
from models.user_model import db

def create_churn_condition_service(data):
    """
    Create a new churn condition (same interface as priority conditions)
    
    Args:
        data: Dictionary containing:
            - condition_name: Name of the condition
            - description: Optional description
            - filter_conditions: Dictionary of filter rules
            - created_by: User ID who created this condition
    
    Returns:
        Created ChurnCondition object
    """
    if 'filter_conditions' not in data:
        return None
    
    condition = ChurnCondition(
        condition_name=data['condition_name'],
        description=data.get('description', ''),
        user_id=data['created_by'],  # For backward compatibility
        created_by=data['created_by'],
        is_active=True
    )
    
    # Set filter conditions from dictionary
    condition.set_filter_conditions(data['filter_conditions'])
    
    db.session.add(condition)
    db.session.commit()
    
    return condition


def get_churn_conditions_by_user_service(user_id):
    """Get all active churn conditions created by a specific user"""
    return ChurnCondition.query.filter_by(created_by=user_id, is_active=True).all()


def get_churn_accounts_service(condition_id, user_id=None):
    """
    Get all accounts matching a specific churn condition (using SQLAlchemy queries)
    
    Args:
        condition_id: ID of the churn condition
        user_id: Optional - filter accounts by CSM user ID
        
    Returns:
        List of Account objects matching all conditions, or None if condition not found
    """
    condition = ChurnCondition.query.get(condition_id)
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
            # For string columns, use case-insensitive comparison
            if isinstance(value, str):
                query = query.filter(db.func.lower(column) == value.lower())
            else:
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


def get_accounts_by_user_churn_conditions_service(user_id):
    """
    Get all accounts that match ANY churn condition created by a specific user.
    Only returns accounts assigned to this CSM user.
    
    Args:
        user_id: ID of the CSM user who created the conditions
        
    Returns:
        Dictionary with conditions and their matching accounts
    """
    # Get all churn conditions created by this user
    conditions = get_churn_conditions_by_user_service(user_id)
    
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
        accounts = get_churn_accounts_service(condition.id, user_id)
        
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


def delete_churn_condition_service(condition_id):
    """Delete a churn condition"""
    condition = ChurnCondition.query.get(condition_id)
    if not condition:
        return False
    
    db.session.delete(condition)
    db.session.commit()
    return True
