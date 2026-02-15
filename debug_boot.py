import sys
import os

print(f"Python Version: {sys.version}")
print(f"Current Directory: {os.getcwd()}")
print(f"Directory Contents: {os.listdir('.')}")
print(f"Src Contents: {os.listdir('src') if os.path.exists('src') else 'SRC NOT FOUND'}")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Attempting to import src.api.flask_app...")
try:
    from src.api.flask_app import app
    print("SUCCESS: Imported app successfully.")
except Exception as e:
    print(f"FAILURE: Could not import app. Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Starting app with internal server (bypass gunicorn)...")
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
