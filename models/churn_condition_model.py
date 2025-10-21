from datetime import datetime
from models.user_model import db
import json

class ChurnCondition(db.Model):
    """Model for churn risk conditions/rules"""
    __tablename__ = 'churn_conditions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)  # No FK constraint to avoid circular dependency
    condition_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Filter conditions stored as JSON (same as PriorityCondition)
    # Format: {"field_name": {"operator": "==", "value": "active"}}
    filter_conditions = db.Column(db.Text, nullable=False)
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=False, index=True)  # User who created this condition
    
    def get_filter_conditions(self):
        """Parse JSON filter conditions"""
        return json.loads(self.filter_conditions) if self.filter_conditions else {}
    
    def set_filter_conditions(self, conditions_dict):
        """Set filter conditions from dictionary"""
        self.filter_conditions = json.dumps(conditions_dict)
    
    def to_dict(self):
        """Serialize churn condition to dictionary"""
        return {
            'id': self.id,
            'condition_name': self.condition_name,
            'description': self.description,
            'filter_conditions': self.get_filter_conditions(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }
    
    def __repr__(self):
        return f'<ChurnCondition {self.condition_name}>'
