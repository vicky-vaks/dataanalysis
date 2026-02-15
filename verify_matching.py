import requests
import json

url = "http://127.0.0.1:8000/match_candidates"
payload = {
    "required_skills": ["Python", "SQL"],
    "experience_level": "Mid-level"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
