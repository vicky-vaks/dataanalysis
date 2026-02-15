import sys
import os
sys.path.append(os.getcwd())
from src.api.flask_app import app
import json

client = app.test_client()

def test_prediction():
    print("Testing /predict_salary endpoint...")
    data = {
        "role": "Data Scientist",
        "location": "Bangalore, India",
        "experience_years": 5,
        "skills": ["Python", "Machine Learning"]
    }
    
    response = client.post('/predict_salary', json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.get_json()}")
    
    if response.status_code == 200 and "predicted_salary" in response.get_json():
        print("SUCCESS: Prediction returned.")
    else:
        print("FAILURE: Prediction failed.")

    # Test unknown attributes handling
    print("\nTesting Unknown Role/Location...")
    data_unknown = {
        "role": "Super Unique Role 123",
        "location": "Moon Base",
        "experience_years": 5,
        "skills": ["Telepathy"]
    }
    response_unknown = client.post('/predict_salary', json=data_unknown)
    print(f"Status Code: {response_unknown.status_code}")
    print(f"Response: {response_unknown.get_json()}")

if __name__ == "__main__":
    test_prediction()
