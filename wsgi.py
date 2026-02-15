import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.api.flask_app import app
except Exception as e:
    print(f"Failed to import app: {e}")
    raise

if __name__ == "__main__":
    app.run()
