# apps/messages_app/management/commands/populate_messages.py
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from django.db import connection
from datetime import datetime, timedelta
from faker import Faker
import random
import argparse

from apps.messages_app.models import Message

class Command(BaseCommand):
    help = 'Populates the database with realistic test messages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=200,
            help='Number of messages to create (default: 200)'
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Skip confirmation prompt'
        )
        parser.add_argument(
            '--create-db',
            action='store_true',
            help='Create database if it doesn\'t exist'
        )

    def handle(self, *args, **options):
        fake = Faker()
        count = options['count']
        noinput = options['noinput']
        create_db = options['create_db']

        if create_db:
            self.create_database_if_not_exists()

        if not noinput and not self.clear_existing_data():
            return

        self.stdout.write(self.style.SUCCESS(f'Generating {count} realistic test messages...'))
        messages = self.generate_realistic_messages(fake, count)
        
        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
        self.print_statistics()

    def create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        self.stdout.write('Checking database existence...')
        db_exists = False
        
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                cursor.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s", 
                    [connection.settings_dict['NAME']]
                )
                db_exists = cursor.fetchone() is not None
                if not db_exists:
                    cursor.execute(f"CREATE DATABASE {connection.settings_dict['NAME']}")
            elif connection.vendor == 'mysql':
                cursor.execute(
                    f"SHOW DATABASES LIKE '{connection.settings_dict['NAME']}'"
                )
                db_exists = cursor.fetchone() is not None
                if not db_exists:
                    cursor.execute(f"CREATE DATABASE {connection.settings_dict['NAME']}")

        if db_exists:
            self.stdout.write(self.style.SUCCESS('Database already exists'))
        else:
            self.stdout.write(self.style.SUCCESS('Database created successfully'))

    def generate_phone_number(self):
        """Generate realistic phone numbers"""
        return f"+{random.randint(1, 99)}{random.randint(100000000, 999999999)}"

    def generate_message_status(self):
        """Generate random status with weighted distribution"""
        rand = random.random()
        if rand < 0.6:  # 60% pending
            return (False, False)
        elif rand < 0.8:  # 20% approved
            return (True, False)
        else:  # 20% declined
            return (False, True)

    def generate_realistic_messages(self, fake, count):
        """Generate realistic SMS-like messages"""
        messages = []
        base_time = datetime.now() - timedelta(days=30)
        
        for i in range(count):
            # Create messages with increasing timestamps
            created_at = base_time + timedelta(
                hours=i,
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            
            approved, declined = self.generate_message_status()
            
            messages.append(Message(
                from_number=self.generate_phone_number(),
                message_body=fake.sentence(nb_words=random.randint(5, 20)),
                approved=approved,
                declined=declined,
                created_at=created_at
            ))
            
            if len(messages) % 100 == 0:
                Message.objects.bulk_create(messages)
                messages = []
                self.stdout.write(f'Created {i+1} messages...', ending='\r')
        
        if messages:  
            Message.objects.bulk_create(messages)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} messages'))

    def clear_existing_data(self):
        """Clear existing data with confirmation"""
        if Message.objects.exists():
            confirm = input(
                self.style.WARNING('This will delete ALL existing messages. Continue? (y/n): ')
            )
            if confirm.lower() != 'y':
                self.stdout.write(self.style.NOTICE('Operation cancelled.'))
                return False
            
            Message.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All existing messages deleted.'))
        
        return True

    def print_statistics(self):
        """Print statistics about the generated data"""
        total = Message.objects.count()
        pending = Message.objects.filter(approved=False, declined=False).count()
        approved = Message.objects.filter(approved=True).count()
        declined = Message.objects.filter(declined=True).count()
        
        self.stdout.write('\nMessage Statistics:')
        self.stdout.write(f'{"Total messages:":<20} {self.style.SUCCESS(total)}')
        self.stdout.write(f'{"Pending moderation:":<20} {self.style.WARNING(pending)}')
        self.stdout.write(f'{"Approved messages:":<20} {self.style.SUCCESS(approved)}')
        self.stdout.write(f'{"Declined messages:":<20} {self.style.ERROR(declined)}')