import requests
import time
import threading

BASE_URL = "http://127.0.0.1:5000"

def test_endpoints():
    print("Running Full System Check...")
    
    # 1. Index
    try:
        r = requests.get(BASE_URL)
        assert r.status_code == 200, "Index failed"
        print("✅ Frontend (Index) Reachable")
    except Exception as e:
        print(f"❌ Frontend Unreachable: {e}")
        return

    # 2. Text Analysis
    try:
        files = {'file': ('test.txt', 'This is a test file for verification.')}
        r = requests.post(f"{BASE_URL}/analyze", files=files)
        assert r.status_code == 200, f"Analyze failed: {r.status_code}"
        data = r.json()
        assert data['total_words'] == 7, f"Wrong word count: {data['total_words']}"
        print("✅ Text Analysis Working")
    except Exception as e:
        print(f"❌ Text Analysis Failed: {e}")

    # 3. URL Analysis
    try:
        # We can't really test a real URL without internet, but we can test the validator
        r = requests.post(f"{BASE_URL}/analyze_url", data={'url': 'invalid_url'})
        # Should fail gracefully
        assert r.status_code == 500 or 'error' in r.text, "Should handle invalid URL"
        print("✅ URL Analysis Validator Working")
    except Exception as e:
        print(f"❌ URL Analysis Logic Failed: {e}")

    # 4. History
    try:
        r = requests.get(f"{BASE_URL}/api/history")
        assert r.status_code == 200, "History failed"
        print("✅ History API Reachable")
    except Exception as e:
        print(f"❌ History API Failed: {e}")

    # 5. Spark Simulation
    try:
        r = requests.post(f"{BASE_URL}/api/spark/start")
        assert r.status_code == 200, "Start Spark failed"
        print("✅ Spark Job Started")
        
        # Poll for a bit
        time.sleep(2)
        r = requests.get(f"{BASE_URL}/api/spark/status")
        state = r.json()
        print(f"✅ Spark Status: {state['status']} (Progress: {state['progress']}%)")
        assert state['status'] == 'running', "Spark should be running"
        assert state['progress'] > 0, "Progress should be increasing"
        
    except Exception as e:
        print(f"❌ Spark Simulation Failed: {e}")

if __name__ == "__main__":
    test_endpoints()
