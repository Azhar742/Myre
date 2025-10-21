from datetime import datetime
from models.user_model import db
import json


class AccountRule(db.Model):
    """Unified model for all account filtering rules (priority, churn, upsell, custom)"""
    __tablename__ = 'account_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Rule metadata
    rule_name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    rule_type = db.Column(db.String(50), nullable=False, index=True)  # 'priority', 'churn', 'upsell', 'custom'
    
    # Filter conditions stored as JSON
    # Format: {"field_name": {"operator": "==", "value": "active"}}
    filter_conditions = db.Column(db.Text, nullable=False)
    
    # Ownership & permissions
    created_by = db.Column(db.Integer, nullable=False, index=True)
    organization_id = db.Column(db.Integer, index=True)  # For multi-tenancy (future)
    is_shared = db.Column(db.Boolean, default=False)  # Share with team
    
    # Dashboard configuration (JSON)
    # Format: {"color": "#ff0000", "icon": "alert", "position": 1, "widget_type": "card"}
    dashboard_config = db.Column(db.Text)
    
    # Status & metadata
    is_active = db.Column(db.Boolean, default=True, index=True)
    priority_order = db.Column(db.Integer, default=0)  # For sorting rules
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_executed_at = db.Column(db.DateTime)  # Track when rule was last run
    
    # Performance optimization - cache results
    cached_account_count = db.Column(db.Integer, default=0)
    cache_updated_at = db.Column(db.DateTime)
    
    # Composite indexes for faster queries
    __table_args__ = (
        db.Index('idx_user_type_active', 'created_by', 'rule_type', 'is_active'),
        db.Index('idx_org_shared', 'organization_id', 'is_shared'),
        db.Index('idx_type_priority', 'rule_type', 'priority_order'),
    )
    
    def get_filter_conditions(self):
        """Parse JSON filter conditions"""
        return json.loads(self.filter_conditions) if self.filter_conditions else {}
    
    def set_filter_conditions(self, conditions_dict):
        """Set filter conditions from dictionary"""
        self.filter_conditions = json.dumps(conditions_dict)
    
    def get_dashboard_config(self):
        """Parse JSON dashboard configuration"""
        return json.loads(self.dashboard_config) if self.dashboard_config else {}
    
    def set_dashboard_config(self, config_dict):
        """Set dashboard configuration from dictionary"""
        self.dashboard_config = json.dumps(config_dict)
    
    def can_view(self, user_id, user_org_id=None, is_admin=False):
        """Check if user can view this rule"""
        if is_admin:
            return True
        if self.created_by == user_id:
            return True
        if self.is_shared and user_org_id and self.organization_id == user_org_id:
            return True
        return False
    
    def can_edit(self, user_id, is_admin=False):
        """Check if user can edit this rule"""
        return self.created_by == user_id or is_admin
    
    def can_delete(self, user_id, is_admin=False):
        """Check if user can delete this rule"""
        return self.created_by == user_id or is_admin
    
    def to_dict(self):
        """Serialize rule to dictionary"""
        return {
            'id': self.id,
            'rule_name': self.rule_name,
            'description': self.description,
            'rule_type': self.rule_type,
            'filter_conditions': self.get_filter_conditions(),
            'dashboard_config': self.get_dashboard_config(),
            'created_by': self.created_by,
            'organization_id': self.organization_id,
            'is_shared': self.is_shared,
            'is_active': self.is_active,
            'priority_order': self.priority_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_executed_at': self.last_executed_at.isoformat() if self.last_executed_at else None,
            'cached_account_count': self.cached_account_count,
            'cache_updated_at': self.cache_updated_at.isoformat() if self.cache_updated_at else None
        }
    
    def __repr__(self):
        return f'<AccountRule {self.rule_type}:{self.rule_name}>'
