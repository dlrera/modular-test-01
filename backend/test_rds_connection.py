import os
import psycopg
from pathlib import Path
import environ

# Load environment variables
env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Get database credentials
DB_NAME = env('DB_NAME', default='postgres')
DB_USER = env('DB_USER', default='postgres')
DB_PASSWORD = env('DB_PASSWORD', default='')
DB_HOST = env('DB_HOST', default='localhost')
DB_PORT = env('DB_PORT', default='5432')

print(f"Testing RDS connection...")
print(f"Host: {DB_HOST}")
print(f"Port: {DB_PORT}")
print(f"Database: {DB_NAME}")
print(f"User: {DB_USER}")
print(f"Password: {'*' * len(DB_PASSWORD) if DB_PASSWORD else '(no password set)'}")

if DB_PASSWORD == 'your_rds_password_here':
    print("\nERROR: You need to update the DB_PASSWORD in your .env file!")
    print("Please edit backend/.env and replace 'your_rds_password_here' with your actual RDS password.")
    exit(1)

try:
    # Build connection string
    conn_string = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    
    print(f"\nConnecting to RDS...")
    with psycopg.connect(conn_string) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"Successfully connected to PostgreSQL!")
            print(f"PostgreSQL version: {version[0]}")
            
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()
            print(f"Current database: {db_name[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';")
            table_count = cursor.fetchone()
            print(f"Number of tables in public schema: {table_count[0]}")
            
except Exception as e:
    print(f"\nFailed to connect to database: {str(e)}")
    print("\nPlease check:")
    print("1. Your RDS instance is running")
    print("2. Security group allows connections from your IP")
    print("3. Database credentials are correct in backend/.env")
    print("4. Database name exists on the RDS instance")