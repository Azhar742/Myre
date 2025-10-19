from models.user_model import User
from app import db

def hello():
    # Check if a user exists, otherwise create one
    user = User.query.filter_by(username='testuser').first()
    if not user:
        user = User(username='testuser')
        db.session.add(user)
        db.session.commit()

    return f'Hello, {user.username}!'
