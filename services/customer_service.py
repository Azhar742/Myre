import logging
from typing import List, Dict, Any, Optional
from services.field_mapper_service import FieldMapperService
from services.supabase_service import SupabaseService
from extensions import db

logger = logging.getLogger(__name__)

class CustomerService:
    """Service for customer data operations"""
    
    def __init__(self, tenant_code: str, use_supabase: bool = True):
        self.tenant_code = tenant_code
        self.use_supabase = use_supabase
        self.field_mapper = FieldMapperService(tenant_code)
        
        if use_supabase:
            self.supabase = SupabaseService()
    
    def get_customers(self, filters: Optional[Dict[str, Any]] = None, 
                     limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get customers with tenant-specific field mapping"""
        
        logger.info(f'Fetching customers', extra={
            'extra_data': {
                'tenant_code': self.tenant_code,
                'limit': limit,
                'offset': offset,
                'filters': filters,
                'use_supabase': self.use_supabase
            }
        })
        
        try:
            # Get visible fields configuration
            visible_fields = self.field_mapper.get_visible_fields()
            canonical_fields = [f['canonical_field'] for f in visible_fields]
            
            # Build tenant-specific field list for query
            tenant_fields = self.field_mapper.build_query_fields(canonical_fields)
            
            if self.use_supabase:
                # Query Supabase
                customers_data = self._query_supabase_customers(
                    tenant_fields, filters, limit, offset
                )
            else:
                # Query PostgreSQL directly via SQLAlchemy
                customers_data = self._query_db_customers(
                    tenant_fields, filters, limit, offset
                )
            
            # Transform results using field mapper
            customers = []
            for row in customers_data:
                transformed = self.field_mapper.transform_db_to_response(row)
                customers.append(transformed)
            
            logger.info(f'Successfully fetched customers', extra={
                'extra_data': {
                    'tenant_code': self.tenant_code,
                    'customer_count': len(customers)
                }
            })
            
            return {
                'customers': customers,
                'field_config': visible_fields,
                'total': len(customers),
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            logger.error(f'Error fetching customers', extra={
                'extra_data': {
                    'tenant_code': self.tenant_code,
                    'error': str(e)
                }
            }, exc_info=True)
            raise
    
    def _query_supabase_customers(self, tenant_fields: List[str], 
                                 filters: Optional[Dict[str, Any]],
                                 limit: int, offset: int) -> List[Dict[str, Any]]:
        """Query customers from Supabase"""
        
        # Build select string
        select_fields = ", ".join(tenant_fields)
        
        # Map canonical filters to tenant field names if provided
        tenant_filters = {}
        if filters:
            for canonical_field, value in filters.items():
                tenant_field = self.field_mapper.to_tenant_field(canonical_field)
                tenant_filters[tenant_field] = value
        
        # Query Supabase
        return self.supabase.query_table(
            table_name='customers',
            filters=tenant_filters,
            select=select_fields,
            limit=limit,
            offset=offset
        )
    
    def _query_db_customers(self, tenant_fields: List[str], 
                           filters: Optional[Dict[str, Any]],
                           limit: int, offset: int) -> List[Dict[str, Any]]:
        """Query customers from PostgreSQL directly"""
        from sqlalchemy import text
        
        query = f"SELECT {', '.join(tenant_fields)} FROM customers LIMIT :limit OFFSET :offset"
        result = db.session.execute(
            text(query),
            {'limit': limit, 'offset': offset}
        )
        
        return [dict(zip(tenant_fields, row)) for row in result]
    
    def get_customer_by_id(self, customer_id: Any) -> Optional[Dict[str, Any]]:
        """Get single customer by ID"""
        
        logger.info(f'Fetching customer by ID', extra={
            'extra_data': {
                'tenant_code': self.tenant_code,
                'customer_id': customer_id,
                'use_supabase': self.use_supabase
            }
        })
        
        try:
            # Get field configuration
            visible_fields = self.field_mapper.get_visible_fields()
            canonical_fields = [f['canonical_field'] for f in visible_fields]
            tenant_fields = self.field_mapper.build_query_fields(canonical_fields)
            
            # Get ID field mapping
            id_field = self.field_mapper.to_tenant_field('customer_id')
            
            if self.use_supabase:
                # Query from Supabase
                select_fields = ", ".join(tenant_fields)
                result = self.supabase.get_by_id('customers', id_field, customer_id)
            else:
                # Query from PostgreSQL
                from sqlalchemy import text
                query = f"SELECT {', '.join(tenant_fields)} FROM customers WHERE {id_field} = :customer_id"
                result_row = db.session.execute(
                    text(query),
                    {'customer_id': customer_id}
                ).fetchone()
                result = dict(zip(tenant_fields, result_row)) if result_row else None
            
            if not result:
                logger.warning(f'Customer not found', extra={
                    'extra_data': {
                        'tenant_code': self.tenant_code,
                        'customer_id': customer_id
                    }
                })
                return None
            
            transformed = self.field_mapper.transform_db_to_response(result)
            
            logger.info(f'Successfully fetched customer', extra={
                'extra_data': {
                    'tenant_code': self.tenant_code,
                    'customer_id': customer_id
                }
            })
            
            return transformed
            
        except Exception as e:
            logger.error(f'Error fetching customer', extra={
                'extra_data': {
                    'tenant_code': self.tenant_code,
                    'customer_id': customer_id,
                    'error': str(e)
                }
            }, exc_info=True)
            raise