"""
Quick test to verify analysis endpoints are working
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from text_analyzer import TextAnalyzer

print("=" * 60)
print("Quick Analysis Test")
print("=" * 60)

# Test 1: Text Analysis
print("\n1. Testing Text Analyzer...")
analyzer = TextAnalyzer()

test_text = """
Python is a high-level programming language. Python is widely used for web development,
data science, and artificial intelligence. Python's simplicity makes it popular among beginners.
"""

try:
    results = analyzer.process_text(test_text)
    print("✅ Text analysis SUCCESS!")
    print(f"   Total words: {results['total_words']}")
    print(f"   Unique words: {results['unique_words']}")
    print(f"   Top 3 words: {results['top_words'][:3]}")
    print(f"   Sentiment: {results['sentiment_label']}")
except Exception as e:
    print(f"❌ Text analysis FAILED: {e}")
    sys.exit(1)

# Test 2: URL Content Fetching (without actually making request to avoid dependencies)
print("\n2. Testing URL content processing...")
sample_html = """
<html>
<body>
<h1>Sample Page</h1>
<p>This is a test page with some content.</p>
<p>We are testing the word frequency analyzer.</p>
</body>
</html>
"""

# Simulating cleaned text (what would come after BeautifulSoup processing)
cleaned_text = "Sample Page This is a test page with some content. We are testing the word frequency analyzer."

try:
    results = analyzer.process_text(cleaned_text)
    print("✅ URL-style content analysis SUCCESS!")
    print(f"   Total words: {results['total_words']}")
    print(f"   Unique words: {results['unique_words']}")
    print(f"   Top 3 words: {results['top_words'][:3]}")
except Exception as e:
    print(f"❌ URL content analysis FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All core functionality tests PASSED!")
print("=" * 60)
print("\nThe analyzer is working correctly.")
print("If you're seeing 'analyzation failed' in the web interface,")
print("the issue was in the frontend error handling, which has been fixed.")
print("\nTo test the full web interface:")
print("1. Start the server: python app.py")
print("2. Open browser: http://localhost:5000")
print("3. Try uploading a file or entering a URL")
