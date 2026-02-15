import subprocess
import os
import sys
import threading
import time
import webbrowser

def run_backend():
    print("🚀 Starting Flask Backend on port 5000...")
    # Use python directly to avoid path issues
    cmd = [sys.executable, "src/api/flask_app.py"]
    subprocess.run(cmd, check=True)

def run_frontend():
    print("🎨 Starting React Frontend...")
    # Change directory to frontend and run dev script
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    # Use shell=True for npm commands on Windows
    subprocess.run("npm run dev", cwd=frontend_dir, shell=True, check=True)

if __name__ == "__main__":
    print("🌟 AI Job Market - Local Launcher 🌟")
    print("-----------------------------------")
    
    # Start Backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Give backend a moment to init
    time.sleep(2)
    
    # Start Frontend
    # Frontend (npm) is interactive/blocking usually, so we run it in main thread or separate
    # Actually, npm run dev blocks, so we should run it here.
    
    print("\n✅ Backend is running in background.")
    print("✅ Frontend is starting... (Press Ctrl+C to stop)")
    print("👉 Once ready, open: http://localhost:5173\n")
    
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\nStopping...")
