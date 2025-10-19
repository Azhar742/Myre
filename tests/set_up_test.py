#!/usr/bin/env python3
"""
Setup Verification Script
Run this to verify your environment is configured correctly
"""

import sys
import os
from pathlib import Path

def print_status(message, status):
    """Print colored status message"""
    colors = {
        'OK': '\033[92m✓',      # Green
        'FAIL': '\033[91m✗',    # Red
        'WARN': '\033[93m⚠',    # Yellow
        'INFO': '\033[94mℹ'     # Blue
    }
    reset = '\033[0m'
    symbol = colors.get(status, '?')
    print(f"{symbol} {message}{reset}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_status(f"Python version {version.major}.{version.minor}.{version.micro}", 'OK')
        return True
    else:
        print_status(f"Python version {version.major}.{version.minor}.{version.micro} (Need 3.8+)", 'FAIL')
        return False

def check_virtual_env():
    """Check if running in virtual environment"""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if in_venv:
        print_status("Virtual environment active", 'OK')
        return True
    else:
        print_status("Not in virtual environment (recommended to use one)", 'WARN')
        return True

def check_required_packages():
    """Check if required packages are installed"""
    required = {
        'flask': 'Flask',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'flask_migrate': 'Flask-Migrate',
        'supabase': 'Supabase',
        'psycopg2': 'psycopg2-binary',
        'dotenv': 'python-dotenv'
    }
    
    all_ok = True
    for module, package in required.items():
        try:
            __import__(module)
            print_status(f"Package '{package}' installed", 'OK')
        except ImportError:
            print_status(f"Package '{package}' NOT installed", 'FAIL')
            print(f"   Install with: pip install {package}")
            all_ok = False
    
    return all_ok

def check_project_structure():
    """Check if project structure exists"""
    required_files = [
        'app.py',
        'config.py',
        'extensions.py',
        'logging_config.py',
        'requirements.txt',
        '.env'
    ]
    
    required_dirs = [
        'models',
        'services',
        'controllers',
        'utils'
    ]
    
    all_ok = True
    
    for file in required_files:
        if Path(file).exists():
            print_status(f"File '{file}' exists", 'OK')
        else:
            print_status(f"File '{file}' missing", 'FAIL')
            all_ok = False
    
    for dir in required_dirs:
        if Path(dir).is_dir():
            print_status(f"Directory '{dir}/' exists", 'OK')
        else:
            print_status(f"Directory '{dir}/' missing", 'FAIL')
            all_ok = False
    
    return all_ok

def check_env_variables():
    """Check if environment variables are set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'SUPABASE_URL': 'https://xxxxx.supabase.co',
        'SUPABASE_KEY': 'eyJhbGc...',
        'DATABASE_URL': 'postgresql://...',
        'SECRET_KEY': 'your-secret-key'
    }
    
    all_ok = True
    
    for var, example in required_vars.items():
        value = os.getenv(var)
        if value and value != example:
            # Mask sensitive values
            if 'KEY' in var or 'PASSWORD' in var:
                masked = value[:10] + '...' + value[-5:] if len(value) > 15 else '***'
                print_status(f"{var} = {masked}", 'OK')
            else:
                print_status(f"{var} = {value[:30]}...", 'OK')
        else:
            print_status(f"{var} not set or using placeholder", 'FAIL')
            print(f"   Set in .env file: {var}=your_actual_value")
            all_ok = False
    
    return all_ok

def test_supabase_connection():
    """Test Supabase connection"""
    try:
        from extensions import get_supabase_client
        client = get_supabase_client()
        
        # Try a simple query
        response = client.table('tenants').select('count', count='exact').execute()
        print_status(f"Supabase connection successful (found {len(response.data)} records)", 'OK')
        return True
    except ValueError as e:
        print_status(f"Supabase configuration error: {str(e)}", 'FAIL')
        return False
    except Exception as e:
        print_status(f"Supabase connection failed: {str(e)}", 'FAIL')
        print("   Check your SUPABASE_URL and SUPABASE_KEY in .env")
        return False

def test_database_schema():
    """Test if required tables exist"""
    try:
        from extensions import get_supabase_client
        client = get_supabase_client()
        
        required_tables = ['tenants', 'field_mappings', 'customers']
        all_ok = True
        
        for table in required_tables:
            try:
                response = client.table(table).select('count', count='exact').execute()
                print_status(f"Table '{table}' exists", 'OK')
            except Exception as e:
                print_status(f"Table '{table}' not found", 'FAIL')
                print(f"   Run the setup SQL in Supabase SQL Editor")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print_status(f"Cannot check database schema: {str(e)}", 'FAIL')
        return False

def test_sample_data():
    """Test if sample data exists"""
    try:
        from extensions import get_supabase_client
        client = get_supabase_client()
        
        # Check for sample tenant
        tenants = client.table('tenants').select('*').eq('tenant_code', 'firm_a').execute()
        if tenants.data:
            print_status("Sample tenant 'firm_a' exists", 'OK')
        else:
            print_status("Sample tenant 'firm_a' not found", 'WARN')
            print("   Run the INSERT statements from the setup guide")
        
        # Check for sample customers
        customers = client.table('customers').select('count', count='exact').execute()
        count = customers.count if hasattr(customers, 'count') else len(customers.data)
        if count > 0:
            print_status(f"Found {count} sample customers", 'OK')
            return True
        else:
            print_status("No sample customers found", 'WARN')
            print("   Insert sample data using the setup SQL")
            return False
    except Exception as e:
        print_status(f"Cannot check sample data: {str(e)}", 'WARN')
        return False

def test_flask_app():
    """Test if Flask app can be imported"""
    try:
        from app import create_app
        app = create_app()
        print_status("Flask app can be created", 'OK')
        
        # Check if blueprints are registered
        blueprints = list(app.blueprints.keys())
        if 'customers' in blueprints and 'tenants' in blueprints:
            print_status(f"Blueprints registered: {', '.join(blueprints)}", 'OK')
            return True
        else:
            print_status(f"Some blueprints missing: {', '.join(blueprints)}", 'WARN')
            return False
    except Exception as e:
        print_status(f"Cannot create Flask app: {str(e)}", 'FAIL')
        print(f"   Error details: {e}")
        return False

def main():
    """Run all verification checks"""
    print("\n" + "="*60)
    print("  TENANT FIELD MAPPING SYSTEM - SETUP VERIFICATION")
    print("="*60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_env),
        ("Required Packages", check_required_packages),
        ("Project Structure", check_project_structure),
        ("Environment Variables", check_env_variables),
        ("Supabase Connection", test_supabase_connection),
        ("Database Schema", test_database_schema),
        ("Sample Data", test_sample_data),
        ("Flask Application", test_flask_app)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        print("-" * 40)
        try:
            results[check_name] = check_func()
        except Exception as e:
            print_status(f"Check failed with error: {str(e)}", 'FAIL')
            results[check_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("  VERIFICATION SUMMARY")
    print("="*60 + "\n")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for check_name, result in results.items():
        status = 'PASS' if result else 'FAIL'
        symbol = '✓' if result else '✗'
        print(f"{symbol} {check_name}: {status}")
    
    print(f"\n{passed}/{total} checks passed")
    
    if passed == total:
        print_status("\n🎉 All checks passed! You're ready to start!", 'OK')
        print("\nNext steps:")
        print("  1. Run the app: python app.py")
        print("  2. Test the API: curl http://localhost:5000/health")
        print("  3. View customers: curl -H 'X-Tenant-Code: firm_a' http://localhost:5000/api/customers/")
        return 0
    else:
        print_status("\n⚠️  Some checks failed. Please fix the issues above.", 'WARN')
        print("\nCommon fixes:")
        print("  • Install packages: pip install -r requirements.txt")
        print("  • Configure .env: Copy values from Supabase dashboard")
        print("  • Run SQL setup: Execute SQL in Supabase SQL Editor")
        return 1

if __name__ == '__main__':
    sys.exit(main())