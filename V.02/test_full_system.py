"""
Comprehensive system validation script for Word-Count-Analyzer
Tests all endpoints and basic functionality
"""
import requests
import json
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:5000"

def test_home_page():
    """Test that home page loads"""
    print("✓ Testing home page...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200, "Home page failed to load"
    assert "Word Intelligence" in response.text, "Dashboard title not found"
    print("  ✓ Home page loads successfully")

def test_file_upload():
    """Test file upload and analysis"""
    print("\n✓ Testing file upload...")
    test_file = Path("uploads/sample1.txt")
    
    if not test_file.exists():
        # Create a test file
        os.makedirs("uploads", exist_ok=True)
        with open(test_file, "w") as f:
            f.write("This is a test file for word analysis. Test words appear multiple times. Analysis test complete.")
    
    with open(test_file, "rb") as f:
        files = {"file": f}
        data = {"stopwords": "is,a,for"}
        response = requests.post(f"{BASE_URL}/analyze", files=files, data=data)
    
    assert response.status_code == 200, f"Upload failed: {response.text}"
    result = response.json()
    assert "top_words" in result, "Missing top_words in response"
    assert "total_words" in result, "Missing total_words in response"
    assert result["total_words"] > 0, "No words analyzed"
    print(f"  ✓ File uploaded successfully - {result['total_words']} words analyzed")
    return result

def test_url_analysis():
    """Test URL analysis (using a simple text URL)"""
    print("\n✓ Testing URL analysis...")
    # Using example.com as it's always available
    data = {
        "url": "http://example.com",
        "stopwords": "the,a,an"
    }
    response = requests.post(f"{BASE_URL}/analyze_url", data=data)
    
    assert response.status_code == 200, f"URL analysis failed: {response.text}"
    result = response.json()
    assert "top_words" in result, "Missing top_words in response"
    print(f"  ✓ URL analyzed successfully - {result.get('total_words', 0)} words found")

def test_history_api():
    """Test history API endpoints"""
    print("\n✓ Testing history API...")
    response = requests.get(f"{BASE_URL}/api/history")
    assert response.status_code == 200, "History API failed"
    history = response.json()
    assert isinstance(history, list), "History should return a list"
    print(f"  ✓ History API working - {len(history)} records found")
    return history

def test_spark_status():
    """Test Spark status endpoint"""
    print("\n✓ Testing Spark status...")
    response = requests.get(f"{BASE_URL}/api/spark/status")
    assert response.status_code == 200, "Spark status failed"
    status = response.json()
    assert "active" in status, "Missing active field in Spark status"
    print(f"  ✓ Spark status API working - Active: {status['active']}")

def test_csv_download():
    """Test CSV download functionality"""
    print("\n✓ Testing CSV download...")
    # First check if any analysis CSV exists
    csv_files = list(Path("uploads").glob("*_analysis.csv"))
    if csv_files:
        csv_name = csv_files[0].name
        response = requests.get(f"{BASE_URL}/download/{csv_name}")
        assert response.status_code == 200, "CSV download failed"
        print(f"  ✓ CSV download working - {csv_name}")
    else:
        print("  ⚠ No CSV files found to test download")

def test_history_delete():
    """Test history record deletion"""
    print("\n✓ Testing history deletion...")
    history = test_history_api()
    if len(history) > 0:
        # Try to delete the first record
        record_id = history[0]["id"]
        response = requests.delete(f"{BASE_URL}/api/history/{record_id}")
        assert response.status_code == 200, "History deletion failed"
        result = response.json()
        assert result.get("success"), "Deletion not successful"
        print(f"  ✓ History deletion working - Deleted record {record_id}")
    else:
        print("  ⚠ No history records to test deletion")

def run_all_tests():
    """Run all validation tests"""
    print("=" * 60)
    print("COMPREHENSIVE SYSTEM VALIDATION")
    print("=" * 60)
    
    try:
        test_home_page()
        test_file_upload()
        test_url_analysis()
        test_history_api()
        test_spark_status()
        test_csv_download()
        test_history_delete()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED - SYSTEM IS FULLY FUNCTIONAL")
        print("=" * 60)
        
        print("\n📋 MANUAL VERIFICATION CHECKLIST:")
        print("  1. Open http://127.0.0.1:5000")
        print("  2. Verify Dashboard tab shows by default")
        print("  3. Click 'Upload File' button → Modal opens")
        print("  4. Upload a file → Analysis completes → Charts appear")
        print("  5. Check History tab → Click 'View' (👁️) button → Details modal opens")
        print("  6. Click 'Spark UI' in sidebar → Spark UI tab displays")
        print("  7. Verify no UI freeze during analysis")
        print("  8. Check loading animation appears ONLY in graph section")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except requests.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server at http://127.0.0.1:5000")
        print("   Make sure the Flask server is running: python app.py")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
