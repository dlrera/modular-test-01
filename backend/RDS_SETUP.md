# AWS RDS Setup Instructions

## Prerequisites
- AWS account with RDS access
- PostgreSQL RDS instance created
- Security group configured to allow connections from your IP

## Step 1: Update .env File

Edit the `backend/.env` file with your RDS credentials:

```env
DB_NAME=your_database_name
DB_USER=your_rds_master_username
DB_PASSWORD=your_rds_master_password
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_PORT=5432
```

### Finding Your RDS Details:
1. Go to AWS RDS Console
2. Select your database instance
3. Find the endpoint under "Connectivity & security"
4. Master username is under "Configuration"

## Step 2: Configure Security Group

Ensure your RDS security group allows inbound PostgreSQL traffic:
1. Go to your RDS instance in AWS Console
2. Click on the VPC security group
3. Edit inbound rules
4. Add rule: Type: PostgreSQL, Port: 5432, Source: Your IP address

## Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 4: Test Connection

```bash
python manage.py test_db_connection
```

If successful, you'll see:
- ✓ Successfully connected to PostgreSQL!
- PostgreSQL version
- Current database name
- Number of tables

## Step 5: Run Migrations

Once connected, create the database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

## Troubleshooting

### Connection Timeout
- Check security group allows your IP
- Verify RDS instance is publicly accessible (if connecting from local)
- Check VPC and subnet configuration

### Authentication Failed
- Verify username and password
- Ensure database name exists
- Check if using master credentials or IAM authentication

### SSL/TLS Issues
If your RDS requires SSL, add to settings.py:
```python
DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require',
}
```

## Security Best Practices
1. Never commit `.env` file to version control
2. Use IAM database authentication for production
3. Restrict security group to specific IPs
4. Enable encryption at rest and in transit
5. Regular automated backups
6. Use read replicas for scaling