from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from functools import wraps
import os

# Initialize Flask app first
app = Flask(__name__, template_folder='views', static_folder='views', static_url_path='/static')
# Use absolute path to ensure database is in project root
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')


# Import blueprints
from blueprints.collab_routes import collab_bp
from blueprints.auth_routes import auth_bp
from blueprints.account_routes import account_bp
from blueprints.churn_management_routes import churn_management_bp
from blueprints.collab_routes import collab_bp
from blueprints.org_routes import org_bp
from blueprints.user_routes import user_bp
from blueprints.collab_insights_calander import calendar_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(org_bp)
app.register_blueprint(collab_bp)
app.register_blueprint(account_bp)
app.register_blueprint(user_bp)
app.register_blueprint(churn_management_bp)
app.register_blueprint(calendar_bp)

# Import db and initialize it
from models.user_model import db, User

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myre.db'

db.init_app(app)

# Import ALL models before db.create_all()
from models.account_model import Account
from models.priority_condition_model import PriorityCondition
from models.churn_condition_model import ChurnCondition
from models.organization_model import Organization

# Import utilities and controllers
from utils.utils import serialize_account


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

from decorators import login_required, validate_user_access

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


