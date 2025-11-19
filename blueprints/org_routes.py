# --- Organization Routes ---

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from controllers.organization_controller import (
    create_organization_service,
    get_organization_service,
    update_organization_service,
    delete_organization_service,
    get_organization_users_service,
    get_organization_stats_service,
    get_organization_by_slug_service,
    add_user_to_organization_service)

from controllers.priority_condition_controller import (
    get_accounts_by_user_priority_conditions_service
)

from models.user_model import User
from models.account_model import Account
from decorators import validate_user_access


org_bp = Blueprint('org_bp', __name__)

@org_bp.route('/organization/signup', methods=['GET'])
def organization_signup_page():
    """Render organization signup page"""
    return render_template('html/org_signup.html')


@org_bp.route('/organization/signup', methods=['POST'])
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

@org_bp.route('/organization/<int:org_id>', methods=['GET'])
def get_organization(org_id):
    """Get organization details by ID"""
    organization = get_organization_service(org_id)
    
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify(organization.to_dict())


@org_bp.route('/organization/<int:org_id>', methods=['PUT'])
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


@org_bp.route('/organization/<int:org_id>', methods=['DELETE'])
def delete_organization(org_id):
    """Soft delete organization and all users"""
    success = delete_organization_service(org_id)
    
    if not success:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify({'message': 'Organization deleted successfully'})


@org_bp.route('/organization/<int:org_id>/users', methods=['GET'])
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


@org_bp.route('/organization/<int:org_id>/users', methods=['POST'])
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


@org_bp.route('/organization/<int:org_id>/stats', methods=['GET'])
def get_organization_stats(org_id):
    """Get organization statistics (users, accounts, limits)"""
    stats = get_organization_stats_service(org_id)
    
    if not stats:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify(stats)


@org_bp.route('/organization/slug/<slug>', methods=['GET'])
def get_organization_by_slug(slug):
    """Get organization by slug"""
    organization = get_organization_by_slug_service(slug)
    
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify(organization.to_dict())


@org_bp.route('/organization/add_employee', methods=['GET'])
def add_employee_page():
    """Render add employee page"""
    return render_template('html/add_employee.html')


@org_bp.route('/csm_dashboard/<int:user_id>', methods=['GET'])
@validate_user_access
def csm_dashboard(user_id):
    """Redirect to analytics dashboard"""
    return redirect(url_for('org_bp.dashboard', user_id=user_id))


@org_bp.route('/account_management_dashboard/<int:user_id>', methods=['GET'])
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


@org_bp.route('/dashboard/<int:user_id>', methods=['GET'])
@validate_user_access
def dashboard(user_id):
    """Main dashboard with graphs and stats"""
    user = User.query.get(user_id)
    all_accounts = Account.query.filter_by(csm_user_id=user_id).all()
    active_accounts = Account.query.filter_by(csm_user_id=user_id, account_status='active').all()
    priority_result = get_accounts_by_user_priority_conditions_service(user_id)
    priority_count = priority_result.get('total_unique_accounts', 0) if priority_result else 0
    # Example dynamic data (replace with real queries as needed)
    monthly_accounts = [12, 19, 25, 32, 38, 45, 52, 61, 68, len(all_accounts)]
    monthly_revenue = [15, 18, 20, 22, 21, 24.5]
    weekly_activity = [45, 52, 48, 65, 58, 42, 38]
    return render_template('html/dashboard.html',
                         user_id=user_id,
                         user_email=user.user_email,
                         total_accounts=len(all_accounts),
                         active_accounts=len(active_accounts),
                         priority_accounts=priority_count,
                         monthly_accounts=monthly_accounts,
                         monthly_revenue=monthly_revenue,
                         weekly_activity=weekly_activity)
