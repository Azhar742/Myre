from datetime import datetime, timedelta
from models.account_rule_model import AccountRule
from models.account_model import Account
from models.user_model import db


def create_rule(data):
    """
    Create a new account rule (any type: priority, churn, upsell, custom)
    
    Args:
        data: Dictionary containing:
            - rule_name: Name of the rule
            - description: Optional description
            - rule_type: Type of rule ('priority', 'churn', 'upsell', 'custom')
            - filter_conditions: Dictionary of filter rules
            - created_by: User ID who created this rule
            - dashboard_config: Optional dashboard configuration
            - is_shared: Optional, share with organization
            - priority_order: Optional, for sorting
    
    Returns:
        Created AccountRule object
    """
    if 'filter_conditions' not in data or 'rule_type' not in data:
        return None
    
    rule = AccountRule(
        rule_name=data['rule_name'],
        description=data.get('description', ''),
        rule_type=data['rule_type'],
        created_by=data['created_by'],
        organization_id=data.get('organization_id'),
        is_shared=data.get('is_shared', False),
        priority_order=data.get('priority_order', 0),
        is_active=True
    )
    
    # Set filter conditions
    rule.set_filter_conditions(data['filter_conditions'])
    
    # Set dashboard config if provided
    if 'dashboard_config' in data:
        rule.set_dashboard_config(data['dashboard_config'])
    
    db.session.add(rule)
    db.session.commit()
    
    return rule


def get_rules_by_type(user_id, rule_type, include_shared=False, organization_id=None):
    """
    Get all rules of a specific type for a user
    
    Args:
        user_id: ID of the user
        rule_type: Type of rules to fetch ('priority', 'churn', 'upsell', 'custom', or 'all')
        include_shared: Include shared rules from same organization
        organization_id: Organization ID for shared rules
    
    Returns:
        List of AccountRule objects
    """
    # Base query - user's own rules
    query = AccountRule.query.filter_by(
        created_by=user_id,
        is_active=True
    )
    
    # Filter by rule type if not 'all'
    if rule_type != 'all':
        query = query.filter_by(rule_type=rule_type)
    
    rules = query.all()
    
    # Include shared rules if requested
    if include_shared and organization_id:
        shared_query = AccountRule.query.filter_by(
            rule_type=rule_type,
            is_active=True,
            is_shared=True,
            organization_id=organization_id
        ).filter(AccountRule.created_by != user_id)
        
        rules.extend(shared_query.all())
    
    # Sort by priority order
    rules.sort(key=lambda r: r.priority_order)
    
    return rules


def get_rule_by_id(rule_id):
    """Get a specific rule by ID"""
    return AccountRule.query.get(rule_id)


def update_rule(rule_id, data, user_id):
    """
    Update an existing rule
    
    Args:
        rule_id: ID of the rule to update
        data: Dictionary with fields to update
        user_id: ID of user making the update
    
    Returns:
        Updated AccountRule object or None if unauthorized/not found
    """
    rule = AccountRule.query.get(rule_id)
    if not rule or not rule.can_edit(user_id):
        return None
    
    # Update fields
    if 'rule_name' in data:
        rule.rule_name = data['rule_name']
    if 'description' in data:
        rule.description = data['description']
    if 'filter_conditions' in data:
        rule.set_filter_conditions(data['filter_conditions'])
    if 'dashboard_config' in data:
        rule.set_dashboard_config(data['dashboard_config'])
    if 'is_active' in data:
        rule.is_active = data['is_active']
    if 'is_shared' in data:
        rule.is_shared = data['is_shared']
    if 'priority_order' in data:
        rule.priority_order = data['priority_order']
    
    rule.updated_at = datetime.utcnow()
    
    # Invalidate cache
    rule.cache_updated_at = None
    
    db.session.commit()
    return rule


def delete_rule(rule_id, user_id):
    """
    Delete a rule
    
    Args:
        rule_id: ID of the rule to delete
        user_id: ID of user making the deletion
    
    Returns:
        True if deleted, False if unauthorized/not found
    """
    rule = AccountRule.query.get(rule_id)
    if not rule or not rule.can_delete(user_id):
        return False
    
    db.session.delete(rule)
    db.session.commit()
    return True


def get_accounts_by_rule(rule_id, user_id, use_cache=True):
    """
    Get all accounts matching a specific rule (with optional caching)
    
    Args:
        rule_id: ID of the rule
        user_id: ID of the user (for filtering accounts)
        use_cache: Whether to use cached results
    
    Returns:
        List of Account objects matching the rule
    """
    rule = AccountRule.query.get(rule_id)
    if not rule:
        return None
    
    # Check cache validity (5 minutes)
    if use_cache and rule.cache_updated_at:
        cache_age = (datetime.utcnow() - rule.cache_updated_at).total_seconds()
        if cache_age < 300:  # 5 minutes
            # Return cached count (actual accounts still need to be queried)
            pass
    
    # Apply filters using SQLAlchemy
    accounts = apply_rule_filters(rule, user_id)
    
    # Update cache
    rule.cached_account_count = len(accounts)
    rule.cache_updated_at = datetime.utcnow()
    rule.last_executed_at = datetime.utcnow()
    db.session.commit()
    
    return accounts


def apply_rule_filters(rule, user_id):
    """
    Apply rule filters to get matching accounts (SQLAlchemy queries)
    
    Args:
        rule: AccountRule object
        user_id: ID of user (for filtering accounts by CSM)
    
    Returns:
        List of Account objects
    """
    filter_conditions = rule.get_filter_conditions()
    
    # Start with all accounts for this user
    query = Account.query.filter(Account.csm_user_id == user_id)
    
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
        elif operator == 'contains':
            query = query.filter(column != None).filter(column.like(f"%{value}%"))
        elif operator == 'not_contains':
            query = query.filter(column != None).filter(~column.like(f"%{value}%"))
        elif operator == 'in':
            query = query.filter(column.in_(value))
        elif operator == 'not_in':
            query = query.filter(~column.in_(value))
    
    return query.all()


def get_accounts_by_user_rules(user_id, rule_type=None):
    """
    Get all accounts that match ANY rule for a user (OR logic)
    
    Args:
        user_id: ID of the user
        rule_type: Optional filter by rule type
    
    Returns:
        Dictionary with rules and their matching accounts
    """
    # Get all active rules for user
    if rule_type:
        rules = get_rules_by_type(user_id, rule_type)
    else:
        rules = get_rules_by_type(user_id, 'all')
    
    if not rules:
        return None
    
    # Collect all matching accounts for each rule
    result = {
        'user_id': user_id,
        'total_rules': len(rules),
        'rules': []
    }
    
    all_account_ids = set()
    
    for rule in rules:
        accounts = get_accounts_by_rule(rule.id, user_id)
        
        if accounts:
            account_ids = [acc.id for acc in accounts]
            all_account_ids.update(account_ids)
            
            result['rules'].append({
                'rule_id': rule.id,
                'rule_name': rule.rule_name,
                'rule_type': rule.rule_type,
                'description': rule.description,
                'filter_conditions': rule.get_filter_conditions(),
                'matching_accounts_count': len(accounts),
                'matching_account_ids': account_ids
            })
    
    # Get unique accounts
    unique_accounts = Account.query.filter(
        Account.id.in_(all_account_ids),
        Account.csm_user_id == user_id
    ).all() if all_account_ids else []
    
    result['total_unique_accounts'] = len(unique_accounts)
    result['accounts'] = unique_accounts
    
    return result
