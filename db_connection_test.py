import os
import psycopg2

def main():
    """Test database connection with environment variables"""
    
    # Get database connection parameters from environment variables
    db_url = os.environ.get('DATABASE_URL')
    
    # Alternative connection using individual parameters
    db_host = os.environ.get('PGHOST')
    db_port = os.environ.get('PGPORT')
    db_name = os.environ.get('PGDATABASE')
    db_user = os.environ.get('PGUSER')
    db_password = os.environ.get('PGPASSWORD')
    
    # Method 1: Connect using the DATABASE_URL
    try:
        print("Connecting to database using DATABASE_URL...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        db_version = cursor.fetchone()
        print(f"Successfully connected to PostgreSQL database using DATABASE_URL")
        print(f"Database version: {db_version[0]}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting with DATABASE_URL: {e}")
    
    # Method 2: Connect using individual parameters
    try:
        print("\nConnecting to database using individual parameters...")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        db_version = cursor.fetchone()
        print(f"Successfully connected to PostgreSQL database using individual parameters")
        print(f"Database version: {db_version[0]}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting with individual parameters: {e}")
    
    print("\nDatabase connection test complete")

if __name__ == "__main__":
    main()