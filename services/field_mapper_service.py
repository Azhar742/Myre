# services/field_mapper_service.py - Field Mapping Service
import logging
from typing import Dict, List, Any, Optional
from models.field_mapping import FieldMapping
from models.tenant import Tenant
from extensions import db
import json

logger = logging.getLogger(__name__)

class FieldMapperService:
    """Service for handling field mapping operations"""
    
    def __init__(self, tenant_code: str):
        self.tenant_code = tenant_code
        self.tenant = None
        self.mappings_cache = {}
        self._load_tenant()
    
    def _load_tenant(self):
        """Load tenant and cache field mappings"""
        logger.info(f'Loading tenant configuration', extra={
            'extra_data': {'tenant_code': self.tenant_code}
        })
        
        self.tenant = Tenant.query.filter_by(
            tenant_code=self.tenant_code,
            is_active=True
        ).first()
        
        if not self.tenant:
            logger.error(f'Tenant not found or inactive', extra={
                'extra_data': {'tenant_code': self.tenant_code}
            })
            raise ValueError(f'Tenant {self.tenant_code} not found or inactive')
        
        # Cache mappings
        mappings = FieldMapping.query.filter_by(tenant_id=self.tenant.id).all()
        self.mappings_cache = {
            mapping.canonical_field: mapping for mapping in mappings
        }
        
        logger.info(f'Loaded {len(self.mappings_cache)} field mappings', extra={
            'extra_data': {
                'tenant_id': self.tenant.id,
                'mapping_count': len(self.mappings_cache)
            }
        })
    
    def to_tenant_field(self, canonical_field: str) -> str:
        """Convert canonical field name to tenant-specific field name"""
        if canonical_field not in self.mappings_cache:
            logger.warning(f'No mapping found for canonical field', extra={
                'extra_data': {
                    'canonical_field': canonical_field,
                    'tenant_code': self.tenant_code
                }
            })
            return canonical_field
        
        return self.mappings_cache[canonical_field].tenant_field_name
    
    def to_display_label(self, canonical_field: str) -> str:
        """Get tenant-specific display label for field"""
        if canonical_field not in self.mappings_cache:
            return canonical_field.replace('_', ' ').title()
        
        return self.mappings_cache[canonical_field].tenant_display_label
    
    def get_visible_fields(self) -> List[Dict[str, Any]]:
        """Get all visible fields with their display configuration"""
        visible_fields = [
            {
                'canonical_field': field,
                'display_label': mapping.tenant_display_label,
                'field_type': mapping.field_type,
                'is_required': mapping.is_required,
                'display_order': mapping.display_order
            }
            for field, mapping in self.mappings_cache.items()
            if mapping.is_visible
        ]
        
        # Sort by display_order
        visible_fields.sort(key=lambda x: x['display_order'])
        
        logger.debug(f'Retrieved visible fields', extra={
            'extra_data': {
                'tenant_code': self.tenant_code,
                'field_count': len(visible_fields)
            }
        })
        
        return visible_fields
    
    def transform_db_to_response(self, db_row: Dict[str, Any]) -> Dict[str, Any]:
        """Transform database row to API response format"""
        response = {}
        
        for canonical_field, mapping in self.mappings_cache.items():
            if not mapping.is_visible:
                continue
            
            tenant_field = mapping.tenant_field_name
            value = db_row.get(tenant_field)
            
            # Apply transformation if defined
            if mapping.transformation_rule and value is not None:
                try:
                    rules = json.loads(mapping.transformation_rule)
                    value = self._apply_transformation(value, rules)
                except Exception as e:
                    logger.error(f'Transformation failed', extra={
                        'extra_data': {
                            'canonical_field': canonical_field,
                            'error': str(e)
                        }
                    })
            
            response[canonical_field] = {
                'label': mapping.tenant_display_label,
                'value': value,
                'type': mapping.field_type
            }
        
        return response
    
    def _apply_transformation(self, value: Any, rules: Dict[str, Any]) -> Any:
        """Apply transformation rules to field value"""
        # Example transformations
        if rules.get('type') == 'date_format':
            # Transform date format
            pass
        elif rules.get('type') == 'phone_format':
            # Transform phone number format
            pass
        
        return value
    
    def build_query_fields(self, canonical_fields: List[str]) -> List[str]:
        """Build list of tenant-specific field names for query"""
        tenant_fields = []
        
        for canonical_field in canonical_fields:
            tenant_field = self.to_tenant_field(canonical_field)
            tenant_fields.append(tenant_field)
            
            logger.debug(f'Field mapping', extra={
                'extra_data': {
                    'canonical': canonical_field,
                    'tenant': tenant_field
                }
            })
        
        return tenant_fields
