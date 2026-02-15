import requests
import pandas as pd
import io
import threading
import time
import sys
import os

# Ensure we can import the app
sys.path.append(os.path.abspath("c:/ai job market project"))
from src.api.flask_app import app

def run_server():
    app.run(port=5001)

def test_endpoints():
    base_url = "http://localhost:5001"
    
    # Wait for server to start
    time.sleep(2)
    
    # 1. Test Health Check
    try:
        resp = requests.get(f"{base_url}/")
        print(f"Health Check: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return

    # 2. Test CSV Upload
    print("\nTesting CSV Upload...")
    csv_content = """role,salary,skills,experience
Data Scientist,15,Python|SQL,2 years
Software Engineer,12,Java|React,3 years
"""
    files = {'file': ('test.csv', csv_content, 'text/csv')}
    try:
        resp = requests.post(f"{base_url}/upload_csv", files=files)
        print(f"Upload Status: {resp.status_code}")
        print(f"Upload Response: {resp.text}")
    except Exception as e:
        print(f"Upload Failed: {e}")

    # 3. Test Market Data
    print("\nTesting Market Data Analysis...")
    try:
        resp = requests.get(f"{base_url}/market_data")
        print(f"Market Data Status: {resp.status_code}")
        # Print first few chars to avoid spam
        print(f"Market Data Response: {resp.text[:200]}...")
    except Exception as e:
        print(f"Market Data Failed: {e}")

if __name__ == "__main__":
    # Run server in a separate thread
    flask_thread = threading.Thread(target=run_server, daemon=True)
    flask_thread.start()
    
    test_endpoints()
