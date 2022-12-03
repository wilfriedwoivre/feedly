import os
import ssl
import requests
import json

def run():
    repository = os.getenv("GithubRepository")
    token = os.getenv("GithubToken")
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    r = requests.get(f'https://api.github.com/repos/{repository}/issues?labels=ignore&state=open', headers=headers)

    issues = json.loads(r.text)

    for item in issues:
        issueNumber = item['number']
        requests.patch(f'https://api.github.com/repos/{repository}/issues/{issueNumber}', headers=headers, json={"state": "closed"})
        
if __name__ == "__main__":
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    run()
