from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, event
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(150), nullable=False)
    user_email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    user_password = db.Column(db.String(200), nullable=False)  # In production, hash this!
    user_role = db.Column(db.String(50), default='user', index=True)
    user_status = db.Column(db.String(50), default='active')
    user_created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_deleted_at = db.Column(db.DateTime, nullable=True, index=True)
    company_name = db.Column(db.String(150), nullable=True)
    company_id = db.Column(db.Integer, nullable=True, index=True)

    # Define composite indexes
    __table_args__ = (
        Index('idx_users_email', 'user_email'),
        Index('idx_users_company_id', 'company_id'),
        Index('idx_users_deleted_at', 'user_deleted_at'),
        Index('idx_users_company_active', 'company_id', 'user_deleted_at'),
        Index('idx_users_role', 'user_role'),
    )

    def __repr__(self):
        return f'<User {self.user_email}>'


# Event listener to automatically update user_updated_at before update
@event.listens_for(User, 'before_update')
def receive_before_update(mapper, connection, target):
    """Trigger to update user_updated_at column before any update"""
    target.user_updated_at = datetime.utcnow()
