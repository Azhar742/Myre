"""
Migration script to transfer data from SQLite to PostgreSQL (Supabase)

This script will:
1. Read all data from your SQLite database
2. Connect to your PostgreSQL database (Supabase)
3. Transfer all records while preserving relationships
4. Verify the migration was successful

Usage:
    python migrate_to_postgres.py
"""

import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Import your models
from models.user_model import User, db
from models.account_model import Account
from models.organization_model import Organization
from models.priority_condition_model import PriorityCondition
from models.churn_condition_model import ChurnCondition
from models.account_rule_model import AccountRule
from models.custom_dashboard_model import CustomDashboard


def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    
    # Get PostgreSQL connection string from environment
    postgres_url = os.environ.get('DATABASE_URL')
    
    if not postgres_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("Please add your Supabase connection string to .env file:")
        print("DATABASE_URL=postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres")
        sys.exit(1)
    
    # SQLite database path
    basedir = os.path.abspath(os.path.dirname(__file__))
    sqlite_url = f'sqlite:///{os.path.join(basedir, "mydatabase.db")}'
    
    print("🔄 Starting migration from SQLite to PostgreSQL...")
    print(f"📁 Source: {sqlite_url}")
    print(f"🌐 Target: {postgres_url.split('@')[1] if '@' in postgres_url else 'PostgreSQL'}\n")
    
    # Create engines
    sqlite_engine = create_engine(sqlite_url)
    postgres_engine = create_engine(postgres_url)
    
    # Create sessions
    SqliteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)
    
    sqlite_session = SqliteSession()
    postgres_session = PostgresSession()
    
    try:
        # Check if SQLite database exists and has data
        inspector = inspect(sqlite_engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("⚠️  No tables found in SQLite database. Nothing to migrate.")
            return
        
        print(f"📊 Found {len(tables)} tables in SQLite database\n")
        
        # Migration order (respects foreign key dependencies)
        migration_order = [
            ('user', User),
            ('organization', Organization),
            ('account', Account),
            ('priority_condition', PriorityCondition),
            ('churn_condition', ChurnCondition),
            ('account_rule', AccountRule),
            ('custom_dashboard', CustomDashboard),
        ]
        
        total_records = 0
        
        for table_name, model in migration_order:
            # Check if table exists in SQLite
            if table_name not in tables:
                print(f"⏭️  Skipping {table_name} (not found in SQLite)")
                continue
            
            # Get all records from SQLite
            records = sqlite_session.query(model).all()
            
            if not records:
                print(f"⏭️  Skipping {table_name} (no data)")
                continue
            
            print(f"📦 Migrating {len(records)} records from '{table_name}'...")
            
            # Add records to PostgreSQL
            for record in records:
                # Create a dictionary of the record's attributes
                record_dict = {
                    column.name: getattr(record, column.name)
                    for column in record.__table__.columns
                }
                
                # Create new instance for PostgreSQL
                new_record = model(**record_dict)
                postgres_session.add(new_record)
            
            # Commit after each table
            postgres_session.commit()
            print(f"✅ Successfully migrated {len(records)} records from '{table_name}'\n")
            total_records += len(records)
        
        print(f"🎉 Migration completed successfully!")
        print(f"📊 Total records migrated: {total_records}\n")
        
        # Verify migration
        print("🔍 Verifying migration...")
        for table_name, model in migration_order:
            if table_name not in tables:
                continue
            
            sqlite_count = sqlite_session.query(model).count()
            postgres_count = postgres_session.query(model).count()
            
            if sqlite_count == postgres_count:
                print(f"✅ {table_name}: {postgres_count} records (verified)")
            else:
                print(f"⚠️  {table_name}: SQLite={sqlite_count}, PostgreSQL={postgres_count} (mismatch!)")
        
        print("\n✨ Migration complete! Your data is now in Supabase PostgreSQL.")
        print("💡 You can now update your .env to use DATABASE_URL for production.")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        postgres_session.rollback()
        raise
    
    finally:
        sqlite_session.close()
        postgres_session.close()


if __name__ == '__main__':
    print("=" * 70)
    print("  SQLite → PostgreSQL Migration Tool")
    print("=" * 70)
    print()
    
    # Confirm before proceeding
    response = input("⚠️  This will copy all data from SQLite to PostgreSQL. Continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        migrate_data()
    else:
        print("❌ Migration cancelled.")
        sys.exit(0)
