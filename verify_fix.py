import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def verify():
    print("Waiting for server reload...")
    time.sleep(3)
    
    print(f"Checking {BASE_URL}...")
    try:
        # Check Index
        resp = requests.get(BASE_URL)
        if resp.status_code != 200:
            print(f"Index failed: {resp.status_code}")
            return False
            
        print("Index OK.")
        
        # Check Analyze
        print("Testing Analysis...")
        files = {'file': ('test.txt', 'This is a test of the emergency broadcast system.')}
        resp = requests.post(f"{BASE_URL}/analyze", files=files)
        
        if resp.status_code == 200:
            data = resp.json()
            print("Analysis OK!")
            print(f"Words: {data.get('total_words')}")
            return True
        else:
            print(f"Analysis FAILED: {resp.status_code}")
            print(resp.text)
            return False
            
    except Exception as e:
        print(f"Connection Failed: {e}")
        return False

if __name__ == "__main__":
    verify()
