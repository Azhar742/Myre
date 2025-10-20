from models.user_model import db
from datetime import datetime
import json


class PriorityCondition(db.Model):
    __tablename__ = 'priority_conditions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    condition_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Client account ID (optional - for reference purposes)
    client_account_id = db.Column(db.Integer, nullable=True)
    
    # Also keep old column name for backward compatibility
    reference_account_id = db.Column(db.Integer, nullable=True)
    
    # Store filter conditions as JSON
    # Example: {
    #   "account_status": {"operator": "==", "value": "active"},
    #   "plan_name": {"operator": "==", "value": "Enterprise"},
    #   "last_paid_bill_amount": {"operator": ">", "value": 100}
    # }
    filter_conditions = db.Column(db.Text, nullable=False)
    
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f'<PriorityCondition {self.condition_name}>'
    
    def get_filter_conditions(self):
        """Parse JSON filter conditions"""
        return json.loads(self.filter_conditions) if self.filter_conditions else {}
    
    def set_filter_conditions(self, conditions_dict):
        """Set filter conditions from dictionary"""
        self.filter_conditions = json.dumps(conditions_dict)
    
    def to_dict(self):
        """Serialize priority condition to dictionary"""
        return {
            'id': self.id,
            'condition_name': self.condition_name,
            'description': self.description,
            'client_account_id': self.client_account_id or self.reference_account_id,
            'filter_conditions': self.get_filter_conditions(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }
