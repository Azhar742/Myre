const sidebar = document.getElementById('sidebar');
const hamburger = document.getElementById('hamburger');

// Toggle sidebar on mobile
hamburger?.addEventListener('click', () => sidebar.classList.toggle('open'));

// Close sidebar when clicking outside on mobile
document.addEventListener('click', e => {
  if (window.matchMedia('(max-width:800px)').matches) {
    if (!sidebar.contains(e.target) && !hamburger.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  }
});

// Account table columns
const accountColumns = [
  { value: 'account_name', label: 'Account Name' },
  { value: 'account_status', label: 'Account Status' },
  { value: 'plan_name', label: 'Plan Name' },
  { value: 'client_email', label: 'Client Email' },
  { value: 'client_phn', label: 'Client Phone' },
  { value: 'last_paid_bill_amount', label: 'Last Paid Bill Amount' },
  { value: 'company_name', label: 'Company Name' },
  { value: 'domain', label: 'Domain' }
];

// Operators for different data types
const operators = [
  { value: '==', label: 'Equal to' },
  { value: '!=', label: 'Not equal to' },
  { value: '>', label: 'Greater than' },
  { value: '<', label: 'Less than' },
  { value: '>=', label: 'Greater than or equal to' },
  { value: '<=', label: 'Less than or equal to' },
  { value: 'contains', label: 'Contains' },
  { value: 'not_contains', label: 'Does not contain' },
  { value: 'in', label: 'In' },
  { value: 'not_in', label: 'Not in' },
  { value: 'is_empty', label: 'Is empty' },
  { value: 'is_not_empty', label: 'Is not empty' },
  { value: 'exists', label: 'Exists' },
  { value: 'not_exists', label: 'Does not exist' }
];

let conditionCounter = 0;

// Modal functions
function openCreateRuleModal() {
  const modal = document.getElementById('createRuleModal');
  if (modal) {
    modal.style.display = 'flex';
    // Add initial condition
    if (document.getElementById('conditionsContainer').children.length === 0) {
      addCondition();
    }
  }
}

function closeCreateRuleModal() {
  const modal = document.getElementById('createRuleModal');
  if (modal) {
    modal.style.display = 'none';
    document.getElementById('createRuleForm').reset();
    document.getElementById('conditionsContainer').innerHTML = '';
    conditionCounter = 0;
    editingRuleId = null;
    
    // Reset modal title and button text
    document.querySelector('#createRuleModal h3').textContent = 'Create New Priority Rule';
    document.querySelector('#createRuleForm button[type="submit"]').textContent = 'Create Rule';
    
    // Hide status toggle and delete button (only shown when editing)
    document.getElementById('ruleStatusToggle').style.display = 'none';
    document.getElementById('deleteRuleBtn').style.display = 'none';
  }
}

// Delete current rule from modal
function deleteCurrentRule() {
  if (editingRuleId) {
    deleteRule(editingRuleId);
    closeCreateRuleModal();
  }
}

// Add a new condition row (only one allowed)
function addCondition() {
  const container = document.getElementById('conditionsContainer');
  
  // Only allow one condition - clear any existing
  container.innerHTML = '';
  
  const conditionId = conditionCounter++;
  
  const conditionRow = document.createElement('div');
  conditionRow.id = `condition-${conditionId}`;
  conditionRow.style.cssText = 'display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;padding:12px;background:#f8f9fa;border-radius:6px;align-items:start;';
  
  conditionRow.innerHTML = `
    <div>
      <select class="condition-field" data-id="${conditionId}" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:4px;font-size:13px;">
        <option value="">Select Field</option>
        ${accountColumns.map(col => `<option value="${col.value}">${col.label}</option>`).join('')}
      </select>
    </div>
    
    <div>
      <select class="condition-operator" data-id="${conditionId}" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:4px;font-size:13px;">
        <option value="">Select Operator</option>
        ${operators.map(op => `<option value="${op.value}">${op.label}</option>`).join('')}
      </select>
    </div>
    
    <div>
      <input type="text" class="condition-value" data-id="${conditionId}" placeholder="Value" style="width:100%;padding:8px;border:1px solid #dee2e6;border-radius:4px;font-size:13px;">
      <small style="color:var(--muted);font-size:11px;display:block;margin-top:4px;">Leave empty for 'is empty' or 'exists' operators</small>
    </div>
  `;
  
  container.appendChild(conditionRow);
  
  // Add event listener to hide/show value input based on operator
  const operatorSelect = conditionRow.querySelector('.condition-operator');
  const valueInput = conditionRow.querySelector('.condition-value');
  
  operatorSelect.addEventListener('change', (e) => {
    const noValueOperators = ['is_empty', 'is_not_empty', 'exists', 'not_exists'];
    if (noValueOperators.includes(e.target.value)) {
      valueInput.disabled = true;
      valueInput.style.background = '#e9ecef';
      valueInput.value = '';
    } else {
      valueInput.disabled = false;
      valueInput.style.background = 'white';
    }
  });
}

// Remove a condition row
function removeCondition(conditionId) {
  const conditionRow = document.getElementById(`condition-${conditionId}`);
  if (conditionRow) {
    conditionRow.remove();
  }
}

// Build filter conditions object from form
function buildFilterConditions() {
  const conditions = {};
  const container = document.getElementById('conditionsContainer');
  const conditionRows = container.querySelectorAll('[id^="condition-"]');
  
  conditionRows.forEach(row => {
    const field = row.querySelector('.condition-field').value;
    const operator = row.querySelector('.condition-operator').value;
    const value = row.querySelector('.condition-value').value;
    
    if (field && operator) {
      const noValueOperators = ['is_empty', 'is_not_empty', 'exists', 'not_exists'];
      
      if (noValueOperators.includes(operator)) {
        conditions[field] = { operator: operator };
      } else if (value) {
        // Try to parse as number if it looks like a number
        const parsedValue = !isNaN(value) && value !== '' ? parseFloat(value) : value;
        conditions[field] = { operator: operator, value: parsedValue };
      }
    }
  });
  
  return conditions;
}

// Handle create/update rule form submission
async function handleCreateRule(event) {
  event.preventDefault();
  
  // Get user_id from URL path instead of localStorage
  const pathParts = window.location.pathname.split('/');
  const userId = parseInt(pathParts[pathParts.length - 1]);
  
  if (!userId || isNaN(userId)) {
    alert('Could not determine user ID');
    return;
  }
  
  const ruleName = document.getElementById('ruleName').value;
  const ruleDescription = document.getElementById('ruleDescription').value;
  const filterConditions = buildFilterConditions();
  
  // Validate that at least one condition is added
  if (Object.keys(filterConditions).length === 0) {
    alert('Please add at least one filter condition');
    return;
  }
  
  try {
    let response;
    
    if (editingRuleId) {
      // Update existing rule
      const isActive = document.getElementById('ruleIsActive').checked;
      
      response = await fetch(`/priority_condition/${editingRuleId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          condition_name: ruleName,
          description: ruleDescription,
          filter_conditions: filterConditions,
          is_active: isActive
        })
      });
    } else {
      // Create new rule (always active by default)
      response = await fetch('/priority_condition', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          condition_name: ruleName,
          description: ruleDescription,
          filter_conditions: filterConditions,
          created_by: userId
        })
      });
    }
    
    const data = await response.json();
    
    if (!response.ok) {
      alert(data.error || `Failed to ${editingRuleId ? 'update' : 'create'} rule`);
      return;
    }
    
    alert(`Priority rule ${editingRuleId ? 'updated' : 'created'} successfully!`);
    closeCreateRuleModal();
    
    // Reload rules table
    loadPriorityRules();
    
  } catch (error) {
    console.error('Error saving rule:', error);
    alert('An error occurred while saving the rule');
  }
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
  const modal = document.getElementById('createRuleModal');
  if (modal && e.target === modal) {
    closeCreateRuleModal();
  }
});

// Load priority rules on page load
document.addEventListener('DOMContentLoaded', () => {
  loadPriorityRules();
});

// Load and display priority rules as boxes
async function loadPriorityRules() {
  const container = document.getElementById('rulesContainer');
  if (!container) return;
  
  // Get user_id from URL path (e.g., /priority_accounts_dashboard/21)
  const pathParts = window.location.pathname.split('/');
  const userId = parseInt(pathParts[pathParts.length - 1]);
  
  if (!userId || isNaN(userId)) {
    console.error('Could not determine user ID from URL');
    return;
  }
  
  try {
    const showInactive = document.getElementById('showInactiveRules').checked;
    
    // Fetch all rules to filter client-side
    const response = await fetch('/priority_conditions_all');
    const data = await response.json();
    
    console.log('All conditions:', data.conditions);
    console.log('Current user ID from URL:', userId);
    
    // Filter rules by user and active status
    let rules = data.conditions.filter(r => r.created_by === userId);
    
    console.log('Filtered rules for user:', rules);
    
    if (!showInactive) {
      rules = rules.filter(r => r.is_active === true || r.is_active === 1);
      console.log('Active rules only:', rules);
    }
    
    if (rules.length === 0) {
      container.innerHTML = '<p style="color:var(--muted);text-align:center;padding:20px;width:100%;">No priority rules found. Click "Create New Rule" to get started.</p>';
      return;
    }
    
    // Build rule boxes
    let boxesHTML = '';
    
    rules.forEach(rule => {
      // Different styling for active vs inactive (handle both boolean and integer)
      const isActive = rule.is_active === true || rule.is_active === 1;
      const boxStyle = isActive
        ? 'background:white;border:2px solid #28a745;color:#212529;'
        : 'background:#f8f9fa;border:2px solid #dc3545;color:#6c757d;opacity:0.7;';
      
      // Format filter conditions for display
      let conditionsText = '';
      if (rule.filter_conditions && typeof rule.filter_conditions === 'object') {
        // filter_conditions is a dictionary: { "field_name": {"operator": "==", "value": "active"} }
        const conditions = Object.entries(rule.filter_conditions).map(([field, condition]) => 
          `${field} ${condition.operator} ${condition.value}`
        );
        conditionsText = conditions.join(' AND ');
      }
      
      boxesHTML += `
        <div class="rule-box-item" onclick="editRule(${rule.id})" 
             style="${boxStyle}padding:12px 16px;border-radius:8px;cursor:pointer;transition:all 0.2s;box-shadow:0 2px 4px rgba(0,0,0,0.1);min-width:200px;max-width:280px;flex:1 1 200px;position:relative;" 
             onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 4px 8px rgba(0,0,0,0.15)';this.querySelector('.delete-x').style.opacity='1';"
             onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)';this.querySelector('.delete-x').style.opacity='0';">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:14px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding-right:8px;">${rule.condition_name}</span>
            <button class="delete-x" onclick="event.stopPropagation();deleteRule(${rule.id})" 
                    style="opacity:0;transition:opacity 0.2s;background:transparent;border:none;color:#dc3545;font-size:18px;font-weight:bold;cursor:pointer;padding:0;width:24px;height:24px;display:flex;align-items:center;justify-content:center;border-radius:4px;"
                    onmouseover="this.style.background='#dc3545';this.style.color='white';"
                    onmouseout="this.style.background='transparent';this.style.color='#dc3545';">
              ×
            </button>
          </div>
          ${conditionsText ? `<div style="font-size:12px;color:#6c757d;margin-top:4px;font-family:monospace;">${conditionsText}</div>` : ''}
        </div>
      `;
    });
    
    container.innerHTML = boxesHTML;
    
  } catch (error) {
    console.error('Error loading rules:', error);
    container.innerHTML = '<p style="color:#dc3545;text-align:center;padding:20px;width:100%;">Error loading rules</p>';
  }
}

// Edit rule - populate modal with existing data
let editingRuleId = null;

async function editRule(ruleId) {
  try {
    const response = await fetch('/priority_conditions_all');
    const data = await response.json();
    const rule = data.conditions.find(r => r.id === ruleId);
    
    if (!rule) {
      alert('Rule not found');
      return;
    }
    
    // Set editing mode
    editingRuleId = ruleId;
    
    // Populate form
    document.getElementById('ruleName').value = rule.condition_name;
    document.getElementById('ruleDescription').value = rule.description || '';
    
    // Show and set active status toggle
    document.getElementById('ruleStatusToggle').style.display = 'block';
    document.getElementById('ruleIsActive').checked = rule.is_active;
    
    // Clear existing conditions
    document.getElementById('conditionsContainer').innerHTML = '';
    conditionCounter = 0;
    
    // Add conditions from rule
    Object.entries(rule.filter_conditions || {}).forEach(([field, condition]) => {
      addCondition();
      const lastCondition = document.getElementById('conditionsContainer').lastElementChild;
      lastCondition.querySelector('.condition-field').value = field;
      lastCondition.querySelector('.condition-operator').value = condition.operator;
      if (condition.value !== undefined) {
        lastCondition.querySelector('.condition-value').value = condition.value;
      }
    });
    
    // Change modal title and button text
    document.querySelector('#createRuleModal h3').textContent = 'Edit Priority Rule';
    document.querySelector('#createRuleForm button[type="submit"]').textContent = 'Update Rule';
    
    // Show delete button in modal
    document.getElementById('deleteRuleBtn').style.display = 'block';
    
    // Open modal
    openCreateRuleModal();
    
  } catch (error) {
    console.error('Error loading rule:', error);
    alert('Error loading rule data');
  }
}

// Delete rule
async function deleteRule(ruleId) {
  if (!confirm('Are you sure you want to delete this rule?')) {
    return;
  }
  
  try {
    const response = await fetch(`/priority_condition/${ruleId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      alert('Failed to delete rule');
      return;
    }
    
    alert('Rule deleted successfully!');
    loadPriorityRules();
    
  } catch (error) {
    console.error('Error deleting rule:', error);
    alert('Error deleting rule');
  }
}
