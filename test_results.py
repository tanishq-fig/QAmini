import requests
import json
import time

# Give it a moment to ensure results are ready
time.sleep(1)

# Fetch experiment 2 results
r = requests.get('http://127.0.0.1:8000/api/experiment/exp2')
data = r.json()

print("Experiment exp2 response status:", r.status_code)
print("Response keys:", list(data.keys()))
print("\nHas 'findings'?", 'findings' in data)
print("Has 'summary'?", 'summary' in data)
print("Has 'plots'?", 'plots' in data)
if 'findings' in data:
    print(f"Findings count: {len(data['findings'])}")
    print("First finding:", data['findings'][0] if data['findings'] else "None")

# Test chat endpoint with the data
print("\n--- Testing Chat Endpoint ---")
r2 = requests.post('http://127.0.0.1:8000/api/chat', 
                   json={'question': 'What columns are in the dataset?'})
if r2.ok:
    chat_data = r2.json()
    print("Chat response status:", r2.status_code)
    print("Response keys:", list(chat_data.keys()))
    if 'results' in chat_data and chat_data['results']:
        print("First result:", json.dumps(chat_data['results'][0], indent=2))
else:
    print("Chat error:", r2.status_code, r2.text)
