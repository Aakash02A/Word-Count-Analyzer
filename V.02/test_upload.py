import requests

# Test file upload
url = 'http://127.0.0.1:5000/analyze'
files = {'file': open('uploads/sample3.txt', 'rb')}
data = {'stopwords': 'the,and,or,is,at,in,on'}

response = requests.post(url, files=files, data=data)
print("Status Code:", response.status_code)
print("Response:", response.json())

# Test history API
history_url = 'http://127.0.0.1:5000/api/history'
history_response = requests.get(history_url)
print("\nHistory Count:", len(history_response.json()))
print("Latest Record:", history_response.json()[-1].get('filename'))
