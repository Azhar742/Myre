# Cleanup Plan - Unused Files & Code

## 🗑️ Files to Remove

### Root Directory:
1. ✅ `csm_bare_code.html` - Unused bare HTML file
2. ✅ `test_app.py` - Empty test file (0 bytes)
3. ✅ `test_script.py` - Old test script (replaced by test_unified_api.sh)
4. ✅ `migrate_database.py` - Old migration (replaced by migrations/migrate_to_unified_rules.py)
5. ✅ `create_unified_tables.py` - One-time use script (already executed)

### Views Directory:
6. ✅ `views/html/csm_dashboard_simple.html` - No longer used (redirects to dashboard)

### Controllers:
7. ⚠️ Keep `priority_condition_controller.py` - Still used by legacy routes
8. ⚠️ Keep `churn_condition_controller.py` - Still used by legacy routes
9. ✅ Eventually migrate to use only `rule_controller.py`

### Models:
10. ⚠️ Keep `priority_condition_model.py` - Still has data in DB
11. ⚠️ Keep `churn_condition_model.py` - Still has data in DB
12. ✅ Eventually migrate to use only `account_rule_model.py`

---

## 📝 Code to Clean Up in app.py

### Duplicate/Legacy Routes:
1. `/priority_condition/<account_id>` (POST) - Legacy endpoint, consider removing
2. Consider consolidating all rule creation to unified API

### Unused Imports:
- Check for any unused controller imports

---

## ✅ Safe to Delete Now

These files are definitely safe to remove:

```bash
rm csm_bare_code.html
rm test_app.py
rm test_script.py
rm migrate_database.py
rm create_unified_tables.py
rm views/html/csm_dashboard_simple.html
```

---

## ⚠️ Keep for Now (Backward Compatibility)

These are still referenced and should be kept:
- `priority_condition_controller.py`
- `churn_condition_controller.py`
- `priority_condition_model.py`
- `churn_condition_model.py`

---

## 🔄 Future Migration Plan

### Phase 1: (Current)
- ✅ Unified models created
- ✅ Unified controller created
- ✅ Unified API routes added
- ⚠️ Legacy routes still active

### Phase 2: (Next)
- Update frontend to use unified API
- Deprecate legacy endpoints
- Add deprecation warnings

### Phase 3: (Future)
- Remove legacy controllers
- Remove legacy models
- Drop old database tables
- Clean up all legacy code

---

## 📊 File Size Analysis

**Before Cleanup:**
- Total files: ~50
- Unused files: 6
- Code duplication: High

**After Cleanup:**
- Total files: ~44
- Unused files: 0
- Code duplication: Medium (legacy support)

---

## 🎯 Recommended Action

**Safe Immediate Cleanup:**
```bash
cd /Users/mafraah/Library/CloudStorage/OneDrive-athenahealth/Desktop/Targets/Myre

# Remove unused files
rm csm_bare_code.html
rm test_app.py
rm test_script.py
rm migrate_database.py
rm create_unified_tables.py
rm views/html/csm_dashboard_simple.html

# Commit changes
git add -A
git commit -m "cleanup: remove unused files and scripts"
```

This removes 6 files that are definitely not being used anymore.
