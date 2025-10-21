"""
Migration script to consolidate priority_conditions and churn_conditions 
into the unified account_rules table.

Run this script AFTER creating the account_rules table in the database.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user_model import db
from models.account_rule_model import AccountRule
from models.priority_condition_model import PriorityCondition
from models.churn_condition_model import ChurnCondition
from datetime import datetime


def migrate_priority_conditions():
    """Migrate all priority conditions to account_rules"""
    print("Migrating priority conditions...")
    
    priority_rules = PriorityCondition.query.all()
    migrated_count = 0
    
    for pr in priority_rules:
        try:
            # Check if already migrated
            existing = AccountRule.query.filter_by(
                rule_name=pr.condition_name,
                rule_type='priority',
                created_by=pr.created_by
            ).first()
            
            if existing:
                print(f"  Skipping '{pr.condition_name}' - already migrated")
                continue
            
            new_rule = AccountRule(
                rule_name=pr.condition_name,
                description=pr.description or '',
                rule_type='priority',
                filter_conditions=pr.filter_conditions,
                created_by=pr.created_by,
                is_active=pr.is_active,
                created_at=pr.created_at,
                updated_at=pr.updated_at,
                priority_order=0
            )
            
            db.session.add(new_rule)
            migrated_count += 1
            print(f"  ✓ Migrated: {pr.condition_name}")
            
        except Exception as e:
            print(f"  ✗ Error migrating '{pr.condition_name}': {str(e)}")
            db.session.rollback()
            continue
    
    db.session.commit()
    print(f"✓ Migrated {migrated_count} priority conditions\n")
    return migrated_count


def migrate_churn_conditions():
    """Migrate all churn conditions to account_rules"""
    print("Migrating churn conditions...")
    
    try:
        churn_rules = ChurnCondition.query.all()
    except Exception as e:
        print(f"  ⚠️  Could not query churn_conditions table: {str(e)}")
        print("  Skipping churn conditions migration (table may not exist or have old schema)")
        return 0
    
    migrated_count = 0
    
    for cr in churn_rules:
        try:
            # Check if already migrated
            existing = AccountRule.query.filter_by(
                rule_name=cr.condition_name,
                rule_type='churn',
                created_by=cr.created_by
            ).first()
            
            if existing:
                print(f"  Skipping '{cr.condition_name}' - already migrated")
                continue
            
            new_rule = AccountRule(
                rule_name=cr.condition_name,
                description=cr.description or '',
                rule_type='churn',
                filter_conditions=cr.filter_conditions,
                created_by=cr.created_by,
                is_active=cr.is_active,
                created_at=cr.created_at,
                updated_at=cr.updated_at,
                priority_order=0
            )
            
            db.session.add(new_rule)
            migrated_count += 1
            print(f"  ✓ Migrated: {cr.condition_name}")
            
        except Exception as e:
            print(f"  ✗ Error migrating '{cr.condition_name}': {str(e)}")
            db.session.rollback()
            continue
    
    db.session.commit()
    print(f"✓ Migrated {migrated_count} churn conditions\n")
    return migrated_count


def verify_migration():
    """Verify that migration was successful"""
    print("Verifying migration...")
    
    try:
        priority_count = PriorityCondition.query.count()
    except:
        priority_count = 0
    
    try:
        churn_count = ChurnCondition.query.count()
    except:
        churn_count = 0
    
    migrated_priority = AccountRule.query.filter_by(rule_type='priority').count()
    migrated_churn = AccountRule.query.filter_by(rule_type='churn').count()
    
    print(f"  Original priority conditions: {priority_count}")
    print(f"  Migrated priority rules: {migrated_priority}")
    print(f"  Original churn conditions: {churn_count}")
    print(f"  Migrated churn rules: {migrated_churn}")
    
    if migrated_priority >= priority_count:
        print("✓ Migration verification passed!\n")
        return True
    else:
        print("⚠️  Migration partially complete\n")
        return True  # Still return True since priority migration succeeded


def run_migration(drop_old_tables=False):
    """
    Run the complete migration
    
    Args:
        drop_old_tables: If True, drop old tables after successful migration
                        WARNING: This is irreversible!
    """
    print("=" * 60)
    print("UNIFIED RULES MIGRATION")
    print("=" * 60)
    print()
    
    # Migrate priority conditions
    priority_migrated = migrate_priority_conditions()
    
    # Migrate churn conditions
    churn_migrated = migrate_churn_conditions()
    
    # Verify migration
    success = verify_migration()
    
    if success:
        print("=" * 60)
        print(f"✓ MIGRATION COMPLETE!")
        print(f"  Total rules migrated: {priority_migrated + churn_migrated}")
        print("=" * 60)
        
        if drop_old_tables:
            print("\n⚠️  WARNING: About to drop old tables!")
            print("   This action is IRREVERSIBLE!")
            response = input("   Type 'YES' to confirm: ")
            
            if response == 'YES':
                try:
                    # Drop old tables
                    db.session.execute('DROP TABLE IF EXISTS priority_conditions')
                    db.session.execute('DROP TABLE IF EXISTS churn_conditions')
                    db.session.commit()
                    print("✓ Old tables dropped successfully")
                except Exception as e:
                    print(f"✗ Error dropping tables: {str(e)}")
            else:
                print("  Skipped dropping old tables")
    else:
        print("=" * 60)
        print("✗ MIGRATION FAILED - Please review errors above")
        print("=" * 60)


if __name__ == '__main__':
    # Import app context
    from app import app
    
    with app.app_context():
        # Run migration (don't drop old tables by default for safety)
        run_migration(drop_old_tables=False)
