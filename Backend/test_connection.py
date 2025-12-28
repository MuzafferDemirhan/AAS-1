"""Test PostgreSQL connection and create database if needed"""
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

load_dotenv(encoding='utf-8')

DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'attendance_db')

print("Testing PostgreSQL connection...")
print(f"Host: {DB_HOST}")
print(f"Port: {DB_PORT}")
print(f"User: {DB_USER}")
print(f"Database: {DB_NAME}")

try:
    # First, connect to the default 'postgres' database to check if our database exists
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database='postgres'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("\n✓ Successfully connected to PostgreSQL server!")
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    exists = cursor.fetchone()
    
    if not exists:
        print(f"\nDatabase '{DB_NAME}' does not exist. Creating it...")
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print(f"✓ Database '{DB_NAME}' created successfully!")
    else:
        print(f"\n✓ Database '{DB_NAME}' already exists!")
    
    cursor.close()
    conn.close()
    
    # Now test connection to our database
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    print(f"✓ Successfully connected to '{DB_NAME}' database!")
    conn.close()
    
    print("\n✅ All checks passed! Your database is ready.")
    print("You can now run: python Backend/main.py")
    
except psycopg2.OperationalError as e:
    print(f"\n❌ Connection failed: {e}")
    print("\nPlease verify in pgAdmin 4:")
    print("1. PostgreSQL server is running")
    print("2. Username and password are correct")
    print("3. Port 5432 is correct")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
