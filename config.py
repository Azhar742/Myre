import os
from datetime import timedelta
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    USE_SUPABASE_AUTH = os.environ.get('USE_SUPABASE_AUTH', 'False').lower() == 'true'
    
    # Database Configuration (Supabase PostgreSQL)
    # Construct DATABASE_URL from individual components (Supabase recommended approach)
    _user = os.environ.get('user', 'postgres')
    _password = os.environ.get('password', '')
    _host = os.environ.get('host', 'localhost')
    _port = os.environ.get('port', '5432')
    _dbname = os.environ.get('dbname', 'postgres')
    
    # Use DATABASE_URL if provided, otherwise construct from components
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    else:
        # URL-encode password to handle special characters
        _encoded_password = quote_plus(_password)
        SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{_user}:{_encoded_password}@{_host}:{_port}/{_dbname}?sslmode=require"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    JSON_SORT_KEYS = False
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.environ.get('LOG_FORMAT', 'json')