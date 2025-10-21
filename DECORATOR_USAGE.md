# Security Decorators - Usage Reference

## 📋 All Decorators

### 1. `@validate_user_access`
**Purpose:** Full security - validates login + user exists + authorization
**Use case:** Dashboard routes where user can only access their own data

### 2. `@login_required`
**Purpose:** Just checks if user is logged in
**Use case:** API routes that need authentication but don't have user_id in URL

### 3. `@validate_user_exists`
**Purpose:** Just checks if user exists (no auth)
**Use case:** Public/semi-public routes (currently unused)

---

## 🔒 Routes Protected with `@validate_user_access`

These routes require login AND users can only access their own data (unless admin):

1. `/dashboard/<user_id>` - Main dashboard
2. `/account_management_dashboard/<user_id>` - Account management page
3. `/priority_accounts_dashboard/<user_id>` - Priority accounts dashboard
4. `/priority_accounts_dashboard/<user_id>/automation` - Automation view
5. `/priority_accounts_dashboard/<user_id>/integration` - Integration view
6. `/churn_management/<user_id>` - Churn management dashboard

**Security:** 
- ✅ Must be logged in
- ✅ User must exist
- ✅ Can only access own dashboard (unless admin)

---

## 🔐 Routes Protected with `@login_required`

These routes require login but don't restrict by user_id:

### Unified Rules API:
1. `POST /api/rules` - Create rule
2. `PUT /api/rules/<rule_id>` - Update rule
3. `DELETE /api/rules/<rule_id>` - Delete rule

### Priority Conditions API:
4. `POST /priority_conditions` - Create priority condition
5. `DELETE /priority_conditions/<condition_id>` - Delete priority condition

### Churn Conditions API:
6. `POST /churn_conditions` - Create churn condition
7. `DELETE /churn_conditions/<condition_id>` - Delete churn condition

**Security:**
- ✅ Must be logged in
- ⚠️ Additional authorization checks done in controller logic

---

## 🌐 Unprotected Routes (Public)

These routes don't require authentication:

- `GET /` - Landing page
- `POST /login` - Login endpoint
- `POST /signup` - Signup endpoint
- `GET /logout` - Logout endpoint
- `GET /session` - Check session status
- `GET /api/rules/<rule_type>` - Get rules (should be protected!)
- `GET /api/rules/<rule_id>` - Get specific rule (should be protected!)
- `GET /api/rules/<rule_id>/accounts` - Get accounts (should be protected!)
- `GET /api/users/<user_id>/rules/accounts` - Get user's accounts (should be protected!)

**⚠️ Security Gap:** Some GET endpoints should probably be protected!

---

## 🎯 Recommended Improvements

### Add `@login_required` to these GET endpoints:

```python
@app.route('/api/rules/<rule_type>', methods=['GET'])
@login_required  # ADD THIS
def get_rules_by_type_route(rule_type):
    ...

@app.route('/api/rules/<int:rule_id>', methods=['GET'])
@login_required  # ADD THIS
def get_rule_route(rule_id):
    ...

@app.route('/api/rules/<int:rule_id>/accounts', methods=['GET'])
@login_required  # ADD THIS
def get_rule_accounts_route(rule_id):
    ...

@app.route('/api/users/<int:user_id>/rules/accounts', methods=['GET'])
@validate_user_access  # ADD THIS (since it has user_id)
def get_user_rules_accounts_route(user_id):
    ...
```

---

## 📊 Current Security Coverage

| Route Type | Total | Protected | Unprotected |
|------------|-------|-----------|-------------|
| **Dashboards** | 6 | 6 ✅ | 0 |
| **Write APIs** | 7 | 7 ✅ | 0 |
| **Read APIs** | 4 | 0 ⚠️ | 4 |
| **Auth Routes** | 4 | 0 (intentional) | 4 |
| **Total** | 21 | 13 (62%) | 8 (38%) |

---

## 🔍 How to Check Decorator Usage

### Find all routes with `@validate_user_access`:
```bash
grep -n "@validate_user_access" app.py
```

### Find all routes with `@login_required`:
```bash
grep -n "@login_required" app.py
```

### Find all routes with `@validate_user_exists`:
```bash
grep -n "@validate_user_exists" app.py
```

### Find all unprotected routes:
```bash
grep -B1 "def.*_route\|def.*_dashboard\|def.*_view" app.py | grep -v "@"
```

---

## ✅ Quick Reference

**When to use each decorator:**

| Scenario | Decorator |
|----------|-----------|
| Dashboard with `<user_id>` in URL | `@validate_user_access` |
| API endpoint that modifies data | `@login_required` |
| API endpoint that reads sensitive data | `@login_required` |
| Public endpoint (login, signup) | None |
| Check if user exists (no auth) | `@validate_user_exists` |

---

## 🚀 Next Steps

1. ✅ Add `@login_required` to GET API endpoints
2. ✅ Consider adding rate limiting
3. ✅ Add CSRF protection for forms
4. ✅ Implement proper password hashing
5. ✅ Add session timeout
6. ✅ Add audit logging for security events
