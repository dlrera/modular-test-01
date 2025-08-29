# Setup Instructions

## PostgreSQL Client (psql) is now installed!
✓ PostgreSQL 16.4 client tools are installed
✓ psql is available at: C:\Program Files\PostgreSQL\16\bin\psql.exe

## Next Steps:

### 1. Update RDS Credentials
Edit the file `backend/.env` and replace the placeholder values with your actual RDS credentials:

```
DB_NAME=your_actual_database_name
DB_USER=your_actual_rds_username
DB_PASSWORD=your_actual_rds_password
DB_HOST=your-actual-endpoint.region.rds.amazonaws.com
DB_PORT=5432
```

### 2. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Test RDS Connection
Once you've updated the .env file:
```bash
cd backend
python manage.py test_db_connection
```

### 4. Run Migrations (after successful connection)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin Account
```bash
python manage.py createsuperuser
```

## Alternative: Using psql directly
You can also test your RDS connection with psql:
```bash
psql -h your-endpoint.region.rds.amazonaws.com -U your_username -d your_database -p 5432
```

## Troubleshooting
- If connection fails, check your RDS security group
- Ensure your IP is whitelisted
- Verify RDS is publicly accessible (if connecting from local)