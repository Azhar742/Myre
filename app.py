from flask import Flask, request, jsonify
import os

# Initialize Flask app first
app = Flask(__name__)
# Use absolute path to ensure database is in project root
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "mydatabase.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import db and initialize it
from models.user_model import db, User
db.init_app(app)

# Import ALL models before db.create_all()
from models.account_model import Account
from models.priority_condition_model import PriorityCondition

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
    delete_account_service,
)
from controllers.priority_condition_controller import (
    get_account_filter_conditions,
    create_priority_condition_service,
    get_priority_accounts_service
)


# Initialize DB and create tables
with app.app_context():
    db.create_all()

# --- Routes ---

@app.route('/', methods=['GET'])
def home():
    return 'Hello, World!'

# --- User Routes ---

@app.route('/users', methods=['POST'])
def create_user():
    """Route to create a new user - handles request/response only"""
    data = request.get_json()
    
    # Call controller service to handle business logic
    user = create_user_service(data)
    
    return jsonify({'message': 'User created', 'user_id': user.id}), 201


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Route to get a user by ID - handles request/response only"""
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
        'user_created_at': user.user_created_at.isoformat(),
        'user_updated_at': user.user_updated_at.isoformat(),
        'company_name': user.company_name,
        'company_id': user.company_id
    })


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Route to update a user - handles request/response only"""
    data = request.get_json()
    
    # Call controller service to handle business logic
    user = update_user_service(user_id, data)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({'message': 'User updated'})


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Route to delete a user - handles request/response only"""
    # Call controller service to handle business logic
    success = delete_user_service(user_id)
    
    if not success:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({'message': 'User deleted (soft delete)'})


# --- Account Routes ---

@app.route('/accounts', methods=['POST'])
def create_account_route():
    """Route to create a new account - handles request/response only"""
    data = request.get_json()
    
    account = create_account_service(data)
    
    return jsonify({'message': 'Account created', 'account_id': account.id}), 201


@app.route('/accounts/<int:account_id>/fields', methods=['GET'])
def get_account_populated_fields_route(account_id):
    """
    Get all field names that are populated (non-null) for a specific account.
    This is useful for understanding what data is available for filtering.
    """
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
    """Route to get an account by ID - handles request/response only"""
    account = get_account_service(account_id)
    
    if not account:
        return jsonify({'message': 'Account not found'}), 404

    return jsonify(serialize_account(account))


@app.route('/accounts/<int:account_id>', methods=['PUT'])
def update_account_route(account_id):
    """Route to update an account - handles request/response only"""
    data = request.get_json()
    
    account = update_account_service(account_id, data)
    
    if not account:
        return jsonify({'message': 'Account not found'}), 404

    return jsonify({'message': 'Account updated'})


@app.route('/accounts/<int:account_id>', methods=['DELETE'])
def delete_account_route(account_id):
    """Route to delete an account - handles request/response only"""
    # Call controller service to handle business logic
    success = delete_account_service(account_id)
    
    if not success:
        return jsonify({'message': 'Account not found'}), 404

    return jsonify({'message': 'Account deleted'})


# --- Priority Condition Routes ---

@app.route('/priority_condition/<int:account_id>', methods=['GET'])
def get_priority_condition_fields_route(account_id):
    """Get populated field names for an account to use as filter conditions"""
    fields = get_account_filter_conditions(account_id)
    
    if fields is None:
        return jsonify({'message': 'Account not found'}), 404
    
    return jsonify({
        'account_id': account_id,
        'available_filter_fields': fields,
    })
    
@app.route('/priority_condition/<int:account_id>', methods=['POST'])
def create_priority_condition_route(account_id):
    """
    Create a new priority condition with filter rules.
    
    Request body example:
    {
        "condition_name": "High Value Customers",
        "description": "Customers with bill > 100 and active status",
        "filter_conditions": {
            "account_status": {"operator": "==", "value": "active"},
            "last_paid_bill_amount": {"operator": ">", "value": 100}
        },
        "created_by": 1
    }
    """
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
    """
    Get all accounts that match the filter conditions of a priority condition.
    This applies all the stored filter rules (e.g., bill_amount > 100, status == active)
    """
    accounts = get_priority_accounts_service(condition_id)
    
    if accounts is None:
        return jsonify({'message': 'Priority condition not found'}), 404
    
    return jsonify({
        'condition_id': condition_id,
        'total_accounts': len(accounts),
        'accounts': [serialize_account(account) for account in accounts]
    })


if __name__ == '__main__':
    app.run(debug=True)
