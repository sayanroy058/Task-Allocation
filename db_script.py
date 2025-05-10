import psycopg2
from db_config import get_db_connection_string, get_db_config

def main():
    """
    Connect to the PostgreSQL database and perform operations.
    """
    # Get database connection string from our config module
    conn_string = get_db_connection_string()
    
    try:
        # Connect to the PostgreSQL database
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(conn_string)
        
        # Create a cursor
        cur = conn.cursor()
        
        # Execute a test query
        print("PostgreSQL database version:")
        cur.execute('SELECT version()')
        
        # Display the result
        db_version = cur.fetchone()
        print(db_version)
        
        # Add your database operations here
        # For example:
        # - Create tables
        # - Insert data
        # - Query data
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        print("Database connection closed.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()