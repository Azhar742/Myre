import sys
import os
import random
from faker import Faker
from datetime import datetime

# Add parent dir to sys.path so we can import app + controllers + models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from controllers.account_controller import create_account_service

fake = Faker()

def create_fake_accounts(n=10):
    with app.app_context():
        for _ in range(n):
            data = {
                'account_name': fake.company(),
                'account_id': fake.uuid4(),
                'client_account_id': fake.uuid4(),
                'client_email': fake.email(),
                'client_phn': fake.phone_number(),
                'last_paid_bill_amount': round(random.uniform(50, 500), 2),
                'last_paid_bill_date': fake.date_time_between(start_date='-90d', end_date='-1d'),
                'next_due_date': fake.date_time_between(start_date='now', end_date='+60d'),
                'last_meaningful_interaction': fake.date_time_between(start_date='-30d', end_date='now'),
                'account_status': random.choice(['active', 'inactive', 'suspended']),
                'company_name': fake.company(),
                'domain': fake.domain_name(),
                'plan_name': random.choice(['Basic', 'Pro', 'Enterprise']),
                'meta_data': fake.text(max_nb_chars=200),
                'last_login': fake.date_time_between(start_date='-15d', end_date='now'),
                'last_sent_email': fake.date_time_between(start_date='-7d', end_date='now')
            }
            # Set created_at to a random date within the last 30 days
            from datetime import datetime, timedelta
            data['created_at'] = fake.date_time_between(start_date='-30d', end_date='now')
            create_account_service(data)

        print(f"{n} fake accounts added.")

if __name__ == "__main__":
    create_fake_accounts(20)  # Adjust number as needed
