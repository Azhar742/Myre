from models.user_model import db
from datetime import datetime
from sqlalchemy import Index

class Organization(db.Model):
    """
    Organization/Company model for multi-tenant architecture.
    Each organization can have multiple users (employees) and accounts (customers).
    """
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Basic Information
    org_name = db.Column(db.String(200), nullable=False, index=True)
    org_slug = db.Column(db.String(100), unique=True, nullable=False, index=True)  # URL-friendly identifier
    org_email = db.Column(db.String(150), nullable=False)
    org_phone = db.Column(db.String(20), nullable=True)
    
    # Address Information
    org_address = db.Column(db.String(300), nullable=True)
    org_city = db.Column(db.String(100), nullable=True)
    org_state = db.Column(db.String(100), nullable=True)
    org_country = db.Column(db.String(100), nullable=True)
    org_zipcode = db.Column(db.String(20), nullable=True)
    
    # Business Information
    org_industry = db.Column(db.String(100), nullable=True)
    org_size = db.Column(db.String(50), nullable=True)  # e.g., '1-10', '11-50', '51-200', '201-500', '500+'
    org_website = db.Column(db.String(200), nullable=True)
    
    # Subscription & Plan
    subscription_plan = db.Column(db.String(50), default='free')  # 'free', 'basic', 'pro', 'enterprise'
    subscription_status = db.Column(db.String(50), default='active')  # 'active', 'suspended', 'cancelled'
    subscription_start_date = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    
    # Limits based on plan (nullable - no hard limits enforced)
    max_users = db.Column(db.Integer, nullable=True)  # Maximum users allowed (optional)
    max_accounts = db.Column(db.Integer, nullable=True)  # Maximum customer accounts (optional)
    
    # Status & Timestamps
    org_status = db.Column(db.String(50), default='active', index=True)  # 'active', 'inactive', 'suspended'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)
    
    # Settings (JSON stored as text)
    settings = db.Column(db.Text, nullable=True)  # Store JSON configuration
    
    # Relationships
    users = db.relationship('User', backref='organization', lazy='dynamic', 
                           foreign_keys='User.organization_id')
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_org_slug', 'org_slug'),
        Index('idx_org_status', 'org_status'),
        Index('idx_org_deleted', 'deleted_at'),
        Index('idx_org_subscription', 'subscription_status', 'subscription_plan'),
    )

    def __repr__(self):
        return f'<Organization {self.org_name} ({self.org_slug})>'
    
    def to_dict(self):
        """Serialize organization to dictionary"""
        return {
            'id': self.id,
            'org_name': self.org_name,
            'org_slug': self.org_slug,
            'org_email': self.org_email,
            'org_phone': self.org_phone,
            'org_address': self.org_address,
            'org_city': self.org_city,
            'org_state': self.org_state,
            'org_country': self.org_country,
            'org_zipcode': self.org_zipcode,
            'org_industry': self.org_industry,
            'org_size': self.org_size,
            'org_website': self.org_website,
            'subscription_plan': self.subscription_plan,
            'subscription_status': self.subscription_status,
            'subscription_start_date': self.subscription_start_date.isoformat() if self.subscription_start_date else None,
            'subscription_end_date': self.subscription_end_date.isoformat() if self.subscription_end_date else None,
            'max_users': self.max_users,
            'max_accounts': self.max_accounts,
            'org_status': self.org_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_active_users_count(self):
        """Get count of active users in this organization"""
        return self.users.filter_by(user_status='active', user_deleted_at=None).count()
    
    def can_add_user(self):
        """Check if organization can add more users based on plan limits"""
        # If no limit set, always allow
        if self.max_users is None:
            return True
        return self.get_active_users_count() < self.max_users
    
    def is_active(self):
        """Check if organization is active and not deleted"""
        return self.org_status == 'active' and self.deleted_at is None
