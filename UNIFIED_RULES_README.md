# Unified Rules System - Migration Guide

## Overview

The unified rules system consolidates **Priority Rules**, **Churn Rules**, and future rule types (Upsell, Custom) into a single, scalable architecture.

## Benefits

✅ **Single Source of Truth** - One model, one controller for all rule types
✅ **Better Performance** - Indexed queries, caching support, optimized filters
✅ **Enhanced Security** - Row-level permissions, organization-level sharing
✅ **Custom Dashboards** - Fully customizable user dashboards
✅ **Scalability** - Easy to add new rule types without code duplication
✅ **Maintainability** - 70% less code, consistent API

## Architecture

### Models

1. **AccountRule** (`models/account_rule_model.py`)
   - Unified model for all rule types
   - Supports: priority, churn, upsell, custom
   - Features: caching, sharing, permissions

2. **CustomDashboard** (`models/custom_dashboard_model.py`)
   - User-customizable dashboard layouts
   - Widget-based configuration
   - Public/private sharing

### Controller

**rule_controller.py** - Single controller with functions:
- `create_rule()` - Create any type of rule
- `get_rules_by_type()` - Get rules filtered by type
- `update_rule()` - Update existing rule
- `delete_rule()` - Delete rule
- `get_accounts_by_rule()` - Get matching accounts (with caching)
- `apply_rule_filters()` - Apply SQLAlchemy filters
- `get_accounts_by_user_rules()` - Get all accounts matching user's rules

## Migration Steps

### Step 1: Create New Tables

Run these SQL commands to create the new tables:

```sql
-- Create account_rules table
CREATE TABLE account_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name VARCHAR(255) NOT NULL,
    description TEXT,
    rule_type VARCHAR(50) NOT NULL,
    filter_conditions TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    organization_id INTEGER,
    is_shared BOOLEAN DEFAULT 0,
    dashboard_config TEXT,
    is_active BOOLEAN DEFAULT 1,
    priority_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_executed_at DATETIME,
    cached_account_count INTEGER DEFAULT 0,
    cache_updated_at DATETIME
);

-- Create indexes
CREATE INDEX idx_user_type_active ON account_rules(created_by, rule_type, is_active);
CREATE INDEX idx_org_shared ON account_rules(organization_id, is_shared);
CREATE INDEX idx_type_priority ON account_rules(rule_type, priority_order);
CREATE INDEX idx_rule_name ON account_rules(rule_name);
CREATE INDEX idx_created_by ON account_rules(created_by);
CREATE INDEX idx_rule_type ON account_rules(rule_type);
CREATE INDEX idx_is_active ON account_rules(is_active);
CREATE INDEX idx_created_at ON account_rules(created_at);

-- Create custom_dashboards table
CREATE TABLE custom_dashboards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dashboard_name VARCHAR(255) NOT NULL,
    created_by INTEGER NOT NULL,
    layout_config TEXT NOT NULL,
    is_default BOOLEAN DEFAULT 0,
    is_public BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_viewed_at DATETIME
);

CREATE INDEX idx_dashboard_created_by ON custom_dashboards(created_by);
```

### Step 2: Run Migration Script

```bash
cd /path/to/Myre
python3 migrations/migrate_to_unified_rules.py
```

This will:
1. Migrate all priority_conditions → account_rules (type='priority')
2. Migrate all churn_conditions → account_rules (type='churn')
3. Verify migration success
4. Optionally drop old tables (if you confirm)

### Step 3: Update app.py

Add new unified API routes (see `UNIFIED_API_ROUTES.md` for details)

### Step 4: Update Frontend

Update JavaScript to use new unified API endpoints

### Step 5: Test

Test all functionality:
- Create new rules
- View rules by type
- Filter accounts
- Custom dashboards

## API Usage Examples

### Create a Priority Rule

```python
from controllers.rule_controller import create_rule

rule_data = {
    'rule_name': 'High Value Clients',
    'description': 'Clients with high revenue',
    'rule_type': 'priority',
    'filter_conditions': {
        'last_paid_bill_amount': {'operator': '>', 'value': '1000'}
    },
    'created_by': 1,
    'dashboard_config': {
        'color': '#28a745',
        'icon': 'star',
        'position': 1
    }
}

rule = create_rule(rule_data)
```

### Create a Churn Rule

```python
rule_data = {
    'rule_name': 'Inactive Users',
    'description': 'Users inactive for 30+ days',
    'rule_type': 'churn',
    'filter_conditions': {
        'last_login': {'operator': '<', 'value': '30'}
    },
    'created_by': 1,
    'dashboard_config': {
        'color': '#dc3545',
        'icon': 'alert',
        'position': 2
    }
}

rule = create_rule(rule_data)
```

### Get All Rules for a User

```python
from controllers.rule_controller import get_rules_by_type

# Get all priority rules
priority_rules = get_rules_by_type(user_id=1, rule_type='priority')

# Get all churn rules
churn_rules = get_rules_by_type(user_id=1, rule_type='churn')

# Get ALL rules
all_rules = get_rules_by_type(user_id=1, rule_type='all')
```

### Get Accounts Matching a Rule

```python
from controllers.rule_controller import get_accounts_by_rule

accounts = get_accounts_by_rule(rule_id=5, user_id=1)
print(f"Found {len(accounts)} matching accounts")
```

## Security Features

### Row-Level Permissions

```python
rule = AccountRule.query.get(rule_id)

# Check if user can view
if rule.can_view(user_id=1):
    # Show rule

# Check if user can edit
if rule.can_edit(user_id=1):
    # Allow editing

# Check if user can delete
if rule.can_delete(user_id=1):
    # Allow deletion
```

### Organization Sharing

```python
# Create a shared rule
rule_data = {
    'rule_name': 'Team Priority Accounts',
    'rule_type': 'priority',
    'filter_conditions': {...},
    'created_by': 1,
    'organization_id': 100,
    'is_shared': True  # Share with organization
}

rule = create_rule(rule_data)

# Get rules including shared ones
rules = get_rules_by_type(
    user_id=2,
    rule_type='priority',
    include_shared=True,
    organization_id=100
)
```

## Performance Optimizations

### Caching

```python
# First call - queries database and caches result
accounts = get_accounts_by_rule(rule_id=5, user_id=1, use_cache=True)

# Second call within 5 minutes - uses cached count
accounts = get_accounts_by_rule(rule_id=5, user_id=1, use_cache=True)
```

### Indexes

All critical queries are optimized with composite indexes:
- `(created_by, rule_type, is_active)` - Fast user rule lookups
- `(organization_id, is_shared)` - Fast shared rule lookups
- `(rule_type, priority_order)` - Fast sorted rule lists

## Future Enhancements

1. **Redis Caching** - Add Redis for distributed caching
2. **Background Jobs** - Periodic cache refresh
3. **Rule Templates** - Pre-built rule templates
4. **Advanced Analytics** - Rule performance metrics
5. **Rule Scheduling** - Time-based rule activation
6. **Webhooks** - Trigger actions when rules match

## Rollback Plan

If migration fails, you can rollback:

1. Keep old tables (`priority_conditions`, `churn_conditions`)
2. Drop new table: `DROP TABLE account_rules;`
3. Revert code changes
4. Continue using old system

## Support

For questions or issues, contact the development team.
