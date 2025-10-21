from datetime import datetime
from models.user_model import db
import json


class CustomDashboard(db.Model):
    """User-customizable dashboards"""
    __tablename__ = 'custom_dashboards'
    
    id = db.Column(db.Integer, primary_key=True)
    dashboard_name = db.Column(db.String(255), nullable=False)
    created_by = db.Column(db.Integer, nullable=False, index=True)
    
    # Dashboard layout configuration (JSON)
    # Format: {
    #   "widgets": [
    #     {"type": "rule", "rule_id": 1, "position": {"x": 0, "y": 0, "w": 6, "h": 4}},
    #     {"type": "chart", "chart_type": "bar", "data_source": "rule:2", "position": {"x": 6, "y": 0, "w": 6, "h": 4}}
    #   ],
    #   "theme": "light",
    #   "refresh_interval": 300
    # }
    layout_config = db.Column(db.Text, nullable=False)
    
    # Dashboard settings
    is_default = db.Column(db.Boolean, default=False)  # User's default dashboard
    is_public = db.Column(db.Boolean, default=False)  # Share with organization
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_viewed_at = db.Column(db.DateTime)
    
    def get_layout_config(self):
        """Parse JSON layout configuration"""
        return json.loads(self.layout_config) if self.layout_config else {}
    
    def set_layout_config(self, config_dict):
        """Set layout configuration from dictionary"""
        self.layout_config = json.dumps(config_dict)
    
    def to_dict(self):
        """Serialize dashboard to dictionary"""
        return {
            'id': self.id,
            'dashboard_name': self.dashboard_name,
            'created_by': self.created_by,
            'layout_config': self.get_layout_config(),
            'is_default': self.is_default,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_viewed_at': self.last_viewed_at.isoformat() if self.last_viewed_at else None
        }
    
    def __repr__(self):
        return f'<CustomDashboard {self.dashboard_name}>'
