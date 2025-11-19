from functools import wraps
from flask import session, jsonify, redirect, url_for
from models.user_model import User

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
        requested_user_id = kwargs.get('user_id')
        if not requested_user_id:
            return redirect(url_for('home'))
        requested_user = User.query.get(requested_user_id)
        if not requested_user:
            return "<h1>404 - User Not Found</h1><p>The requested user does not exist.</p>", 404
        logged_in_user_id = session.get('user_id')
        if not logged_in_user_id:
            return redirect(url_for('home'))
        logged_in_user = User.query.get(logged_in_user_id)
        if not logged_in_user:
            session.clear()
            return redirect(url_for('home'))
        if logged_in_user_id != requested_user_id and logged_in_user.user_role != 'admin':
            return f"""
                <h1>403 - Access Denied</h1>
                <p>You are logged in as user {logged_in_user_id}, but tried to access user {requested_user_id}'s dashboard.</p>
                <p><a href=\"/dashboard/{logged_in_user_id}\">Go to your dashboard</a></p>
                <p><a href=\"/logout\">Logout</a></p>
            """, 403
        return f(*args, **kwargs)
    return decorated_function
