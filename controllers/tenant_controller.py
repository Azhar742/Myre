# controllers/tenant_controller.py - Tenant Management Controller
from flask import Blueprint, request, jsonify
from models.tenant import Tenant
from models.field_mapping import FieldMapping
from extensions import db
import logging

tenant_bp = Blueprint('tenants', __name__)
logger = logging.getLogger(__name__)

@tenant_bp.route('/', methods=['POST'])
def create_tenant():
    """Create new tenant with field mappings"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('tenant_code') or not data.get('tenant_name'):
            return jsonify({'error': 'tenant_code and tenant_name are required'}), 400
        
        # Create tenant
        tenant = Tenant(
            tenant_code=data['tenant_code'],
            tenant_name=data['tenant_name'],
            database_schema=data.get('database_schema')
        )
        
        db.session.add(tenant)
        db.session.flush()  # Get tenant ID
        
        # Create field mappings
        mappings_data = data.get('field_mappings', [])
        for mapping_data in mappings_data:
            mapping = FieldMapping(
                tenant_id=tenant.id,
                canonical_field=mapping_data['canonical_field'],
                tenant_field_name=mapping_data['tenant_field_name'],
                tenant_display_label=mapping_data['tenant_display_label'],
                field_type=mapping_data.get('field_type', 'string'),
                is_required=mapping_data.get('is_required', False),
                is_visible=mapping_data.get('is_visible', True),
                display_order=mapping_data.get('display_order', 0)
            )
            db.session.add(mapping)
        
        db.session.commit()
        
        logger.info(f'Created tenant', extra={
            'extra_data': {
                'tenant_code': tenant.tenant_code,
                'mapping_count': len(mappings_data)
            }
        })
        
        return jsonify({
            'message': 'Tenant created successfully',
            'tenant': tenant.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error('Error creating tenant', exc_info=True)
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/<tenant_code>/mappings', methods=['GET'])
def get_tenant_mappings(tenant_code):
    """Get field mappings for a tenant"""
    try:
        tenant = Tenant.query.filter_by(tenant_code=tenant_code).first()
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        mappings = FieldMapping.query.filter_by(tenant_id=tenant.id).all()
        
        return jsonify({
            'tenant': tenant.to_dict(),
            'mappings': [m.to_dict() for m in mappings]
        }), 200
        
    except Exception as e:
        logger.error('Error fetching tenant mappings', exc_info=True)
        return jsonify({'error': str(e)}), 500
