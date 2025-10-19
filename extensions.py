from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from supabase import create_client, Client
from functools import lru_cache
import os

db = SQLAlchemy()
migrate = Migrate()

@lru_cache()
def get_supabase_client() -> Client:
    """Get Supabase client instance (cached)"""
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError('SUPABASE_URL and SUPABASE_KEY must be set')
    
    return create_client(url, key)

@lru_cache()
def get_supabase_admin_client() -> Client:
    """Get Supabase admin client with service role key (cached)"""
    url = os.environ.get('SUPABASE_URL')
    service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not url or not service_key:
        raise ValueError('SUPABASE_URL and SUPABASE_SERVICE_KEY must be set')
    
    return create_client(url, service_key)
