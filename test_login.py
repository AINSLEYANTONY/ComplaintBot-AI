import sys
import os
import requests
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_login(email, password):
    try:
        # Make a request to the login endpoint
        response = requests.post(
            'http://localhost:5000/api/auth/login',
            json={
                'email': email,
                'password': password
            }
        )
        
        # Print the response
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Login successful!")
            print(f"User: {data['user']['name']}")
            print(f"Role: {data['user']['role']}")
            print(f"Access Token: {data['access_token'][:20]}...")
            return True
        else:
            print(f"Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test login with credentials')
    parser.add_argument('--email', required=True, help='Email to test')
    parser.add_argument('--password', required=True, help='Password to test')
    
    args = parser.parse_args()
    
    test_login(args.email, args.password)