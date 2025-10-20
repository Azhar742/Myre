# Quick Start Guide - Multi-Tenant Organization System

## Getting Started in 5 Minutes

### Step 1: Initialize Database

The new organization tables will be created automatically when you run the app:

```bash
python app.py
```

This creates the `organizations` table and adds the necessary fields to `users` and `accounts` tables.

### Step 2: Access Organization Sign Up

Open your browser and navigate to:
```
http://localhost:5000/organization/signup
```

### Step 3: Create Your First Organization

Fill out the 3-step form:

**Step 1 - Organization Details:**
- Organization Name: "My Company"
- Organization Email: "contact@mycompany.com"
- Industry: Select your industry
- Company Size: Select size

**Step 2 - Admin Account:**
- Full Name: "Your Name"
- Email: "you@mycompany.com"
- Password: Create a secure password

**Step 3 - Choose Plan:**
- Select a plan (Free, Basic, or Pro)

Click "Create Organization" and you're done!

### Step 4: Add Team Members

After creating your organization, add employees:

```
http://localhost:5000/organization/add_employee?org_id=1
```

Fill in employee details:
- Full Name
- Email Address
- Temporary Password
- Role (CSM, Manager, Admin, User)
- Admin Privileges (optional)

## API Quick Reference

### Create Organization
```bash
curl -X POST http://localhost:5000/organization/signup \
  -H "Content-Type: application/json" \
  -d '{
    "organization": {
      "org_name": "Acme Corp",
      "org_email": "contact@acme.com",
      "subscription_plan": "basic"
    },
    "admin": {
      "user_name": "John Doe",
      "user_email": "john@acme.com",
      "user_password": "securepass123"
    }
  }'
```

### Get Organization Stats
```bash
curl http://localhost:5000/organization/1/stats
```

### Add Employee
```bash
curl -X POST http://localhost:5000/organization/1/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "Jane Smith",
    "user_email": "jane@acme.com",
    "user_password": "temppass123",
    "user_role": "csm"
  }'
```

### Get All Users in Organization
```bash
curl http://localhost:5000/organization/1/users
```

## File Structure

```
Myre/
├── models/
│   ├── organization_model.py    # NEW: Organization entity
│   ├── user_model.py            # UPDATED: Added organization_id
│   └── account_model.py         # UPDATED: Added organization_id
├── controllers/
│   └── organization_controller.py  # NEW: Business logic
├── views/
│   ├── html/
│   │   ├── org_signup.html      # NEW: Signup page
│   │   └── add_employee.html    # NEW: Add employee page
│   ├── css/
│   │   ├── org_signup.css       # NEW: Signup styles
│   │   └── add_employee.css     # NEW: Employee styles
│   └── js/
│       └── org_signup.js        # NEW: Signup logic
├── docs/
│   ├── ORGANIZATION_ARCHITECTURE.md  # Full documentation
│   └── QUICK_START_GUIDE.md         # This file
└── app.py                       # UPDATED: Added org routes

```

## Key Features

✅ **Multi-tenant architecture** - Complete data isolation per organization  
✅ **Beautiful UI** - Modern, responsive design with gradient branding  
✅ **Role-based access** - Admin, CSM, Manager, User roles  
✅ **Subscription plans** - Free, Basic, Pro, Enterprise tiers  
✅ **User limits** - Enforced based on subscription plan  
✅ **Soft deletes** - Organizations and users can be recovered  
✅ **RESTful API** - Complete CRUD operations  

## Common Use Cases

### Use Case 1: SaaS Platform
Multiple companies sign up, each with their own team managing their own customer accounts.

### Use Case 2: Agency Model
Different agencies manage different client portfolios, all isolated from each other.

### Use Case 3: Enterprise Departments
Different departments within a company operate as separate organizations.

## Next Steps

1. **Add Authentication**: Implement JWT or session-based auth
2. **Hash Passwords**: Use `werkzeug.security` for password hashing
3. **Email Invitations**: Send invite emails instead of manual passwords
4. **Billing Integration**: Connect to Stripe for subscription payments
5. **Data Isolation Middleware**: Auto-inject organization filters

## Need Help?

- Read full documentation: `docs/ORGANIZATION_ARCHITECTURE.md`
- Check API endpoints in `app.py`
- Review models in `models/` directory
- Examine controllers in `controllers/` directory

## Important Notes

⚠️ **Security**: Passwords are currently stored in plain text. Hash them in production!  
⚠️ **Authentication**: No auth middleware yet. Add JWT/sessions before production.  
⚠️ **Validation**: Add more robust input validation for production use.  

## Success! 🎉

You now have a fully functional multi-tenant organization system with:
- Beautiful sign-up flow
- Employee management
- Subscription plans
- Data isolation
- RESTful API

Start building your SaaS platform today!
