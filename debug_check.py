import requests
import os
import time

BASE_URL = "http://127.0.0.1:5000"

def check_server():
    print(f"Checking {BASE_URL}...")
    try:
        response = requests.get(BASE_URL)
        print(f"Server Status: {response.status_code}")
        if response.status_code == 200:
            print("Server is UP and serving index.html")
            return True
        else:
            print("Server returned unexpected status.")
            return False
    except requests.exceptions.ConnectionError:
        print("Server is DOWN. Is python app.py running?")
        return False

def check_analysis():
    print("\nChecking /analyze endpoint...")
    # Create a dummy file
    files = {'file': ('test.txt', 'Hello world. This is a test. Hello Flask.')}
    try:
        response = requests.post(f"{BASE_URL}/analyze", files=files)
        if response.status_code == 200:
            print("Analysis Success!")
            print(response.json())
            return True
        else:
            print(f"Analysis Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Analysis Error: {e}")
        return False

def reset_db():
    print("\nAttempting to reset DB to fix schema headers...")
    db_path = "analytics.db"
    try:
        if os.path.exists(db_path):
            # We can't delete it if it's locked by the running server process usually on Windows
            # But we can try.
            os.remove(db_path)
            print("analytics.db deleted.")
        else:
            print("analytics.db does not exist.")
    except PermissionError:
        print("Could not delete analytics.db - it is likely locked by the running server.")
        print("PLEASE STOP the 'python app.py' server in your terminal (Ctrl+C) and run it again.")

if __name__ == "__main__":
    if check_server():
        check_analysis()
    else:
        print("Skipping analysis check as server is down.")
        
    reset_db()
