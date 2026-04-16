import requests
import time

# Upload the community.csv file
with open('community.csv', 'rb') as f:
    files = {'file': f}
    r = requests.post('http://127.0.0.1:8000/api/upload', files=files)
    print("Upload Response:", r.json())

# Wait a bit for analysis to start
time.sleep(3)

# Check status
r = requests.get('http://127.0.0.1:8000/api/status')
status = r.json()
print("\nStatus:")
print(f"  Phase: {status['phase']}")
print(f"  Experiments: {status['total_experiments']}")
print(f"  Completed: {status['completed']}")
print(f"  QA Pairs: {status['qa_pairs_count']}")

# Print experiment list
print("\nExperiments:")
for exp in status.get('experiments', []):
    print(f"  - {exp['id']}: {exp['name']} ({exp['status']})")
