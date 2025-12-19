"""
Test script to verify file and URL analysis functionality
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_file_analysis():
    """Test file upload and analysis"""
    print("\n=== Testing File Analysis ===")
    
    # Create a test file
    test_content = """
    This is a test document for analyzing word frequencies.
    The analyzer should count all words and provide meaningful statistics.
    Testing testing one two three.
    """
    
    with open('test_temp.txt', 'w') as f:
        f.write(test_content)
    
    try:
        with open('test_temp.txt', 'rb') as f:
            files = {'file': ('test_temp.txt', f, 'text/plain')}
            response = requests.post(f"{BASE_URL}/analyze", files=files)
            
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ File Analysis SUCCESS!")
            print(f"Total Words: {data.get('total_words', 'N/A')}")
            print(f"Unique Words: {data.get('unique_words', 'N/A')}")
            print(f"Top 5 Words: {data.get('top_words', [])[:5]}")
            print(f"Sentiment: {data.get('sentiment_label', 'N/A')}")
            return True
        else:
            print("❌ File Analysis FAILED!")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception during file analysis: {e}")
        return False
    finally:
        import os
        if os.path.exists('test_temp.txt'):
            os.remove('test_temp.txt')

def test_url_analysis():
    """Test URL analysis"""
    print("\n=== Testing URL Analysis ===")
    
    # Use a simple, reliable URL
    test_url = "https://example.com"
    
    try:
        data = {'url': test_url}
        response = requests.post(f"{BASE_URL}/analyze_url", data=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ URL Analysis SUCCESS!")
            print(f"Total Words: {data.get('total_words', 'N/A')}")
            print(f"Unique Words: {data.get('unique_words', 'N/A')}")
            print(f"Top 5 Words: {data.get('top_words', [])[:5]}")
            print(f"Sentiment: {data.get('sentiment_label', 'N/A')}")
            return True
        else:
            print("❌ URL Analysis FAILED!")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception during URL analysis: {e}")
        return False

def test_endpoints():
    """Test if server is responding"""
    print("\n=== Testing Server Status ===")
    
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Server is running!")
            return True
        else:
            print(f"⚠ Server returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Word Count Analyzer - Test Suite")
    print("=" * 60)
    
    # Test server
    if not test_endpoints():
        print("\n⚠ Server is not running. Please start it with: python app.py")
        exit(1)
    
    # Run tests
    results = {
        'file_analysis': test_file_analysis(),
        'url_analysis': test_url_analysis()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results.values())
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed!")
        exit(0)
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        exit(1)
