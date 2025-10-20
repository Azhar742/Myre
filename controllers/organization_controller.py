from models.user_model import db, User
from models.organization_model import Organization
from datetime import datetime
import re


def generate_org_slug(org_name):
    """Generate URL-friendly slug from organization name"""
    slug = org_name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    
    # Ensure uniqueness
    base_slug = slug
    counter = 1
    while Organization.query.filter_by(org_slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug


def create_organization_service(org_data, admin_user_data):
    """
    Create a new organization with an admin user.
    This is the main signup flow for organizations.
    
    Args:
        org_data: Dictionary with organization details
        admin_user_data: Dictionary with admin user details
    
    Returns:
        Tuple of (organization, admin_user) or (None, None) on error
    """
    try:
        # Validate required fields
        if not org_data.get('org_name'):
            raise ValueError('Organization name is required')
        
        if not admin_user_data.get('user_email'):
            raise ValueError('Admin email is required')
        
        # Check if email already exists
        existing_user = User.query.filter_by(user_email=admin_user_data['user_email']).first()
        if existing_user:
            raise ValueError('An account with this email already exists')
        
        # Generate slug
        org_slug = generate_org_slug(org_data['org_name'])
        
        # Set subscription plan (no hard limits enforced)
        plan = org_data.get('subscription_plan', 'free')
        
        # Create organization
        organization = Organization(
            org_name=org_data['org_name'],
            org_slug=org_slug,
            org_email=org_data.get('org_email', admin_user_data['user_email']),
            org_phone=org_data.get('org_phone'),
            org_address=org_data.get('org_address'),
            org_city=org_data.get('org_city'),
            org_state=org_data.get('org_state'),
            org_country=org_data.get('org_country'),
            org_zipcode=org_data.get('org_zipcode'),
            org_industry=org_data.get('org_industry'),
            org_size=org_data.get('org_size'),
            org_website=org_data.get('org_website'),
            subscription_plan=plan,
            subscription_status='active',
            max_users=org_data.get('max_users'),  # Optional, can be None
            max_accounts=org_data.get('max_accounts'),  # Optional, can be None
            org_status='active'
        )
        
        db.session.add(organization)
        db.session.flush()  # Get organization ID
        
        # Create admin user
        admin_user = User(
            user_name=admin_user_data['user_name'],
            user_email=admin_user_data['user_email'],
            user_password=admin_user_data['user_password'],  # Hash in production!
            user_role=admin_user_data.get('user_role', 'admin'),
            organization_id=organization.id,
            is_org_admin=True,
            user_status='active'
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        return organization, admin_user
    
    except Exception as e:
        db.session.rollback()
        print(f"Error creating organization: {str(e)}")
        return None, None


def get_organization_service(org_id):
    """Get organization by ID"""
    return Organization.query.filter_by(id=org_id, deleted_at=None).first()


def get_organization_by_slug_service(org_slug):
    """Get organization by slug"""
    return Organization.query.filter_by(org_slug=org_slug, deleted_at=None).first()


def update_organization_service(org_id, org_data):
    """Update organization details"""
    try:
        organization = Organization.query.filter_by(id=org_id, deleted_at=None).first()
        
        if not organization:
            return None
        
        # Update allowed fields
        allowed_fields = [
            'org_name', 'org_email', 'org_phone', 'org_address', 'org_city',
            'org_state', 'org_country', 'org_zipcode', 'org_industry', 'org_size',
            'org_website', 'subscription_plan', 'max_users', 'max_accounts', 'settings'
        ]
        
        for field in allowed_fields:
            if field in org_data:
                setattr(organization, field, org_data[field])
        
        db.session.commit()
        return organization
    
    except Exception as e:
        db.session.rollback()
        print(f"Error updating organization: {str(e)}")
        return None


def delete_organization_service(org_id):
    """Soft delete organization and all associated users"""
    try:
        organization = Organization.query.filter_by(id=org_id, deleted_at=None).first()
        
        if not organization:
            return False
        
        # Soft delete organization
        organization.deleted_at = datetime.utcnow()
        organization.org_status = 'inactive'
        
        # Soft delete all users in organization
        users = User.query.filter_by(organization_id=org_id, user_deleted_at=None).all()
        for user in users:
            user.user_deleted_at = datetime.utcnow()
            user.user_status = 'inactive'
        
        db.session.commit()
        return True
    
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting organization: {str(e)}")
        return False


def add_user_to_organization_service(org_id, user_data):
    """
    Add a new employee/user to an existing organization.
    Used for inviting team members.
    """
    try:
        organization = Organization.query.filter_by(id=org_id, deleted_at=None).first()
        
        if not organization:
            raise ValueError('Organization not found')
        
        if not organization.is_active():
            raise ValueError('Organization is not active')
        
        # Check user limit only if max_users is set
        if not organization.can_add_user():
            limit_msg = f'({organization.max_users})' if organization.max_users else ''
            raise ValueError(f'Organization has reached maximum user limit {limit_msg}'.strip())
        
        # Check if email already exists
        existing_user = User.query.filter_by(user_email=user_data['user_email']).first()
        if existing_user:
            raise ValueError('An account with this email already exists')
        
        # Create new user
        new_user = User(
            user_name=user_data['user_name'],
            user_email=user_data['user_email'],
            user_password=user_data['user_password'],  # Hash in production!
            user_role=user_data.get('user_role', 'csm'),
            organization_id=org_id,
            is_org_admin=user_data.get('is_org_admin', False),
            user_status='active'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return new_user
    
    except Exception as e:
        db.session.rollback()
        print(f"Error adding user to organization: {str(e)}")
        return None


def get_organization_users_service(org_id):
    """Get all active users in an organization"""
    return User.query.filter_by(
        organization_id=org_id,
        user_deleted_at=None
    ).order_by(User.is_org_admin.desc(), User.user_created_at).all()


def get_organization_stats_service(org_id):
    """Get statistics for an organization"""
    organization = Organization.query.filter_by(id=org_id, deleted_at=None).first()
    
    if not organization:
        return None
    
    active_users = organization.get_active_users_count()
    
    # Import Account here to avoid circular imports
    from models.account_model import Account
    active_accounts = Account.query.filter_by(
        organization_id=org_id,
        account_status='active'
    ).count()
    
    return {
        'organization': organization.to_dict(),
        'active_users': active_users,
        'max_users': organization.max_users,
        'users_remaining': (organization.max_users - active_users) if organization.max_users else None,
        'active_accounts': active_accounts,
        'max_accounts': organization.max_accounts,
        'accounts_remaining': (organization.max_accounts - active_accounts) if organization.max_accounts else None
    }
