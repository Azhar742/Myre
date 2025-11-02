# Supabase PostgreSQL Setup Guide

This guide will help you migrate from SQLite to Supabase PostgreSQL for production use.

## Step 1: Create Supabase Account & Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up for a free account (no credit card required)
3. Click **"New Project"**
4. Fill in:
   - **Project Name**: `myre-database` (or your preferred name)
   - **Database Password**: Create a strong password (SAVE THIS!)
   - **Region**: Choose closest to your users
   - **Pricing Plan**: Free (500MB storage)
5. Click **"Create new project"** (takes ~2 minutes to provision)

## Step 2: Get Your Database Connection String

1. Once your project is ready, go to **Project Settings** (gear icon in sidebar)
2. Click **"Database"** in the left menu
3. Scroll down to **"Connection string"**
4. Select **"URI"** tab
5. Copy the connection string - it looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
   ```
6. Replace `[YOUR-PASSWORD]` with the password you created in Step 1

## Step 3: Install PostgreSQL Driver

Run this command in your terminal:

```bash
pip install psycopg2-binary
```

Or add to your requirements.txt:
```
psycopg2-binary==2.9.9
```

## Step 4: Update Environment Variables

Add your Supabase connection string to your `.env` file:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxxxxxxxxxx.supabase.co:5432/postgres

# Keep your existing variables
SECRET_KEY=your-secret-key-here
```

**IMPORTANT**: Never commit your `.env` file to git! Make sure it's in `.gitignore`

## Step 5: Update app.py Configuration

The database configuration in `app.py` has been updated to:
- Use `DATABASE_URL` from environment variables
- Fall back to SQLite for local development if not set
- Support both SQLite and PostgreSQL

## Step 6: Create Database Tables

Run this command to create all tables in your Supabase database:

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Tables created successfully!')"
```

## Step 7: Migrate Existing Data (Optional)

If you have existing data in SQLite that you want to migrate:

```bash
python migrate_to_postgres.py
```

This script will:
1. Read all data from your SQLite database
2. Insert it into your Supabase PostgreSQL database
3. Preserve all relationships and foreign keys

## Step 8: Test Your Connection

Start your Flask app:

```bash
python app.py
```

Check the console output - you should see:
```
Using database: postgresql://postgres:****@db.xxxxx.supabase.co:5432/postgres
```

## Step 9: Verify in Supabase Dashboard

1. Go to your Supabase project dashboard
2. Click **"Table Editor"** in the sidebar
3. You should see all your tables:
   - `user`
   - `account`
   - `organization`
   - `priority_condition`
   - `churn_condition`
   - `account_rule`
   - `custom_dashboard`

## Troubleshooting

### Connection Error
- **Check password**: Make sure you replaced `[YOUR-PASSWORD]` with your actual password
- **Check URL**: Verify the connection string is complete and correct
- **Firewall**: Supabase uses port 5432 - ensure it's not blocked

### SSL Error
If you get SSL errors, modify your connection string:
```
postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres?sslmode=require
```

### "relation does not exist" Error
Run `db.create_all()` to create tables:
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## Benefits You'll Get

✅ **Concurrent Access**: Multiple users can write simultaneously  
✅ **Better Performance**: Faster queries with proper indexing  
✅ **Data Integrity**: ACID compliance and foreign key constraints  
✅ **Scalability**: Grows with your application  
✅ **Backups**: Automatic daily backups (Supabase free tier)  
✅ **Cloud Access**: Access your database from anywhere  

## Development vs Production

You can use different databases for development and production:

**Development** (local):
```env
DATABASE_URL=sqlite:///mydatabase.db
```

**Production** (Supabase):
```env
DATABASE_URL=postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres
```

Just change the `DATABASE_URL` environment variable!

## Next Steps

1. Monitor your database usage in Supabase dashboard
2. Set up proper indexes for frequently queried fields
3. Consider upgrading to Pro plan ($25/month) when you exceed 500MB
4. Enable Row Level Security (RLS) in Supabase for additional security

## Need Help?

- Supabase Docs: https://supabase.com/docs
- PostgreSQL Docs: https://www.postgresql.org/docs/
- SQLAlchemy Docs: https://docs.sqlalchemy.org/

---

**Ready to migrate?** Follow the steps above and you'll be running on production-grade PostgreSQL in minutes!
