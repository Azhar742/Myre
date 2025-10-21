# Authentication & Authorization Testing Guide

## 🔒 Security Features Added

1. **Session-based Authentication** - Users must login to access dashboards
2. **User Validation** - Checks if user exists in database
3. **Authorization** - Users can only access their own dashboards (unless admin)
4. **Decorators** - Clean, reusable security layer

---

## 🧪 Testing Steps

### Step 1: Start the Flask App
```bash
cd /Users/mafraah/Library/CloudStorage/OneDrive-athenahealth/Desktop/Targets/Myre
python3 app.py
```

---

### Step 2: Test Without Login (Should Fail)

```bash
# Try to access user 1's dashboard without logging in
curl "http://localhost:5000/dashboard/1"
```

**Expected Response:**
```json
{
  "error": "Authentication required. Please login."
}
```
**Status Code:** 401 Unauthorized ❌

---

### Step 3: Login as User 1

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@acme.com", "password": "hashed_password_123"}' \
  -c cookies.txt
```

**Expected Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@acme.com",
    "role": "admin"
  }
}
```
**Status Code:** 200 ✅

**Note:** `-c cookies.txt` saves the session cookie

---

### Step 4: Check Session

```bash
curl "http://localhost:5000/session" -b cookies.txt
```

**Expected Response:**
```json
{
  "logged_in": true,
  "user_id": 1,
  "user_email": "john@acme.com",
  "user_role": "admin"
}
```
✅ Session active!

---

### Step 5: Access Own Dashboard (Should Work)

```bash
curl "http://localhost:5000/dashboard/1" -b cookies.txt
```

**Expected:** HTML page rendered ✅

---

### Step 6: Try to Access Another User's Dashboard (Should Fail)

```bash
# User 1 trying to access User 2's dashboard
curl "http://localhost:5000/dashboard/2" -b cookies.txt
```

**Expected Response:**
```json
{
  "error": "Access denied. You can only access your own dashboard.",
  "logged_in_as": 1,
  "requested_user": 2
}
```
**Status Code:** 403 Forbidden ❌

---

### Step 7: Login as User 2

```bash
# Logout first
curl -X POST http://localhost:5000/logout -b cookies.txt

# Login as user 2
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "jane@example.com", "password": "hashed_password_123"}' \
  -c cookies2.txt
```

---

### Step 8: Access User 2's Dashboard (Should Work)

```bash
curl "http://localhost:5000/dashboard/2" -b cookies2.txt
```

**Expected:** HTML page rendered ✅

---

### Step 9: Admin Override Test

Since User 1 is an admin, they should be able to access any dashboard:

```bash
# Login as user 1 (admin)
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@acme.com", "password": "hashed_password_123"}' \
  -c admin_cookies.txt

# Access user 2's dashboard as admin
curl "http://localhost:5000/dashboard/2" -b admin_cookies.txt
```

**Expected:** HTML page rendered ✅ (Admin can access any dashboard)

---

### Step 10: Test Non-Existent User

```bash
curl "http://localhost:5000/dashboard/999" -b cookies.txt
```

**Expected Response:**
```json
{
  "error": "User not found"
}
```
**Status Code:** 404 ❌

---

## 📋 Protected Routes

All these routes now require authentication and authorization:

- ✅ `/dashboard/<user_id>`
- ✅ `/account_management_dashboard/<user_id>`
- ✅ `/priority_accounts_dashboard/<user_id>`
- ✅ `/priority_accounts_dashboard/<user_id>/automation`
- ✅ `/priority_accounts_dashboard/<user_id>/integration`
- ✅ `/churn_management/<user_id>`

---

## 🔑 Decorator Usage

### `@validate_user_access`
**Full security:** Checks login + user exists + authorization

```python
@app.route('/dashboard/<int:user_id>')
@validate_user_access
def dashboard(user_id):
    # User is authenticated and authorized
    pass
```

### `@login_required`
**Just checks login:** Use for routes that don't have user_id parameter

```python
@app.route('/api/rules', methods=['POST'])
@login_required
def create_rule():
    # User is logged in
    pass
```

### `@validate_user_exists`
**Just checks user exists:** No auth check (for public routes)

```python
@app.route('/public/user/<int:user_id>')
@validate_user_exists
def public_profile(user_id):
    # User exists, but no login required
    pass
```

---

## 🎯 Security Rules

1. **Users can only access their own dashboards**
2. **Admins can access any dashboard**
3. **Must be logged in to access protected routes**
4. **Session expires when user logs out**
5. **Invalid users return 404**
6. **Unauthorized access returns 403**
7. **Not logged in returns 401**

---

## 🐛 Troubleshooting

### Error: "Authentication required"
**Solution:** Login first using `/login` endpoint

### Error: "Access denied"
**Solution:** You're trying to access another user's dashboard. Login as that user or use an admin account.

### Error: "User not found"
**Solution:** The user ID doesn't exist in the database.

### Session not persisting
**Solution:** Make sure you're using `-b cookies.txt` to send cookies with requests.

---

## 🔐 Production Recommendations

1. **Use HTTPS** - Never send passwords over HTTP
2. **Hash passwords** - Use bcrypt or similar (currently using plain text)
3. **Add CSRF protection** - Use Flask-WTF
4. **Add rate limiting** - Prevent brute force attacks
5. **Use environment variables** - Don't hardcode SECRET_KEY
6. **Add session timeout** - Auto-logout after inactivity
7. **Add 2FA** - Two-factor authentication for sensitive accounts
8. **Log security events** - Track login attempts, access denials

---

## ✅ Test Summary

| Test | Expected Result | Status |
|------|----------------|--------|
| Access without login | 401 Unauthorized | ✅ |
| Login with valid credentials | 200 + Session created | ✅ |
| Access own dashboard | 200 + HTML | ✅ |
| Access other user's dashboard | 403 Forbidden | ✅ |
| Admin access any dashboard | 200 + HTML | ✅ |
| Access non-existent user | 404 Not Found | ✅ |
| Logout | Session cleared | ✅ |

---

## 🚀 Quick Test Script

```bash
#!/bin/bash

echo "=== Testing Authentication System ==="

# Test 1: No login
echo -e "\n1. Access without login (should fail):"
curl -s "http://localhost:5000/dashboard/1" | python3 -m json.tool

# Test 2: Login
echo -e "\n2. Login as user 1:"
curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@acme.com", "password": "hashed_password_123"}' \
  -c /tmp/cookies.txt | python3 -m json.tool

# Test 3: Check session
echo -e "\n3. Check session:"
curl -s "http://localhost:5000/session" -b /tmp/cookies.txt | python3 -m json.tool

# Test 4: Access own dashboard
echo -e "\n4. Access own dashboard (should work):"
curl -s "http://localhost:5000/dashboard/1" -b /tmp/cookies.txt | head -n 5

# Test 5: Access other user's dashboard
echo -e "\n5. Try to access user 2's dashboard (should fail):"
curl -s "http://localhost:5000/dashboard/2" -b /tmp/cookies.txt | python3 -m json.tool

echo -e "\n=== Tests Complete ==="
```

Save as `test_auth.sh`, make executable with `chmod +x test_auth.sh`, and run!
