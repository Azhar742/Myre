# models/field_mapping.py - Field Mapping Model
from extensions import db
from datetime import datetime

class FieldMapping(db.Model):
    __tablename__ = 'field_mappings'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    canonical_field = db.Column(db.String(100), nullable=False)
    tenant_field_name = db.Column(db.String(100), nullable=False)
    tenant_display_label = db.Column(db.String(200), nullable=False)
    field_type = db.Column(db.String(50), default='string')  # string, integer, date, etc.
    transformation_rule = db.Column(db.Text)  # JSON string for transformation logic
    is_required = db.Column(db.Boolean, default=False)
    is_visible = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'canonical_field', name='uq_tenant_canonical_field'),
    )
    
    def __repr__(self):
        return f'<FieldMapping {self.tenant_id}:{self.canonical_field}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'canonical_field': self.canonical_field,
            'tenant_field_name': self.tenant_field_name,
            'tenant_display_label': self.tenant_display_label,
            'field_type': self.field_type,
            'transformation_rule': self.transformation_rule,
            'is_required': self.is_required,
            'is_visible': self.is_visible,
            'display_order': self.display_order
        }
