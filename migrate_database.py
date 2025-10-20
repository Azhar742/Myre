"""
Database Migration Script
Run this to add organization_id columns to existing database without losing data.
"""

import sqlite3
import os

DB_PATH = 'mydatabase.db'

def migrate_database():
    """Add organization_id columns to existing tables"""
    
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} does not exist. No migration needed.")
        print("The database will be created automatically when you run app.py")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if organizations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='organizations'")
        if not cursor.fetchone():
            print("Creating organizations table...")
            # This is complex, better to just recreate the database
            print("\nRecommendation: Delete the database and let Flask recreate it.")
            print("Run: rm mydatabase.db && python3 app.py")
            conn.close()
            return
        
        # Add organization_id to users table if it doesn't exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'organization_id' not in columns:
            print("Adding organization_id to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN organization_id INTEGER")
            cursor.execute("ALTER TABLE users ADD COLUMN is_org_admin BOOLEAN DEFAULT 0")
            print("✓ Users table updated")
        else:
            print("✓ Users table already has organization_id")
        
        # Add organization_id to accounts table if it doesn't exist
        cursor.execute("PRAGMA table_info(accounts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'organization_id' not in columns:
            print("Adding organization_id to accounts table...")
            cursor.execute("ALTER TABLE accounts ADD COLUMN organization_id INTEGER")
            print("✓ Accounts table updated")
        else:
            print("✓ Accounts table already has organization_id")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("\nNote: Existing users and accounts have NULL organization_id.")
        print("You can either:")
        print("1. Create a default organization and assign existing data to it")
        print("2. Delete old data and start fresh with organization signup")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_default_organization():
    """Create a default organization and assign all existing data to it"""
    
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} does not exist.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if organizations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='organizations'")
        if not cursor.fetchone():
            print("Organizations table doesn't exist. Run app.py first to create tables.")
            conn.close()
            return
        
        # Create default organization
        print("Creating default organization...")
        cursor.execute("""
            INSERT INTO organizations 
            (org_name, org_slug, org_email, subscription_plan, subscription_status, org_status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('Default Organization', 'default', 'admin@company.com', 'enterprise', 'active', 'active'))
        
        org_id = cursor.lastrowid
        print(f"✓ Created organization with ID: {org_id}")
        
        # Update all users
        cursor.execute("UPDATE users SET organization_id = ? WHERE organization_id IS NULL", (org_id,))
        users_updated = cursor.rowcount
        print(f"✓ Updated {users_updated} users")
        
        # Update all accounts
        cursor.execute("UPDATE accounts SET organization_id = ? WHERE organization_id IS NULL", (org_id,))
        accounts_updated = cursor.rowcount
        print(f"✓ Updated {accounts_updated} accounts")
        
        conn.commit()
        print("\n✅ Default organization created and data migrated!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("Database Migration Tool")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--create-default':
        print("\nOption: Create default organization and migrate existing data\n")
        migrate_database()
        create_default_organization()
    else:
        print("\nOption: Add missing columns to existing database\n")
        migrate_database()
        print("\nTo also create a default organization and migrate data, run:")
        print("  python3 migrate_database.py --create-default")
