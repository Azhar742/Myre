const userLogsData = [
    { time: '2 min ago', message: 'Sarah Johnson logged in', meta: 'IP: 192.168.1.45', status: 'success' },
    { time: '5 min ago', message: 'Mike Davis updated profile', meta: 'Changes: Email, Phone', status: 'info' },
    { time: '8 min ago', message: 'Emily Chen created new contact', meta: 'Contact ID: #C1247', status: 'success' },
    { time: '12 min ago', message: 'Failed login attempt', meta: 'User: admin@company.com', status: 'error' },
    { time: '15 min ago', message: 'Alex Martinez logged out', meta: 'Session: 2h 34m', status: 'info' },
    { time: '18 min ago', message: 'Lisa Brown exported report', meta: 'Report: Q4-2024-Sales', status: 'success' },
    { time: '22 min ago', message: 'John Smith deleted record', meta: 'Record ID: #R8923', status: 'warning' },
    { time: '25 min ago', message: 'Kate Wilson logged in', meta: 'IP: 192.168.1.67', status: 'success' }
];

const systemLogsData = [
    { time: '1 min ago', message: 'Database backup completed', meta: 'Size: 2.4 GB', status: 'success' },
    { time: '10 min ago', message: 'API rate limit warning', meta: 'Endpoint: /api/users', status: 'warning' },
    { time: '15 min ago', message: 'SSL certificate renewed', meta: 'Valid until: Oct 2026', status: 'success' },
    { time: '20 min ago', message: 'Cache cleared successfully', meta: 'Type: Redis', status: 'info' },
    { time: '30 min ago', message: 'System update available', meta: 'Version: 2.4.1', status: 'info' },
    { time: '35 min ago', message: 'High CPU usage detected', meta: 'Usage: 87%', status: 'error' },
    { time: '40 min ago', message: 'Cron job executed', meta: 'Task: email_digest', status: 'success' },
    { time: '45 min ago', message: 'Server restart completed', meta: 'Downtime: 12s', status: 'success' }
];

const transactionLogsData = [
    { time: '3 min ago', message: 'Payment processed', meta: 'Amount: $1,245.00 • Order #3421', status: 'success' },
    { time: '7 min ago', message: 'Refund initiated', meta: 'Amount: $89.99 • Order #3418', status: 'warning' },
    { time: '11 min ago', message: 'Invoice generated', meta: 'Invoice #INV-2024-1142', status: 'info' },
    { time: '14 min ago', message: 'Payment failed', meta: 'Reason: Insufficient funds', status: 'error' },
    { time: '19 min ago', message: 'Subscription renewed', meta: 'Plan: Premium • $49.99/mo', status: 'success' },
    { time: '24 min ago', message: 'Chargeback received', meta: 'Amount: $120.00 • Order #3401', status: 'error' },
    { time: '28 min ago', message: 'Payment processed', meta: 'Amount: $3,567.50 • Order #3420', status: 'success' },
    { time: '32 min ago', message: 'Tax calculated', meta: 'Amount: $145.20 • Order #3419', status: 'info' }
];

// Store registered users
let registeredUsers = [
    { email: 'demo@crm.com', password: 'demo123', firstName: 'Demo', lastName: 'User' }
];

function renderLogs(containerId, data) {
    const container = document.getElementById(containerId);
    container.innerHTML = data.map(log => `
        <div class="log-item">
            <div class="log-time">${log.time}</div>
            <div class="log-message">${log.message} <span class="status ${log.status}">${log.status}</span></div>
            <div class="log-meta">${log.meta}</div>
        </div>
    `).join('');
}

function refreshLogs(type) {
    const btn = event.currentTarget;
    btn.style.transform = 'rotate(360deg)';
    btn.style.transition = 'transform 0.5s';
    setTimeout(() => {
        btn.style.transform = 'rotate(0deg)';
    }, 500);
    
    if (type === 'user') {
        renderLogs('userLogs', userLogsData);
    } else if (type === 'system') {
        renderLogs('systemLogs', systemLogsData);
    } else if (type === 'transaction') {
        renderLogs('transactionLogs', transactionLogsData);
    }
}

function showSignup(event) {
    event.preventDefault();
    document.getElementById('loginPage').classList.add('hidden');
    document.getElementById('signupPage').classList.remove('hidden');
}

function showLogin(event) {
    event.preventDefault();
    document.getElementById('signupPage').classList.add('hidden');
    document.getElementById('loginPage').classList.remove('hidden');
}

function handleSignup(event) {
    event.preventDefault();
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    // Validate passwords match
    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }

    // Check if user already exists
    const userExists = registeredUsers.find(u => u.email === email);
    if (userExists) {
        alert('An account with this email already exists!');
        return;
    }

    // Register new user
    registeredUsers.push({
        email: email,
        password: password,
        firstName: firstName,
        lastName: lastName
    });

    alert('Account created successfully! Please sign in.');
    
    // Reset form and show login page
    document.getElementById('signupForm').reset();
    showLogin(event);
}

function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    // Validate credentials
    const user = registeredUsers.find(u => u.email === email && u.password === password);
    
    if (!user) {
        alert('Invalid email or password!');
        return;
    }

    // Hide login page, show dashboard
    document.getElementById('loginPage').classList.add('hidden');
    document.getElementById('dashboardPage').classList.add('show');
    
    // Update user info in navbar
    document.getElementById('userEmail').textContent = user.email;
    
    // Update avatar with initials
    const initials = user.firstName.charAt(0) + user.lastName.charAt(0);
    document.getElementById('userAvatar').textContent = initials.toUpperCase();
    
    // Initialize dashboard
    renderLogs('userLogs', userLogsData);
    renderLogs('systemLogs', systemLogsData);
    renderLogs('transactionLogs', transactionLogsData);
}

function handleLogout() {
    // Hide dashboard, show login page
    document.getElementById('dashboardPage').classList.remove('show');
    document.getElementById('loginPage').classList.remove('hidden');
    
    // Reset form
    document.getElementById('loginForm').reset();
}

function toggleThemeMenu() {
    const menu = document.getElementById('themeMenu');
    menu.classList.toggle('show');
}

function changeTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    toggleThemeMenu();
}

// Close theme menu when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.querySelector('.theme-dropdown');
    const menu = document.getElementById('themeMenu');
    if (dropdown && !dropdown.contains(event.target)) {
        menu.classList.remove('show');
    }
});
