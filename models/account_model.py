from models.user_model import db
from datetime import datetime

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    account_name = db.Column(db.String(150), nullable=False)
    account_id = db.Column(db.String(100), unique=True, nullable=False)
    client_account_id = db.Column(db.String(100), unique=True, nullable=False)

    client_email = db.Column(db.String(150), nullable=True)
    client_phn = db.Column(db.String(20), nullable=True)

    last_paid_bill_amount = db.Column(db.Float, nullable=True)
    last_paid_bill_date = db.Column(db.DateTime, nullable=True)
    next_due_date = db.Column(db.DateTime, nullable=True)

    last_meaningful_interaction = db.Column(db.DateTime, nullable=True)
    account_status = db.Column(db.String(50), default='active')

    company_name = db.Column(db.String(150), nullable=True)
    domain = db.Column(db.String(150), nullable=True)
    plan_name = db.Column(db.String(100), nullable=True)

    meta_data = db.Column(db.Text, nullable=True)

    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    last_sent_email = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Account {self.account_name} | {self.account_id}>'
