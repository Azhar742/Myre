import logging
from typing import Dict, Any, List, Optional
from extensions import get_supabase_client, get_supabase_admin_client
from supabase import Client

logger = logging.getLogger(__name__)

class SupabaseService:
    """Service for Supabase operations"""
    
    def __init__(self, use_admin: bool = False):
        """
        Initialize Supabase service
        
        Args:
            use_admin: If True, use service role key for admin operations
        """
        self.client: Client = (
            get_supabase_admin_client() if use_admin 
            else get_supabase_client()
        )
    
    def query_table(self, table_name: str, 
                   filters: Optional[Dict[str, Any]] = None,
                   select: str = "*",
                   limit: int = 100,
                   offset: int = 0) -> List[Dict[str, Any]]:
        """
        Query a Supabase table with filters
        
        Args:
            table_name: Name of the table
            filters: Dictionary of field: value filters
            select: Fields to select (default: all)
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of records
        """
        try:
            logger.info(f'Querying Supabase table', extra={
                'extra_data': {
                    'table': table_name,
                    'filters': filters,
                    'limit': limit,
                    'offset': offset
                }
            })
            
            query = self.client.table(table_name).select(select)
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    query = query.eq(field, value)
            
            # Apply pagination
            query = query.range(offset, offset + limit - 1)
            
            response = query.execute()
            
            logger.info(f'Successfully queried table', extra={
                'extra_data': {
                    'table': table_name,
                    'record_count': len(response.data)
                }
            })
            
            return response.data
            
        except Exception as e:
            logger.error(f'Error querying Supabase table', extra={
                'extra_data': {
                    'table': table_name,
                    'error': str(e)
                }
            }, exc_info=True)
            raise
    
    def get_by_id(self, table_name: str, id_field: str, 
                  id_value: Any) -> Optional[Dict[str, Any]]:
        """Get single record by ID"""
        try:
            response = self.client.table(table_name)\
                .select("*")\
                .eq(id_field, id_value)\
                .limit(1)\
                .execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f'Error fetching record by ID', extra={
                'extra_data': {
                    'table': table_name,
                    'id_field': id_field,
                    'id_value': id_value,
                    'error': str(e)
                }
            }, exc_info=True)
            raise
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a record into Supabase table"""
        try:
            logger.info(f'Inserting record', extra={
                'extra_data': {
                    'table': table_name
                }
            })
            
            response = self.client.table(table_name).insert(data).execute()
            
            logger.info(f'Successfully inserted record', extra={
                'extra_data': {
                    'table': table_name,
                    'record_id': response.data[0].get('id') if response.data else None
                }
            })
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f'Error inserting record', extra={
                'extra_data': {
                    'table': table_name,
                    'error': str(e)
                }
            }, exc_info=True)
            raise
    
    def update(self, table_name: str, id_field: str, 
              id_value: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record in Supabase table"""
        try:
            logger.info(f'Updating record', extra={
                'extra_data': {
                    'table': table_name,
                    'id_field': id_field,
                    'id_value': id_value
                }
            })
            
            response = self.client.table(table_name)\
                .update(data)\
                .eq(id_field, id_value)\
                .execute()
            
            logger.info(f'Successfully updated record', extra={
                'extra_data': {
                    'table': table_name
                }
            })
            
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f'Error updating record', extra={
                'extra_data': {
                    'table': table_name,
                    'error': str(e)
                }
            }, exc_info=True)
            raise
    
    def delete(self, table_name: str, id_field: str, id_value: Any) -> bool:
        """Delete a record from Supabase table"""
        try:
            logger.info(f'Deleting record', extra={
                'extra_data': {
                    'table': table_name,
                    'id_field': id_field,
                    'id_value': id_value
                }
            })
            
            self.client.table(table_name)\
                .delete()\
                .eq(id_field, id_value)\
                .execute()
            
            logger.info(f'Successfully deleted record', extra={
                'extra_data': {
                    'table': table_name
                }
            })
            
            return True
            
        except Exception as e:
            logger.error(f'Error deleting record', extra={
                'extra_data': {
                    'table': table_name,
                    'error': str(e)
                }
            }, exc_info=True)
            raise
    
    def execute_rpc(self, function_name: str, params: Dict[str, Any]) -> Any:
        """
        Execute a Supabase PostgreSQL function (RPC)
        
        Args:
            function_name: Name of the PostgreSQL function
            params: Function parameters
        
        Returns:
            Function result
        """
        try:
            logger.info(f'Executing RPC function', extra={
                'extra_data': {
                    'function': function_name,
                    'params': params
                }
            })
            
            response = self.client.rpc(function_name, params).execute()
            
            return response.data
            
        except Exception as e:
            logger.error(f'Error executing RPC', extra={
                'extra_data': {
                    'function': function_name,
                    'error': str(e)
                }
            }, exc_info=True)
            raise