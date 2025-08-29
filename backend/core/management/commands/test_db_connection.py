from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import sys


class Command(BaseCommand):
    help = 'Test database connection to RDS'

    def handle(self, *args, **options):
        self.stdout.write('Testing database connection...')
        self.stdout.write(f'Database settings:')
        self.stdout.write(f'  Host: {settings.DATABASES["default"]["HOST"]}')
        self.stdout.write(f'  Port: {settings.DATABASES["default"]["PORT"]}')
        self.stdout.write(f'  Database: {settings.DATABASES["default"]["NAME"]}')
        self.stdout.write(f'  User: {settings.DATABASES["default"]["USER"]}')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Successfully connected to PostgreSQL!')
                )
                self.stdout.write(f'  PostgreSQL version: {version[0]}')
                
                cursor.execute("SELECT current_database();")
                db_name = cursor.fetchone()
                self.stdout.write(f'  Current database: {db_name[0]}')
                
                cursor.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';")
                table_count = cursor.fetchone()
                self.stdout.write(f'  Number of tables in public schema: {table_count[0]}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to connect to database: {str(e)}')
            )
            self.stdout.write(
                self.style.WARNING('\nPlease check your .env file and ensure:')
            )
            self.stdout.write('  1. Your RDS instance is running')
            self.stdout.write('  2. Security group allows connections from your IP')
            self.stdout.write('  3. Database credentials are correct')
            self.stdout.write('  4. Database name exists on the RDS instance')
            sys.exit(1)