import os

def get_db_connection_string():
    """
    Returns the database connection string from environment variables.
    The function first checks for DATABASE_URL, then tries to construct
    the connection string from individual environment variables.
    """
    # First try using the DATABASE_URL environment variable
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Replace postgres:// with postgresql:// if needed
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        return db_url
    
    # If DATABASE_URL is not set, try to construct from individual parameters
    db_host = os.environ.get('PGHOST')
    db_port = os.environ.get('PGPORT')
    db_name = os.environ.get('PGDATABASE')
    db_user = os.environ.get('PGUSER')
    db_password = os.environ.get('PGPASSWORD')
    
    # Ensure all required parameters are available
    if all([db_host, db_port, db_name, db_user, db_password]):
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # If we can't construct a valid connection string, raise an error
    raise ValueError("Database connection parameters are missing. Ensure DATABASE_URL or all individual PostgreSQL environment variables are set.")

def get_db_config():
    """
    Returns a dictionary with all database configuration parameters.
    Useful when individual parameters are needed instead of connection string.
    """
    return {
        'host': os.environ.get('PGHOST'),
        'port': os.environ.get('PGPORT'),
        'dbname': os.environ.get('PGDATABASE'),
        'user': os.environ.get('PGUSER'),
        'password': os.environ.get('PGPASSWORD')
    }