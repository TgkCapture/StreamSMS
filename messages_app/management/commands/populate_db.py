import os
import django
import psycopg2
from psycopg2 import sql, OperationalError
from datetime import datetime
import random
from django.utils.crypto import get_random_string

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StreamSMS.settings")
django.setup()

from messages_app.models import Message

# Database configuration
DB_NAME = os.environ.get('DATABASE_NAME')
DB_USER = os.environ.get('DATABASE_USER')
DB_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DB_HOST = os.environ.get('DATABASE_HOST')
DB_PORT = os.environ.get('DATABASE_PORT')

def connect_to_postgresql_server():
    """
    Attempts to connect to the PostgreSQL server.
    """
    try:
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        print("Connected to PostgreSQL server.")
        return conn
    except OperationalError as err:
        print(err)
        return None

def create_database(conn):
    """
    Creates the database.
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            conn.commit()
            print(f"Database '{DB_NAME}' checked/created successfully.")
    except OperationalError as err:
        print(f"Failed creating database: {err}")
        exit(1)

def connect_to_database():
    """
    Connects to the PostgreSQL server and database, creating the database if it doesn't exist.
    """
    conn = connect_to_postgresql_server()
    if conn:
        try:
            conn.autocommit = True  # Enable autocommit mode
            conn.set_isolation_level(0)  # Set isolation level to AUTOCOMMIT
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
                if cursor.fetchone() is None:
                    print(f"Database '{DB_NAME}' does not exist. Creating it...")
                    create_database(conn)
        except OperationalError as err:
            print(err)
            return None
        conn.set_isolation_level(1)  # Reset to default isolation level
        print(f"Connected to database '{DB_NAME}'.")
        return conn
    return None

# Connect to the database
conn = connect_to_database()

if conn is None:
    print("Failed to connect to PostgreSQL server or create database. Exiting.")
    exit(1)

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

# Close the connection
conn.close()
