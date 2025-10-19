# models/tenant.py - Tenant Model
from extensions import db
from datetime import datetime

class Tenant(db.Model):
    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    tenant_name = db.Column(db.String(200), nullable=False)
    database_schema = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    field_mappings = db.relationship('FieldMapping', backref='tenant', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Tenant {self.tenant_code}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_code': self.tenant_code,
            'tenant_name': self.tenant_name,
            'database_schema': self.database_schema,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
