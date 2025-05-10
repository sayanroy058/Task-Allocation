import os
import re

def load_env(env_file='.env'):
    """Load environment variables from a .env file

    Args:
        env_file (str, optional): Path to the .env file. Defaults to '.env'.
    
    Returns:
        dict: Dictionary of environment variables loaded
    """
    if not os.path.exists(env_file):
        print(f"Warning: Environment file {env_file} does not exist.")
        return {}
    
    loaded_vars = {}
    
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            # Skip empty lines or comments
            if not line or line.startswith('#'):
                continue
                
            # Parse variable definitions (KEY=VALUE)
            match = re.match(r'^([A-Za-z0-9_]+)=(.*)$', line)
            if match:
                key, value = match.groups()
                # Strip quotes if present
                value = re.sub(r'^["\']|["\']$', '', value)
                os.environ[key] = value
                loaded_vars[key] = value
    
    return loaded_vars

if __name__ == "__main__":
    # Load environment variables
    loaded = load_env()
    
    # Print the loaded variables (without showing the actual values for security)
    if loaded:
        print(f"Successfully loaded {len(loaded)} environment variables:")
        for key in loaded:
            # Show just the first few characters of sensitive values
            value = loaded[key]
            if any(secret in key.lower() for secret in ['password', 'secret', 'key', 'token']):
                # For sensitive values, show only a hint
                value = value[:3] + '****' if len(value) > 3 else '****'
            print(f"  - {key}={value}")
    else:
        print("No environment variables were loaded.")