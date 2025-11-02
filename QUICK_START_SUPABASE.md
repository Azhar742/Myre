# Quick Start: Supabase Setup (5 Minutes)

## 🚀 Fast Track Setup

### 1. Install PostgreSQL Driver
```bash
pip install psycopg2-binary
```

### 2. Get Supabase Connection String
1. Go to [supabase.com](https://supabase.com) → Sign up (free)
2. Create new project → Save your password!
3. Go to Settings → Database → Copy "URI" connection string
4. Replace `[YOUR-PASSWORD]` with your actual password

### 3. Add to Your .env File
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

### 4. Create Tables in Supabase
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Tables created!')"
```

### 5. (Optional) Migrate Existing Data
```bash
python migrate_to_postgres.py
```

### 6. Run Your App
```bash
python app.py
```

You should see: `Using database: db.xxxxx.supabase.co:5432/postgres`

## ✅ That's It!

Your app is now running on production-grade PostgreSQL!

## 🔄 Switch Between Databases

**Use SQLite (local dev):**
- Remove or comment out `DATABASE_URL` in `.env`

**Use PostgreSQL (production):**
- Add `DATABASE_URL` to `.env`

## 📚 Full Documentation

See `SUPABASE_SETUP_GUIDE.md` for detailed instructions and troubleshooting.

## 🆘 Common Issues

**"No module named psycopg2"**
```bash
pip install psycopg2-binary
```

**"Could not connect to server"**
- Check your password in DATABASE_URL
- Verify connection string is complete

**"relation does not exist"**
- Run `db.create_all()` to create tables (see step 4 above)
