from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from functools import wraps
import os

# Initialize Flask app first
app = Flask(__name__, template_folder='views', static_folder='views', static_url_path='/static')
# Use absolute path to ensure database is in project root
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "mydatabase.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Import db and initialize it
from models.user_model import db, User
db.init_app(app)

# Import ALL models before db.create_all()
from models.account_model import Account
from models.priority_condition_model import PriorityCondition
from models.churn_condition_model import ChurnCondition
from models.organization_model import Organization

# Import utilities and controllers
from utils.utils import serialize_account
from controllers.user_controller import (
    create_user_service,
    get_user_service,
    update_user_service,
    delete_user_service
)
from controllers.account_controller import (
    create_account_service,
    get_account_service,
    update_account_service,
)
from controllers.priority_condition_controller import (
    get_account_filter_conditions,
    create_priority_condition_service,
    get_priority_accounts_service,
    get_accounts_by_user_priority_conditions_service,
    delete_priority_condition_service
)
from controllers.churn_condition_controller import (
    create_churn_condition_service,
    get_churn_conditions_by_user_service,
    get_accounts_by_user_churn_conditions_service,
    delete_churn_condition_service
)
from controllers.organization_controller import (
    create_organization_service,
    get_organization_service,
    get_organization_by_slug_service,
    update_organization_service,
    delete_organization_service,
    add_user_to_organization_service,
    get_organization_users_service,
    get_organization_stats_service
)


# Initialize DB and create tables
with app.app_context():
    db.create_all()


# ============================================
# SECURITY HEADERS & CACHE CONTROL
# ============================================

@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    # Prevent caching of sensitive pages
    if request.endpoint and any(x in request.endpoint for x in ['dashboard', 'account', 'priority', 'churn']):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response


# ============================================
# AUTHENTICATION & AUTHORIZATION DECORATORS
# ============================================

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required. Please login.'}), 401
        return f(*args, **kwargs)
    return decorated_function


def validate_user_access(f):
    """
    Decorator to validate:
    1. User exists in database
    2. Logged-in user can only access their own data (unless admin)
    
    Usage: Apply to routes with <int:user_id> parameter
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get user_id from route parameter
        requested_user_id = kwargs.get('user_id')
        
        if not requested_user_id:
            return redirect(url_for('home'))
        
        # Check if requested user exists
        requested_user = User.query.get(requested_user_id)
        if not requested_user:
            return "<h1>404 - User Not Found</h1><p>The requested user does not exist.</p>", 404
        
        # Check if someone is logged in
        logged_in_user_id = session.get('user_id')
        if not logged_in_user_id:
            # Not logged in - redirect to home/login page immediately
            return redirect(url_for('home'))
        
        # Get logged-in user
        logged_in_user = User.query.get(logged_in_user_id)
        if not logged_in_user:
            # Invalid session - clear it and redirect to login
            session.clear()
            return redirect(url_for('home'))
        
        # Check authorization: user can only access their own data OR is admin
        if logged_in_user_id != requested_user_id and logged_in_user.user_role != 'admin':
            return f"""
                <h1>403 - Access Denied</h1>
                <p>You can only access your own dashboard.</p>
                <p>You are logged in as user {logged_in_user_id}, but tried to access user {requested_user_id}'s dashboard.</p>
                <p><a href="/dashboard/{logged_in_user_id}">Go to your dashboard</a></p>
                <p><a href="/logout">Logout</a></p>
            """, 403
        
        # All checks passed - proceed with the route
        return f(*args, **kwargs)
    return decorated_function


def validate_user_exists(f):
    """
    Lightweight decorator to just check if user exists (no auth check)
    Use this for public/semi-public routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = kwargs.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return "User not found", 404
        
        return f(*args, **kwargs)
    return decorated_function


# --- Routes ---

@app.route('/', methods=['GET'])
def home():
    """Landing page - renders login/signup page"""
    return render_template('html/myre_new.html')


# --- Organization Routes ---

@app.route('/organization/signup', methods=['GET'])
def organization_signup_page():
    """Render organization signup page"""
    return render_template('html/org_signup.html')


@app.route('/organization/signup', methods=['POST'])
def organization_signup():
    """Create new organization with admin user"""
    data = request.get_json()
    
    org_data = data.get('organization', {})
    admin_data = data.get('admin', {})
    
    if not org_data or not admin_data:
        return jsonify({'error': 'Organization and admin data are required'}), 400
    
    # Create organization and admin user
    organization, admin_user = create_organization_service(org_data, admin_data)
    
    if not organization or not admin_user:
        return jsonify({'error': 'Failed to create organization. Email may already exist.'}), 400
    
    return jsonify({
        'message': 'Organization created successfully',
        'organization': organization.to_dict(),
        'admin_user': {
            'id': admin_user.id,
            'name': admin_user.user_name,
            'email': admin_user.user_email,
            'role': admin_user.user_role,
            'is_org_admin': admin_user.is_org_admin
        }
    }), 201


@app.route('/organization/<int:org_id>', methods=['GET'])
def get_organization(org_id):
    """Get organization details by ID"""
    organization = get_organization_service(org_id)
    
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify(organization.to_dict())


@app.route('/organization/<int:org_id>', methods=['PUT'])
def update_organization(org_id):
    """Update organization details"""
    data = request.get_json()
    
    organization = update_organization_service(org_id, data)
    
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify({
        'message': 'Organization updated successfully',
        'organization': organization.to_dict()
    })


@app.route('/organization/<int:org_id>', methods=['DELETE'])
def delete_organization(org_id):
    """Soft delete organization and all users"""
    success = delete_organization_service(org_id)
    
    if not success:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify({'message': 'Organization deleted successfully'})


@app.route('/organization/<int:org_id>/users', methods=['GET'])
def get_organization_users(org_id):
    """Get all users in an organization"""
    users = get_organization_users_service(org_id)
    
    return jsonify({
        'organization_id': org_id,
        'total_users': len(users),
        'users': [{
            'id': user.id,
            'name': user.user_name,
            'email': user.user_email,
            'role': user.user_role,
            'is_org_admin': user.is_org_admin,
            'status': user.user_status,
            'created_at': user.user_created_at.isoformat() if user.user_created_at else None
        } for user in users]
    })


@app.route('/organization/<int:org_id>/users', methods=['POST'])
def add_organization_user(org_id):
    """Add a new user/employee to organization"""
    data = request.get_json()
    
    if not data.get('user_email') or not data.get('user_name') or not data.get('user_password'):
        return jsonify({'error': 'User name, email, and password are required'}), 400
    
    new_user = add_user_to_organization_service(org_id, data)
    
    if not new_user:
        return jsonify({'error': 'Failed to add user. Organization may be at user limit or email already exists.'}), 400
    
    return jsonify({
        'message': 'User added successfully',
        'user': {
            'id': new_user.id,
            'name': new_user.user_name,
            'email': new_user.user_email,
            'role': new_user.user_role,
            'is_org_admin': new_user.is_org_admin
        }
    }), 201


@app.route('/organization/<int:org_id>/stats', methods=['GET'])
def get_organization_stats(org_id):
    """Get organization statistics (users, accounts, limits)"""
    stats = get_organization_stats_service(org_id)
    
    if not stats:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify(stats)


@app.route('/organization/slug/<slug>', methods=['GET'])
def get_organization_by_slug(slug):
    """Get organization by slug"""
    organization = get_organization_by_slug_service(slug)
    
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify(organization.to_dict())


@app.route('/organization/add_employee', methods=['GET'])
def add_employee_page():
    """Render add employee page"""
    return render_template('html/add_employee.html')


@app.route('/login', methods=['POST'])
def login():
    """Authenticate user with email and password"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Find user by email
    user = User.query.filter_by(user_email=email).first()
    
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check password (in production, use hashed passwords)
    if user.user_password != password:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Set session - user is now logged in
    session['user_id'] = user.id
    session['user_email'] = user.user_email
    session['user_role'] = user.user_role
    
    # Return user data
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'name': user.user_name,
            'email': user.user_email,
            'role': user.user_role,
            'organization_id': user.organization_id,
            'is_org_admin': user.is_org_admin
        }
    }), 200


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    """Logout user (clear session)"""
    # Clear the session
    session.clear()
    
    if request.method == 'POST':
        response = jsonify({'message': 'Logged out successfully'})
        response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage"'
        return response, 200
    else:
        # Redirect to home page for GET requests
        response = redirect(url_for('home'))
        response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage"'
        return response


@app.route('/session', methods=['GET'])
def get_session():
    """Get current session info (for testing/debugging)"""
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user_id': session.get('user_id'),
            'user_email': session.get('user_email'),
            'user_role': session.get('user_role')
        }), 200
    else:
        return jsonify({'logged_in': False}), 200


@app.route('/signup', methods=['POST'])
def signup():
    """Create new user account with default CSM role"""
    data = request.get_json()
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(user_email=email).first()
    if existing_user:
        return jsonify({'error': 'An account with this email already exists'}), 409
    
    # Create new user
    user_data = {
        'user_name': name,
        'user_email': email,
        'user_password': password,  # In production, hash this password
        'user_role': 'csm'  # Default role
    }
    
    new_user = create_user_service(user_data)
    
    return jsonify({
        'message': 'Account created successfully',
        'user': {
            'id': new_user.id,
            'name': new_user.user_name,
            'email': new_user.user_email,
            'role': new_user.user_role
        }
    }), 201


@app.route('/csm_dashboard/<int:user_id>', methods=['GET'])
@validate_user_access
def csm_dashboard(user_id):
    """Redirect to analytics dashboard"""
    return redirect(url_for('dashboard', user_id=user_id))


@app.route('/account_management_dashboard/<int:user_id>', methods=['GET'])
@validate_user_access
def account_management_dashboard(user_id):
    """Account management selection page"""
    # Get user (already validated by decorator)
    user = User.query.get(user_id)
    
    # Get account stats
    all_accounts = Account.query.filter_by(csm_user_id=user_id).all()
    active_accounts = Account.query.filter_by(csm_user_id=user_id, account_status='active').all()
    
    # Get priority accounts count
    priority_result = get_accounts_by_user_priority_conditions_service(user_id)
    priority_count = priority_result.get('total_unique_accounts', 0) if priority_result else 0
    
    return render_template('html/account_management.html',
                         user_id=user_id,
                         user_email=user.user_email,
                         total_accounts=len(all_accounts),
                         active_accounts=len(active_accounts),
                         priority_count=priority_count)


@app.route('/dashboard/<int:user_id>', methods=['GET'])
@validate_user_access
def dashboard(user_id):
    """Main dashboard with graphs and stats"""
    # Get user (already validated by decorator)
    user = User.query.get(user_id)
    
    # Get all accounts for this user
    all_accounts = Account.query.filter_by(csm_user_id=user_id).all()
    active_accounts = Account.query.filter_by(csm_user_id=user_id, account_status='active').all()
    
    # Get priority accounts count
    priority_result = get_accounts_by_user_priority_conditions_service(user_id)
    priority_count = priority_result.get('total_unique_accounts', 0) if priority_result else 0
    
    return render_template('html/dashboard.html',
                         user_id=user_id,
                         user_email=user.user_email,
                         total_accounts=len(all_accounts),
                         active_accounts=len(active_accounts),
                         priority_accounts=priority_count)


@app.route('/priority_accounts_dashboard/<int:user_id>', methods=['GET'])
@validate_user_access
def priority_accounts_dashboard(user_id):
    """Render priority accounts dashboard with rules and filtered accounts for user"""
    result = get_accounts_by_user_priority_conditions_service(user_id)
    
    if result is None:
        # Return empty data if no conditions found
        result = {
            'user_id': user_id,
            'total_conditions': 0,
            'conditions': [],
            'total_unique_accounts': 0,
            'accounts': []
        }
    
    # Serialize accounts for template
    accounts = [serialize_account(account) for account in result.get('accounts', [])]
    
    return render_template('html/index.html', 
                         user_id=user_id,
                         accounts=accounts,
                         conditions=result.get('conditions', []),
                         total_conditions=result.get('total_conditions', 0),
                         total_accounts=result.get('total_unique_accounts', 0),
                         active_section='dashboard')


@app.route('/account/<int:account_id>', methods=['GET'])
def get_account_details(account_id):
    """Get account details by ID"""
    account = Account.query.get(account_id)
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    return jsonify(serialize_account(account)), 200


@app.route('/priority_accounts_dashboard/<int:user_id>/automation', methods=['GET'])
@validate_user_access
def automation_view(user_id):
    """Render automation section of dashboard for user"""
    result = get_accounts_by_user_priority_conditions_service(user_id)
    
    if result is None:
        result = {
            'user_id': user_id,
            'total_conditions': 0,
            'conditions': [],
            'total_unique_accounts': 0,
            'accounts': []
        }
    
    accounts = [serialize_account(account) for account in result.get('accounts', [])]
    
    return render_template('html/index.html', 
                         user_id=user_id,
                         accounts=accounts,
                         conditions=result.get('conditions', []),
                         total_conditions=result.get('total_conditions', 0),
                         total_accounts=result.get('total_unique_accounts', 0),
                         active_section='automation')


@app.route('/priority_accounts_dashboard/<int:user_id>/integration', methods=['GET'])
@validate_user_access
def integration_view(user_id):
    """Render integration section of dashboard for user"""
    result = get_accounts_by_user_priority_conditions_service(user_id)
    
    if result is None:
        result = {
            'user_id': user_id,
            'total_conditions': 0,
            'conditions': [],
            'total_unique_accounts': 0,
            'accounts': []
        }
    
    accounts = [serialize_account(account) for account in result.get('accounts', [])]
    
    return render_template('html/index.html', 
                         user_id=user_id,
                         accounts=accounts,
                         conditions=result.get('conditions', []),
                         total_conditions=result.get('total_conditions', 0),
                         total_accounts=result.get('total_unique_accounts', 0),
                         active_section='integration')

# --- User Routes ---

@app.route('/users', methods=['POST'])
def create_user():
    """Create new user via API"""
    data = request.get_json()
    
    # Call controller service to handle business logic
    user = create_user_service(data)
    
    return jsonify({'message': 'User created', 'user_id': user.id}), 201


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details by ID"""
    # Call controller service to handle business logic
    user = get_user_service(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'user_name': user.user_name,
        'user_email': user.user_email,
        'user_role': user.user_role,
        'user_status': user.user_status,
        'company_id': user.company_id
    })


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user information by ID"""
    data = request.get_json()
    
    # Call controller service to handle business logic
    user = update_user_service(user_id, data)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({'message': 'User updated'})


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Soft delete user by ID"""
    # Call controller service to handle business logic
    success = delete_user_service(user_id)
    
    if not success:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({'message': 'User deleted (soft delete)'})


# --- Account Routes ---

@app.route('/accounts', methods=['POST'])
def create_account_route():
    """Create new customer account"""
    data = request.get_json()
    
    account = create_account_service(data)
    
    return jsonify({'message': 'Account created', 'account_id': account.id}), 201


@app.route('/accounts/<int:account_id>/fields', methods=['GET'])
def get_account_populated_fields_route(account_id):
    """Get all non-null field names for an account (useful for building filters)"""
    fields = get_account_filter_conditions(account_id)
    
    if fields is None:
        return jsonify({'message': 'Account not found'}), 404
    
    return jsonify({
        'account_id': account_id,
        'populated_fields': fields,
        'total_fields': len(fields)
    })


@app.route('/accounts/<int:account_id>', methods=['GET'])
def get_account_route(account_id):
    """Get account details by ID"""
    account = get_account_service(account_id)
    
    if not account:
        return jsonify({'message': 'Account not found'}), 404

    return jsonify(serialize_account(account))


@app.route('/accounts/<int:account_id>', methods=['PUT'])
def update_account_route(account_id):
    """Update account information by ID"""
    data = request.get_json()
    
    account = update_account_service(account_id, data)
    
    if not account:
        return jsonify({'message': 'Account not found'}), 404

    return jsonify({'message': 'Account updated'})


@app.route('/accounts/<int:account_id>', methods=['DELETE'])
def delete_account_route(account_id):
    """Delete account by ID"""
    # Call controller service to handle business logic
    success = delete_account_service(account_id)
    
    if not success:
        return jsonify({'message': 'Account not found'}), 404

    return jsonify({'message': 'Account deleted'})


# --- Priority Condition Routes ---
@app.route('/priority_conditions/<int:user_id>', methods=['GET'])
def get_priority_condition_accounts_by_user_route(user_id):
    """Get all priority rules created by a specific user"""
    from controllers.priority_condition_controller import get_priority_conditions_by_user_service
    
    conditions = get_priority_conditions_by_user_service(user_id)
    
    if not conditions:
        return jsonify({
            'user_id': user_id,
            'total_conditions': 0,
            'conditions': []
        }), 200
    
    # Serialize conditions
    result = {
        'user_id': user_id,
        'total_conditions': len(conditions),
        'conditions': [condition.to_dict() for condition in conditions]
    }
    
    return jsonify(result)

@app.route('/priority_conditions_all', methods=['GET'])
def get_all_priority_conditions_route():
    """Get all priority rules across all users"""
    conditions = PriorityCondition.query.all()
    
    result = [condition.to_dict() for condition in conditions]
    
    return jsonify({
        'total_conditions': len(result),
        'conditions': result
    })


@app.route('/priority_condition/<int:account_id>', methods=['GET'])
def get_priority_condition_fields_route(account_id):
    """Get available filter fields for an account (same as /accounts/<id>/fields)"""
    fields = get_account_filter_conditions(account_id)
    
    if fields is None:
        return jsonify({'message': 'Account not found'}), 404
    
    return jsonify({
        'account_id': account_id,
        'available_filter_fields': fields,
    })
    
@app.route('/priority_conditions', methods=['POST'])
@login_required
def create_priority_condition_route():
    """Create a new priority condition with the filter conditions (requires: condition_name, filter_conditions, created_by)"""
    data = request.get_json()
    
    if not data.get('filter_conditions'):
        return jsonify({'error': 'filter_conditions is required'}), 400
    
    # Use account_id=0 as placeholder since this endpoint doesn't require it
    priority_condition = create_priority_condition_service(0, data)
    
    if priority_condition is None:
        return jsonify({'error': 'Failed to create priority condition'}), 400
    
    return jsonify({
        'message': 'Priority condition created successfully',
        'priority_condition': priority_condition.to_dict()
    }), 201


@app.route('/priority_conditions/<int:condition_id>', methods=['DELETE'])
@login_required
def delete_priority_condition_route(condition_id):
    """Delete a priority condition"""
    condition = PriorityCondition.query.get(condition_id)
    if not condition:
        return jsonify({'error': 'Priority condition not found'}), 404
    
    db.session.delete(condition)
    db.session.commit()
    
    return jsonify({'message': 'Priority condition deleted successfully'}), 200


@app.route('/priority_condition/<int:account_id>', methods=['POST'])
@login_required
def create_priority_condition_legacy_route(account_id):
    """Create priority rule using account_id as reference (legacy endpoint)"""
    data = request.get_json()
    
    priority_condition = create_priority_condition_service(account_id, data)
    
    if priority_condition is None:
        return jsonify({'message': 'filter_conditions is required'}), 400
    
    return jsonify({
        'message': 'Priority condition created',
        'priority_condition_id': priority_condition.id,
        'condition_name': priority_condition.condition_name,
        'filter_conditions': priority_condition.get_filter_conditions()
    }), 201


@app.route('/priority_accounts/<int:condition_id>', methods=['GET'])
def get_priority_accounts_route(condition_id):
    """Get all accounts matching a priority rule's filter conditions"""
    accounts = get_priority_accounts_service(condition_id)
    
    if accounts is None:
        return jsonify({'message': 'Priority condition not found'}), 404
    
    return jsonify({
        'condition_id': condition_id,
        'total_accounts': len(accounts),
        'accounts': [serialize_account(account) for account in accounts]
    })


# ============================================
# CHURN MANAGEMENT ROUTES
# ============================================

@app.route('/churn_management/<int:user_id>', methods=['GET'])
@validate_user_access
def churn_management_dashboard(user_id):
    """Render churn management dashboard for user"""
    result = get_accounts_by_user_churn_conditions_service(user_id)
    
    if result is None:
        result = {
            'user_id': user_id,
            'total_conditions': 0,
            'conditions': [],
            'total_unique_accounts': 0,
            'accounts': []
        }
    
    accounts = [serialize_account(account) for account in result.get('accounts', [])]
    
    return render_template('html/churn_management.html',
                         user_id=user_id,
                         accounts=accounts,
                         conditions=result.get('conditions', []),
                         total_conditions=result.get('total_conditions', 0),
                         total_accounts=result.get('total_unique_accounts', 0),
                         active_section='churn')


@app.route('/churn_conditions/<int:user_id>', methods=['GET'])
def get_churn_conditions_by_user_route(user_id):
    """Get all churn rules created by a specific user"""
    conditions = get_churn_conditions_by_user_service(user_id)
    
    # Convert to dict format for JSON response
    return jsonify([c.to_dict() for c in conditions]), 200


@app.route('/churn_conditions', methods=['POST'])
@login_required
def create_churn_condition_route():
    """Create a new churn condition"""
    data = request.json
    
    # Convert old format to new unified format
    if 'field_name' in data and 'operator' in data and 'field_value' in data:
        # Old format - convert to new format
        unified_data = {
            'condition_name': data.get('condition_name'),
            'description': data.get('condition_description', ''),
            'filter_conditions': {
                data['field_name']: {
                    'operator': data['operator'],
                    'value': data['field_value']
                }
            },
            'created_by': data.get('user_id')
        }
    else:
        # Already in new format
        unified_data = data
    
    condition = create_churn_condition_service(unified_data)
    
    if condition is None:
        return jsonify({'error': 'Failed to create churn condition', 'success': False}), 400
    
    return jsonify({
        'success': True,
        'message': 'Churn condition created successfully',
        'condition': condition.to_dict()
    }), 201


@app.route('/churn_conditions/<int:condition_id>', methods=['DELETE'])
@login_required
def delete_churn_condition_route(condition_id):
    """Delete a churn condition"""
    success = delete_churn_condition_service(condition_id)
    
    if success:
        return jsonify({'message': 'Churn condition deleted successfully'}), 200
    else:
        return jsonify({'error': 'Churn condition not found'}), 404


# ============================================
# UNIFIED RULES API (Priority, Churn, Upsell, Custom)
# ============================================

from controllers.rule_controller import (
    create_rule,
    get_rules_by_type,
    get_rule_by_id,
    update_rule,
    delete_rule,
    get_accounts_by_rule,
    get_accounts_by_user_rules
)

@app.route('/api/rules', methods=['POST'])
@login_required
def create_rule_route():
    """Create a new rule (any type: priority, churn, upsell, custom)"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('rule_name') or not data.get('rule_type') or not data.get('filter_conditions'):
        return jsonify({'error': 'rule_name, rule_type, and filter_conditions are required'}), 400
    
    rule = create_rule(data)
    
    if rule is None:
        return jsonify({'error': 'Failed to create rule'}), 400
    
    return jsonify(rule.to_dict()), 201


@app.route('/api/rules/<rule_type>', methods=['GET'])
@login_required
def get_rules_by_type_route(rule_type):
    """Get all rules of a specific type for a user"""
    user_id = request.args.get('user_id', type=int)
    include_shared = request.args.get('include_shared', 'false').lower() == 'true'
    organization_id = request.args.get('organization_id', type=int)
    
    if not user_id:
        return jsonify({'error': 'user_id parameter is required'}), 400
    
    rules = get_rules_by_type(user_id, rule_type, include_shared, organization_id)
    
    return jsonify([rule.to_dict() for rule in rules]), 200


@app.route('/api/rules/<int:rule_id>', methods=['GET'])
@login_required
def get_rule_route(rule_id):
    """Get a specific rule by ID"""
    rule = get_rule_by_id(rule_id)
    
    if rule is None:
        return jsonify({'error': 'Rule not found'}), 404
    
    return jsonify(rule.to_dict()), 200


@app.route('/api/rules/<int:rule_id>', methods=['PUT'])
@login_required
def update_rule_route(rule_id):
    """Update an existing rule"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    rule = update_rule(rule_id, data, user_id)
    
    if rule is None:
        return jsonify({'error': 'Rule not found or unauthorized'}), 404
    
    return jsonify(rule.to_dict()), 200


@app.route('/api/rules/<int:rule_id>', methods=['DELETE'])
@login_required
def delete_rule_route(rule_id):
    """Delete a rule"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    success = delete_rule(rule_id, user_id)
    
    if not success:
        return jsonify({'error': 'Rule not found or unauthorized'}), 404
    
    return jsonify({'message': 'Rule deleted successfully'}), 200


@app.route('/api/rules/<int:rule_id>/accounts', methods=['GET'])
@login_required
def get_rule_accounts_route(rule_id):
    """Get all accounts matching a specific rule"""
    user_id = request.args.get('user_id', type=int)
    use_cache = request.args.get('use_cache', 'true').lower() == 'true'
    
    if not user_id:
        return jsonify({'error': 'user_id parameter is required'}), 400
    
    accounts = get_accounts_by_rule(rule_id, user_id, use_cache)
    
    if accounts is None:
        return jsonify({'error': 'Rule not found'}), 404
    
    return jsonify({
        'rule_id': rule_id,
        'total_accounts': len(accounts),
        'accounts': [serialize_account(account) for account in accounts]
    }), 200


@app.route('/api/users/<int:user_id>/rules/accounts', methods=['GET'])
@validate_user_access
def get_user_rules_accounts_route(user_id):
    """Get all accounts matching ANY of user's rules (OR logic)"""
    rule_type = request.args.get('rule_type')  # Optional filter by type
    
    result = get_accounts_by_user_rules(user_id, rule_type)
    
    if result is None:
        return jsonify({
            'user_id': user_id,
            'total_rules': 0,
            'rules': [],
            'total_unique_accounts': 0,
            'accounts': []
        }), 200
    
    # Serialize accounts
    result['accounts'] = [serialize_account(account) for account in result['accounts']]
    
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(debug=True)


