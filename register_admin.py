import sys
import os
import requests
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def register_admin(full_name, email, password):
    try:
        # Make a request to the register endpoint
        response = requests.post(
            'http://localhost:5000/api/auth/register',
            json={
                'full_name': full_name,
                'email': email,
                'password': password,
                'role': 'admin'
            }
        )
        
        # Print the response
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("Registration successful!")
            print(f"User: {data['user']['name']}")
            print(f"Role: {data['user']['role']}")
            print(f"Access Token: {data['access_token'][:20]}...")
            return True
        else:
            print(f"Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Register a new admin user')
    parser.add_argument('--name', required=True, help='Full name')
    parser.add_argument('--email', required=True, help='Email')
    parser.add_argument('--password', required=True, help='Password')
    
    args = parser.parse_args()
    
    register_admin(args.name, args.email, args.password)