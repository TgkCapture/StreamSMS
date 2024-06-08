import os
import django
import mysql.connector
from mysql.connector import errorcode
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

def connect_to_mysql_server():
    """
    Attempts to connect to the MySQL server.
    """
    try:
        cnx = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cursor = cnx.cursor()
        print("Connected to MySQL server.")
        return cnx, cursor
    except mysql.connector.Error as err:
        print(err)
        return None, None

def create_database(cnx, cursor):
    """
    Creates the database
    """
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        print(f"Database '{DB_NAME}' checked/created successfully.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def connect_to_database():
    """
    Connects to the MySQL server and database, creating the database if it doesn't exist.
    """
    cnx, cursor = connect_to_mysql_server()
    if cnx and cursor:
        try:
            cnx.database = DB_NAME
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"Database '{DB_NAME}' does not exist. Creating it...")
                create_database(cnx, cursor)
                cnx.database = DB_NAME
            else:
                print(err)
                return None, None
        print(f"Connected to database '{DB_NAME}'.")
        return cnx, cursor
    return None, None

# Connect to the database
cnx, cursor = connect_to_database()

if cnx is None or cursor is None:
    print("Failed to connect to MySQL server or create database. Exiting.")
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

# Close the cursor and connection
cursor.close()
cnx.close()
