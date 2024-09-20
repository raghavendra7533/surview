import json
import os

print("Current working directory:", os.getcwd())
try:
    with open('surviews.json', 'r') as f:
        content = json.load(f)
    print("surviews.json contents:", json.dumps(content, indent=2))
except Exception as e:
    print(f"Error reading surviews.json: {str(e)}")