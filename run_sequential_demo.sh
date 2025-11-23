#!/bin/bash
# Sequential Demo Script
# Run this script to demonstrate the pipeline step by step

echo "============================================================"
echo "  REAL ESTATE PIPELINE - SEQUENTIAL DEMONSTRATION"
echo "============================================================"
echo ""

# Step 0: Clear Databases (Optional - uncomment to clear before demo)
# echo "STEP 0: Clearing previous data..."
# echo "yes" | python clear_databases.py
# echo ""

# Step 1: Check PostgreSQL
echo "STEP 1: Checking PostgreSQL..."
docker ps | grep postgres > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL is running"
else
    echo "⚠️  Starting PostgreSQL..."
    docker-compose up -d
    sleep 5
fi
echo ""

# Step 2: Initialize Database
echo "STEP 2: Initializing Database..."
python -c "
from database.postgres_client import PostgreSQLClient
from pathlib import Path
client = PostgreSQLClient()
client.create_tables()
print('✅ Database tables created')
"
echo ""

# Step 3: Run Pipeline
echo "STEP 3: Running Pipeline..."
echo "This will process all PDF documents..."
echo ""
PREFECT_API_URL="" python run_pipeline.py
echo ""

# Step 4: View Outputs
echo "STEP 4: Viewing Outputs..."
echo ""
python view_outputs.py
echo ""

# Step 5: Start Django Server
echo "STEP 5: Starting Django Server..."
echo "Dashboard will be available at: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""
python manage.py runserver

