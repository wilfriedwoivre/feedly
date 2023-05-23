import os
import ssl
import requests
from requests_oauthlib import OAuth1
import json

def run():
    repository = os.getenv("GithubRepository")
    token = os.getenv("GithubToken")
    twitterConsumerKey = os.getenv("TwitterConsumerKey")
    twitterConsumerSecret = os.getenv("TwitterConsumerSecret")
    twitterAccessTokenKey = os.getenv("TwitterAccessTokenKey")
    twitterAccessTokenSecret = os.getenv("TwitterAccessTokenSecret")
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    r = requests.get(f'https://api.github.com/repos/{repository}/issues?labels=publish&state=open&per_page=1', headers=headers)

    issues = json.loads(r.text)

    for item in issues:
        issueNumber = item['number']

        title = item['title']
        link = item['body']
        
        url = 'https://api.twitter.com/2/tweets'
        auth = OAuth1(twitterConsumerKey, twitterConsumerSecret, twitterAccessTokenKey, twitterAccessTokenSecret)
        data = { 'text': f'{title} {link}'}
        requests.post(url, auth=auth, json=data)

        requests.patch(f'https://api.github.com/repos/{repository}/issues/{issueNumber}', headers=headers, json={"state": "closed"})
        
        
if __name__ == "__main__":
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    run()
