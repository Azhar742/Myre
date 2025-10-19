import sys
import os

# Add the parent directory (where app.py is) to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from faker import Faker
from app import app, db
from models.user_model import User
import random



fake = Faker()

ROLES = ['user', 'admin', 'moderator']
STATUS = ['active', 'inactive', 'banned']

def create_mock_users(n=10):
    with app.app_context():
        for _ in range(n):
            name = fake.name()
            email = fake.unique.email()
            password = fake.password(length=12)
            role = random.choice(ROLES)
            status = random.choice(STATUS)
            company = fake.company()
            company_id = random.randint(1, 1000)

            user = User(
                user_name=name,
                user_email=email,
                user_password=password,  # You should hash this in real apps
                user_role=role,
                user_status=status,
                company_name=company,
                company_id=company_id
            )
            db.session.add(user)

        db.session.commit()
        print(f'{n} mock users created.')

if __name__ == '__main__':
    create_mock_users(20)  # Change the number to generate more or fewer users
