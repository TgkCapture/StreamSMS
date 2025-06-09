import os
import django
import random
from datetime import datetime
from django.utils.crypto import get_random_string
from django.db import connection

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StreamSMS.settings")
django.setup()

from messages_app.models import Message

# Database configuration
DB_BACKEND = os.environ.get('DATABASE_BACKEND')
DB_NAME = os.environ.get('DATABASE_NAME')
DB_USER = os.environ.get('DATABASE_USER')
DB_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DB_HOST = os.environ.get('DATABASE_HOST')
DB_PORT = os.environ.get('DATABASE_PORT')

def create_database_if_not_exists():
    """
    Connects to the server and creates the database if it doesn't exist.
    """
    db_exists = False
    
    with connection.cursor() as cursor:
        if DB_BACKEND == 'postgres':
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", [DB_NAME])
            db_exists = cursor.fetchone() is not None
            if not db_exists:
                cursor.execute(f"CREATE DATABASE {DB_NAME}")
                print(f"Database '{DB_NAME}' created successfully.")
        elif DB_BACKEND == 'mysql':
            cursor.execute(f"SHOW DATABASES LIKE '{DB_NAME}'")
            db_exists = cursor.fetchone() is not None
            if not db_exists:
                cursor.execute(f"CREATE DATABASE {DB_NAME}")
                print(f"Database '{DB_NAME}' created successfully.")

    if not db_exists:
        print(f"Database '{DB_NAME}' checked/created successfully.")
    else:
        print(f"Database '{DB_NAME}' already exists.")

# Create database if it doesn't exist
create_database_if_not_exists()

# Populate the database with dummy data
def populate_dummy_data():
    Message.objects.all().delete()

    for _ in range(20):
        from_number = get_random_string(length=10, allowed_chars='0123456789')
        message_body = get_random_string(length=50)
        approved = random.choice([True, False])
        created_at = datetime.now()

        Message.objects.create(from_number=from_number, message_body=message_body, approved=approved, created_at=created_at)

    print("Database populated with dummy data.")

# Run the function
populate_dummy_data()
