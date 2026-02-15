import requests
import threading
import time
import sys
import os

# Ensure we can import the app
sys.path.append(os.path.abspath("c:/ai job market project"))
from src.api.flask_app import app

def run_server():
    app.run(port=5002)

def test_cors():
    base_url = "http://localhost:5002"
    
    # Wait for server to start
    time.sleep(2)
    
    print("\nTesting CORS Configuration...")
    try:
        # Preflight request simulation with a random origin
        test_origin = 'https://random-deployment.vercel.app'
        headers = {
            'Origin': test_origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        resp = requests.options(f"{base_url}/upload_csv", headers=headers)
        
        allow_origin = resp.headers.get('Access-Control-Allow-Origin')
        
        print(f"Status Code: {resp.status_code}")
        print(f"Access-Control-Allow-Origin: {allow_origin}")
        
        if allow_origin == '*' or allow_origin == test_origin:
            print("SUCCESS: CORS allowed the external origin.")
        else:
            print("FAILURE: CORS blocked the external origin.")
            
    except Exception as e:
        print(f"CORS Test Failed: {e}")

if __name__ == "__main__":
    # Run server in a separate thread
    flask_thread = threading.Thread(target=run_server, daemon=True)
    flask_thread.start()
    
    test_cors()
