#!/bin/bash

# Test script for Unified Rules API
# Make sure Flask app is running: python3 app.py

BASE_URL="http://localhost:5000"

echo "=========================================="
echo "UNIFIED RULES API TEST SUITE"
echo "=========================================="
echo ""

# Test 1: Get all priority rules for user 1
echo "1. GET all priority rules for user 1"
echo "   curl $BASE_URL/api/rules/priority?user_id=1"
curl -s "$BASE_URL/api/rules/priority?user_id=1" | python3 -m json.tool
echo ""
echo ""

# Test 2: Create a new priority rule
echo "2. POST - Create new priority rule"
echo "   curl -X POST $BASE_URL/api/rules"
curl -s -X POST "$BASE_URL/api/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "API Test Priority Rule",
    "description": "Testing unified API",
    "rule_type": "priority",
    "filter_conditions": {
      "account_status": {"operator": "==", "value": "active"}
    },
    "created_by": 1
  }' | python3 -m json.tool
echo ""
echo ""

# Test 3: Get all rules (all types) for user 1
echo "3. GET all rules (all types) for user 1"
echo "   curl $BASE_URL/api/rules/all?user_id=1"
curl -s "$BASE_URL/api/rules/all?user_id=1" | python3 -m json.tool
echo ""
echo ""

# Test 4: Get specific rule by ID (use ID from previous response)
echo "4. GET specific rule by ID (rule_id=1)"
echo "   curl $BASE_URL/api/rules/1"
curl -s "$BASE_URL/api/rules/1" | python3 -m json.tool
echo ""
echo ""

# Test 5: Get accounts matching a rule
echo "5. GET accounts matching rule_id=1"
echo "   curl $BASE_URL/api/rules/1/accounts?user_id=1"
curl -s "$BASE_URL/api/rules/1/accounts?user_id=1" | python3 -m json.tool
echo ""
echo ""

# Test 6: Create a churn rule
echo "6. POST - Create new churn rule"
echo "   curl -X POST $BASE_URL/api/rules"
curl -s -X POST "$BASE_URL/api/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "API Test Churn Rule",
    "description": "Inactive accounts",
    "rule_type": "churn",
    "filter_conditions": {
      "account_status": {"operator": "==", "value": "inactive"}
    },
    "created_by": 1
  }' | python3 -m json.tool
echo ""
echo ""

# Test 7: Get all churn rules
echo "7. GET all churn rules for user 1"
echo "   curl $BASE_URL/api/rules/churn?user_id=1"
curl -s "$BASE_URL/api/rules/churn?user_id=1" | python3 -m json.tool
echo ""
echo ""

# Test 8: Get all accounts matching user's rules
echo "8. GET all accounts matching ANY of user 1's rules"
echo "   curl $BASE_URL/api/users/1/rules/accounts"
curl -s "$BASE_URL/api/users/1/rules/accounts" | python3 -m json.tool
echo ""
echo ""

# Test 9: Update a rule
echo "9. PUT - Update rule_id=1"
echo "   curl -X PUT $BASE_URL/api/rules/1"
curl -s -X PUT "$BASE_URL/api/rules/1" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description via API",
    "user_id": 1
  }' | python3 -m json.tool
echo ""
echo ""

# Test 10: Delete a rule (commented out for safety)
# echo "10. DELETE - Delete rule_id=3"
# echo "   curl -X DELETE $BASE_URL/api/rules/3"
# curl -s -X DELETE "$BASE_URL/api/rules/3" \
#   -H "Content-Type: application/json" \
#   -d '{"user_id": 1}' | python3 -m json.tool
# echo ""
# echo ""

echo "=========================================="
echo "✓ TEST SUITE COMPLETE"
echo "=========================================="
