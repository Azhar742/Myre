from models.user_model import db
from models.account_model import Account
from datetime import datetime

def create_account_service(data):
    account = Account(
        account_name=data['account_name'],
        account_id=data['account_id'],
        client_account_id=data['client_account_id'],
        client_email=data.get('client_email'),
        client_phn=data.get('client_phn'),
        last_paid_bill_amount=data.get('last_paid_bill_amount'),
        last_paid_bill_date=data.get('last_paid_bill_date'),
        next_due_date=data.get('next_due_date'),
        last_meaningful_interaction=data.get('last_meaningful_interaction'),
        account_status=data.get('account_status', 'active'),
        company_name=data.get('company_name'),
        domain=data.get('domain'),
        plan_name=data.get('plan_name'),
        meta_data=data.get('meta_data'),
        last_login=data.get('last_login'),
        last_sent_email=data.get('last_sent_email')
    )
    db.session.add(account)
    db.session.commit()
    return account

def get_account_service(account_id):
    return Account.query.get(account_id)

def update_account_service(account_id, data):
    account = Account.query.get(account_id)
    if not account:
        return None
    for key, value in data.items():
        if hasattr(account, key):
            setattr(account, key, value)
    account.last_updated = datetime.utcnow()
    db.session.commit()
    return account

def delete_account_service(account_id):
    account = Account.query.get(account_id)
    if not account:
        return False
    db.session.delete(account)
    db.session.commit()
    return True


