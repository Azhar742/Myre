# Unified Rules API - Testing Guide

## 🚀 Quick Start

### Step 1: Start the Flask App
```bash
cd /Users/mafraah/Library/CloudStorage/OneDrive-athenahealth/Desktop/Targets/Myre
python3 app.py
```

The app will start on `http://localhost:5000`

### Step 2: Run the Test Script
Open a new terminal:
```bash
cd /Users/mafraah/Library/CloudStorage/OneDrive-athenahealth/Desktop/Targets/Myre
chmod +x test_unified_api.sh
./test_unified_api.sh
```

---

## 📋 API Endpoints

### 1. **Create a Rule**
```bash
POST /api/rules
```

**Request Body:**
```json
{
  "rule_name": "High Value Clients",
  "description": "Clients with revenue > $1000",
  "rule_type": "priority",
  "filter_conditions": {
    "last_paid_bill_amount": {"operator": ">", "value": "1000"}
  },
  "created_by": 1
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/rules \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "Test Rule",
    "rule_type": "priority",
    "filter_conditions": {"account_status": {"operator": "==", "value": "active"}},
    "created_by": 1
  }'
```

---

### 2. **Get Rules by Type**
```bash
GET /api/rules/{rule_type}?user_id={user_id}
```

**Rule Types:** `priority`, `churn`, `upsell`, `custom`, `all`

**Examples:**
```bash
# Get all priority rules
curl "http://localhost:5000/api/rules/priority?user_id=1"

# Get all churn rules
curl "http://localhost:5000/api/rules/churn?user_id=1"

# Get ALL rules
curl "http://localhost:5000/api/rules/all?user_id=1"
```

---

### 3. **Get Specific Rule**
```bash
GET /api/rules/{rule_id}
```

**Example:**
```bash
curl http://localhost:5000/api/rules/1
```

---

### 4. **Update a Rule**
```bash
PUT /api/rules/{rule_id}
```

**Request Body:**
```json
{
  "user_id": 1,
  "description": "Updated description",
  "is_active": true
}
```

**Example:**
```bash
curl -X PUT http://localhost:5000/api/rules/1 \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "description": "Updated via API"}'
```

---

### 5. **Delete a Rule**
```bash
DELETE /api/rules/{rule_id}
```

**Request Body:**
```json
{
  "user_id": 1
}
```

**Example:**
```bash
curl -X DELETE http://localhost:5000/api/rules/3 \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

---

### 6. **Get Accounts Matching a Rule**
```bash
GET /api/rules/{rule_id}/accounts?user_id={user_id}
```

**Example:**
```bash
curl "http://localhost:5000/api/rules/1/accounts?user_id=1"
```

---

### 7. **Get All Accounts Matching User's Rules**
```bash
GET /api/users/{user_id}/rules/accounts?rule_type={type}
```

**Examples:**
```bash
# Get all accounts matching ANY priority rule
curl "http://localhost:5000/api/users/1/rules/accounts?rule_type=priority"

# Get all accounts matching ANY rule (all types)
curl "http://localhost:5000/api/users/1/rules/accounts"
```

---

## 🧪 Manual Testing Steps

### Test 1: Create Priority Rule
```bash
curl -X POST http://localhost:5000/api/rules \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "Active Accounts",
    "description": "All active accounts",
    "rule_type": "priority",
    "filter_conditions": {
      "account_status": {"operator": "==", "value": "active"}
    },
    "created_by": 1
  }'
```

**Expected Response:**
```json
{
  "id": 3,
  "rule_name": "Active Accounts",
  "rule_type": "priority",
  "filter_conditions": {
    "account_status": {"operator": "==", "value": "active"}
  },
  "created_by": 1,
  ...
}
```

### Test 2: Get All Rules
```bash
curl "http://localhost:5000/api/rules/all?user_id=1"
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "rule_name": "Basic Plan",
    "rule_type": "priority",
    ...
  },
  {
    "id": 2,
    "rule_name": "Active Clients",
    "rule_type": "priority",
    ...
  },
  {
    "id": 3,
    "rule_name": "Active Accounts",
    "rule_type": "priority",
    ...
  }
]
```

### Test 3: Get Matching Accounts
```bash
curl "http://localhost:5000/api/rules/3/accounts?user_id=1"
```

**Expected Response:**
```json
{
  "rule_id": 3,
  "total_accounts": 5,
  "accounts": [
    {
      "id": 1,
      "account_name": "Acme Corp",
      "account_status": "active",
      ...
    },
    ...
  ]
}
```

### Test 4: Create Churn Rule
```bash
curl -X POST http://localhost:5000/api/rules \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "Inactive Accounts",
    "description": "Accounts at risk",
    "rule_type": "churn",
    "filter_conditions": {
      "account_status": {"operator": "==", "value": "inactive"}
    },
    "created_by": 1
  }'
```

### Test 5: Update Rule
```bash
curl -X PUT http://localhost:5000/api/rules/3 \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "description": "Updated: All active accounts",
    "is_active": true
  }'
```

### Test 6: Get All Accounts (OR Logic)
```bash
curl "http://localhost:5000/api/users/1/rules/accounts"
```

This returns ALL accounts that match ANY of user 1's rules.

---

## 🎯 Expected Results

After running all tests, you should see:

✅ **Rules Created:** 3+ rules (2 migrated + new ones)
✅ **Rules Retrieved:** All rules returned correctly
✅ **Accounts Filtered:** Correct accounts returned based on filters
✅ **Updates Work:** Rule descriptions/settings updated
✅ **Multiple Types:** Both priority and churn rules working

---

## 🐛 Troubleshooting

### Error: "Module not found"
```bash
# Make sure you're in the right directory
cd /Users/mafraah/Library/CloudStorage/OneDrive-athenahealth/Desktop/Targets/Myre
python3 app.py
```

### Error: "Rule not found"
```bash
# Check what rules exist
curl "http://localhost:5000/api/rules/all?user_id=1"
```

### Error: "user_id is required"
```bash
# Make sure to include user_id in query params or body
curl "http://localhost:5000/api/rules/priority?user_id=1"
```

### No accounts returned
```bash
# Check if accounts exist for user 1
sqlite3 mydatabase.db "SELECT COUNT(*) FROM accounts WHERE csm_user_id=1;"
```

---

## 📊 Success Criteria

- ✅ Can create rules of different types (priority, churn)
- ✅ Can retrieve rules by type
- ✅ Can get accounts matching a rule
- ✅ Can update rule properties
- ✅ Can delete rules
- ✅ Filters work correctly (case-insensitive, operators)
- ✅ OR logic works (multiple rules combine accounts)

---

## 🎉 Next Steps

Once all tests pass:
1. Update frontend to use new unified API
2. Add custom dashboards
3. Implement caching (Redis)
4. Add rule templates
5. Build analytics dashboard
