# Multi-Tenant Organization Architecture

## Overview

This document describes the multi-tenant organizational sign-up system implemented in Myre. The architecture allows multiple companies/organizations to sign up, with each organization having multiple employees with different roles and permissions.

## Architecture Design

### Entity Relationship Diagram

```
┌─────────────────┐
│  Organization   │
│  (Tenant)       │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴─────┬──────────────┐
    │          │              │
    ▼          ▼              ▼
┌───────┐  ┌───────┐    ┌──────────┐
│ User  │  │ User  │    │ Account  │
│(Admin)│  │ (CSM) │    │(Customer)│
└───────┘  └───────┘    └──────────┘
```

### Key Principles

1. **Multi-Tenancy**: Each organization is isolated with its own data
2. **Role-Based Access**: Users have roles (admin, CSM, manager, user)
3. **Subscription Plans**: Organizations have different plan limits
4. **Data Isolation**: Queries are scoped by `organization_id`

## Database Schema

### 1. Organization Model (`organizations` table)

**Purpose**: Central tenant entity representing a company/organization

**Key Fields**:
- `id`: Primary key
- `org_name`: Organization name
- `org_slug`: URL-friendly unique identifier
- `org_email`: Primary contact email
- `subscription_plan`: 'free', 'basic', 'pro', 'enterprise'
- `subscription_status`: 'active', 'suspended', 'cancelled'
- `max_users`: Maximum users allowed based on plan
- `max_accounts`: Maximum customer accounts allowed
- `org_status`: 'active', 'inactive', 'suspended'
- `deleted_at`: Soft delete timestamp

**Relationships**:
- One-to-Many with Users
- One-to-Many with Accounts (customer accounts)

### 2. User Model (`users` table)

**Purpose**: Represents employees/users within an organization

**Key Fields**:
- `id`: Primary key
- `user_name`: Full name
- `user_email`: Unique email address
- `user_password`: Hashed password (hash in production!)
- `user_role`: 'admin', 'csm', 'manager', 'user'
- `organization_id`: Foreign key to organizations table
- `is_org_admin`: Boolean flag for admin privileges
- `user_status`: 'active', 'inactive'
- `user_deleted_at`: Soft delete timestamp

**Relationships**:
- Many-to-One with Organization
- One-to-Many with Accounts (as CSM)

### 3. Account Model (`accounts` table)

**Purpose**: Represents customer accounts managed by the organization

**Key Fields**:
- `id`: Primary key
- `account_name`: Customer account name
- `organization_id`: Foreign key to organizations table
- `csm_user_id`: User managing this account
- `account_status`: 'active', 'inactive'

**Relationships**:
- Many-to-One with Organization
- Many-to-One with User (CSM)

## Subscription Plans

| Plan       | Max Users  | Max Accounts | Price/Month |
|------------|------------|--------------|-------------|
| Free       | Unlimited* | Unlimited*   | $0          |
| Basic      | Unlimited* | Unlimited*   | $29         |
| Pro        | Unlimited* | Unlimited*   | $99         |
| Enterprise | Unlimited* | Unlimited*   | Custom      |

**Note**: User and account limits are optional and not enforced by default. The `max_users` and `max_accounts` fields in the Organization model are nullable. You can set custom limits per organization if needed.

## API Endpoints

### Organization Management

#### Create Organization (Sign Up)
```
POST /organization/signup
Content-Type: application/json

{
  "organization": {
    "org_name": "Acme Corporation",
    "org_email": "contact@acme.com",
    "org_phone": "+1-555-1234",
    "org_website": "https://acme.com",
    "org_industry": "technology",
    "org_size": "51-200",
    "subscription_plan": "basic"
  },
  "admin": {
    "user_name": "John Doe",
    "user_email": "john@acme.com",
    "user_password": "securepassword123",
    "user_role": "admin"
  }
}

Response: 201 Created
{
  "message": "Organization created successfully",
  "organization": { ... },
  "admin_user": { ... }
}
```

#### Get Organization
```
GET /organization/{org_id}

Response: 200 OK
{
  "id": 1,
  "org_name": "Acme Corporation",
  "org_slug": "acme-corporation",
  ...
}
```

#### Update Organization
```
PUT /organization/{org_id}
Content-Type: application/json

{
  "org_name": "Updated Name",
  "subscription_plan": "pro"
}

Response: 200 OK
```

#### Delete Organization (Soft Delete)
```
DELETE /organization/{org_id}

Response: 200 OK
```

#### Get Organization Stats
```
GET /organization/{org_id}/stats

Response: 200 OK
{
  "organization": { ... },
  "active_users": 5,
  "max_users": null,  // null = unlimited
  "users_remaining": null,  // null = unlimited
  "active_accounts": 50,
  "max_accounts": null,  // null = unlimited
  "accounts_remaining": null  // null = unlimited
}
```

### User Management

#### Get Organization Users
```
GET /organization/{org_id}/users

Response: 200 OK
{
  "organization_id": 1,
  "total_users": 5,
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@acme.com",
      "role": "admin",
      "is_org_admin": true,
      "status": "active"
    },
    ...
  ]
}
```

#### Add User to Organization
```
POST /organization/{org_id}/users
Content-Type: application/json

{
  "user_name": "Jane Smith",
  "user_email": "jane@acme.com",
  "user_password": "temppassword123",
  "user_role": "csm",
  "is_org_admin": false
}

Response: 201 Created
{
  "message": "User added successfully",
  "user": { ... }
}
```

## Frontend Pages

### 1. Organization Sign Up (`/organization/signup`)
- **File**: `views/html/org_signup.html`
- **Features**:
  - 3-step wizard (Organization → Admin → Plan)
  - Beautiful gradient design
  - Plan selection with pricing
  - Form validation
  - Success/error modals

### 2. Add Employee (`/organization/add_employee?org_id={id}`)
- **File**: `views/html/add_employee.html`
- **Features**:
  - Add new team members
  - Role selection
  - Admin privilege toggle
  - Real-time organization limits display
  - Prevents adding users beyond plan limits

## Data Isolation Strategy

### Query Filtering
All queries for accounts and users should be filtered by `organization_id`:

```python
# Get accounts for an organization
accounts = Account.query.filter_by(
    organization_id=org_id,
    account_status='active'
).all()

# Get users in an organization
users = User.query.filter_by(
    organization_id=org_id,
    user_deleted_at=None
).all()
```

### Middleware (Future Enhancement)
Consider adding middleware to automatically inject `organization_id` filters:

```python
@app.before_request
def inject_organization_context():
    # Get organization from session/token
    # Add to request context
    pass
```

## Security Considerations

### 1. Password Hashing
**IMPORTANT**: Currently passwords are stored in plain text. In production:

```python
from werkzeug.security import generate_password_hash, check_password_hash

# When creating user
user.user_password = generate_password_hash(password)

# When authenticating
if check_password_hash(user.user_password, provided_password):
    # Login successful
```

### 2. Authentication & Authorization
Implement JWT or session-based authentication:
- Verify user belongs to organization
- Check user role/permissions
- Validate organization is active

### 3. Data Access Control
- Users can only access data within their organization
- Admins can manage users in their organization
- CSMs can only manage assigned accounts

## Usage Examples

### Example 1: Organization Sign Up Flow

1. User visits `/organization/signup`
2. Fills out 3-step form:
   - Step 1: Organization details
   - Step 2: Admin account
   - Step 3: Plan selection
3. Submits form → POST to `/organization/signup`
4. Backend creates:
   - Organization record
   - Admin user record (linked to organization)
5. User redirected to dashboard

### Example 2: Adding Team Members

1. Admin logs in
2. Navigates to `/organization/add_employee?org_id=1`
3. Page loads organization stats (users remaining)
4. Admin fills employee details
5. Submits → POST to `/organization/1/users`
6. Backend validates:
   - Organization exists and is active
   - Not at user limit
   - Email is unique
7. Creates new user linked to organization

### Example 3: Data Isolation

```python
# CSM user (id=5) in organization (id=1) views their accounts
user = User.query.get(5)
org_id = user.organization_id  # 1

# Only get accounts for this organization
accounts = Account.query.filter_by(
    organization_id=org_id,
    csm_user_id=user.id
).all()

# This ensures CSM only sees accounts in their organization
```

## Migration Guide

### Migrating Existing Data

If you have existing users and accounts, migrate them to organizations:

```python
# Create a default organization for existing data
default_org = Organization(
    org_name="Default Organization",
    org_slug="default",
    org_email="admin@company.com",
    subscription_plan="enterprise",
    max_users=999,
    max_accounts=99999
)
db.session.add(default_org)
db.session.flush()

# Update existing users
User.query.update({User.organization_id: default_org.id})

# Update existing accounts
Account.query.update({Account.organization_id: default_org.id})

db.session.commit()
```

## Future Enhancements

1. **Email Invitations**: Send email invites instead of creating passwords
2. **SSO Integration**: Support SAML/OAuth for enterprise customers
3. **Role Permissions**: Fine-grained permission system
4. **Audit Logs**: Track all organization changes
5. **Billing Integration**: Stripe/payment gateway integration
6. **Organization Settings**: Custom branding, timezone, etc.
7. **User Groups**: Organize users into teams/departments
8. **API Keys**: Allow programmatic access per organization
9. **Webhooks**: Event notifications for integrations
10. **Multi-factor Authentication**: Enhanced security

## Testing

### Test Organization Creation
```bash
curl -X POST http://localhost:5000/organization/signup \
  -H "Content-Type: application/json" \
  -d '{
    "organization": {
      "org_name": "Test Corp",
      "org_email": "test@test.com",
      "subscription_plan": "free"
    },
    "admin": {
      "user_name": "Test Admin",
      "user_email": "admin@test.com",
      "user_password": "password123"
    }
  }'
```

### Test Adding User
```bash
curl -X POST http://localhost:5000/organization/1/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "New Employee",
    "user_email": "employee@test.com",
    "user_password": "password123",
    "user_role": "csm"
  }'
```

## Troubleshooting

### Issue: Foreign Key Constraint Error
**Solution**: Ensure Organization model is imported before creating tables:
```python
from models.organization_model import Organization
db.create_all()
```

### Issue: Users Not Isolated
**Solution**: Always filter by `organization_id` in queries:
```python
users = User.query.filter_by(organization_id=org_id).all()
```

### Issue: Can't Add More Users
**Solution**: Check organization plan limits (only applies if limits are set):
```python
org = Organization.query.get(org_id)
if org.can_add_user():
    # Add user (returns True if max_users is None or limit not reached)
else:
    # Show upgrade message (only if max_users is set and reached)
```

### Setting Custom Limits
If you want to enforce limits for specific organizations:
```python
# Set limits for an organization
org = Organization.query.get(org_id)
org.max_users = 50
org.max_accounts = 1000
db.session.commit()

# Remove limits (set to unlimited)
org.max_users = None
org.max_accounts = None
db.session.commit()
```

## Support

For questions or issues with the organization architecture, please contact the development team or refer to the main project documentation.
