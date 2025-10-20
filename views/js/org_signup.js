// Current step tracking
let currentStep = 1;

// Step navigation
function nextStep(step) {
    if (validateStep(currentStep)) {
        // Update step indicator
        document.querySelector(`.step[data-step="${currentStep}"]`).classList.add('completed');
        document.querySelector(`.step[data-step="${currentStep}"]`).classList.remove('active');
        document.querySelector(`.step[data-step="${step}"]`).classList.add('active');
        
        // Update form steps
        document.getElementById(`step${currentStep}`).classList.remove('active');
        document.getElementById(`step${step}`).classList.add('active');
        
        currentStep = step;
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function prevStep(step) {
    // Update step indicator
    document.querySelector(`.step[data-step="${currentStep}"]`).classList.remove('active');
    document.querySelector(`.step[data-step="${step}"]`).classList.remove('completed');
    document.querySelector(`.step[data-step="${step}"]`).classList.add('active');
    
    // Update form steps
    document.getElementById(`step${currentStep}`).classList.remove('active');
    document.getElementById(`step${step}`).classList.add('active');
    
    currentStep = step;
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Validation
function validateStep(step) {
    if (step === 1) {
        const orgName = document.getElementById('orgName').value.trim();
        const orgEmail = document.getElementById('orgEmail').value.trim();
        
        if (!orgName) {
            showError('Please enter organization name');
            return false;
        }
        
        if (!orgEmail || !isValidEmail(orgEmail)) {
            showError('Please enter a valid organization email');
            return false;
        }
        
        return true;
    }
    
    if (step === 2) {
        const adminName = document.getElementById('adminName').value.trim();
        const adminEmail = document.getElementById('adminEmail').value.trim();
        const adminPassword = document.getElementById('adminPassword').value;
        const adminPasswordConfirm = document.getElementById('adminPasswordConfirm').value;
        
        if (!adminName) {
            showError('Please enter your full name');
            return false;
        }
        
        if (!adminEmail || !isValidEmail(adminEmail)) {
            showError('Please enter a valid email address');
            return false;
        }
        
        if (!adminPassword || adminPassword.length < 8) {
            showError('Password must be at least 8 characters long');
            return false;
        }
        
        if (adminPassword !== adminPasswordConfirm) {
            showError('Passwords do not match');
            return false;
        }
        
        return true;
    }
    
    return true;
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Password strength indicator
document.getElementById('adminPassword')?.addEventListener('input', function(e) {
    const password = e.target.value;
    const strengthIndicator = document.getElementById('passwordStrength');
    
    if (password.length === 0) {
        strengthIndicator.className = 'password-strength';
    } else if (password.length < 8) {
        strengthIndicator.className = 'password-strength weak';
    } else if (password.length < 12 || !/[A-Z]/.test(password) || !/[0-9]/.test(password)) {
        strengthIndicator.className = 'password-strength medium';
    } else {
        strengthIndicator.className = 'password-strength strong';
    }
});

// Plan selection
function selectPlan(plan) {
    // Remove selected class from all cards
    document.querySelectorAll('.plan-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Add selected class to chosen card
    document.querySelector(`.plan-card[data-plan="${plan}"]`).classList.add('selected');
    
    // Update hidden input
    document.getElementById('selectedPlan').value = plan;
}

// Form submission
document.getElementById('orgSignupForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!validateStep(currentStep)) {
        return;
    }
    
    // Disable submit button
    const submitBtn = document.querySelector('.btn-submit');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating...';
    
    // Gather form data
    const formData = {
        organization: {
            org_name: document.getElementById('orgName').value.trim(),
            org_email: document.getElementById('orgEmail').value.trim(),
            org_phone: document.getElementById('orgPhone').value.trim() || null,
            org_website: document.getElementById('orgWebsite').value.trim() || null,
            org_industry: document.getElementById('orgIndustry').value || null,
            org_size: document.getElementById('orgSize').value || null,
            subscription_plan: document.getElementById('selectedPlan').value
        },
        admin: {
            user_name: document.getElementById('adminName').value.trim(),
            user_email: document.getElementById('adminEmail').value.trim(),
            user_password: document.getElementById('adminPassword').value,
            user_role: 'admin'
        }
    };
    
    try {
        const response = await fetch('/organization/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Show success modal
            showSuccessModal();
            
            // Redirect to dashboard after 2 seconds
            setTimeout(() => {
                window.location.href = `/csm_dashboard/${data.admin_user.id}`;
            }, 2000);
        } else {
            throw new Error(data.error || 'Failed to create organization');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorModal(error.message);
        
        // Re-enable submit button
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
});

// Modal functions
function showSuccessModal() {
    document.getElementById('successModal').classList.add('show');
}

function showErrorModal(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorModal').classList.add('show');
}

function closeErrorModal() {
    document.getElementById('errorModal').classList.remove('show');
}

function showError(message) {
    alert(message); // Simple alert for now, can be enhanced with better UI
}

// Initialize - select free plan by default
document.addEventListener('DOMContentLoaded', function() {
    selectPlan('free');
});
