def serialize_account(account):
    def dt_str(dt):
        return dt.isoformat() if dt else None

    return {
        'id': account.id,
        'account_name': account.account_name,
        'account_id': account.account_id,
        'client_account_id': account.client_account_id,
        'client_email': account.client_email,
        'client_phn': account.client_phn,
        'last_paid_bill_amount': account.last_paid_bill_amount,
        'last_paid_bill_date': dt_str(account.last_paid_bill_date),
        'next_due_date': dt_str(account.next_due_date),
        'last_meaningful_interaction': dt_str(account.last_meaningful_interaction),
        'account_status': account.account_status,
        'company_name': account.company_name,
        'domain': account.domain,
        'plan_name': account.plan_name,
        'meta_data': account.meta_data,
        'last_updated': dt_str(account.last_updated),
        'last_login': dt_str(account.last_login),
        'last_sent_email': dt_str(account.last_sent_email)
    }
