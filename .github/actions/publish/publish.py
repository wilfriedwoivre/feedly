import os
import ssl
import requests
from requests_oauthlib import OAuth1
import json
from datetime import datetime, timezone

def run():
    repository = os.getenv("GithubRepository")
    token = os.getenv("GithubToken")
    twitterConsumerKey = os.getenv("TwitterConsumerKey")
    twitterConsumerSecret = os.getenv("TwitterConsumerSecret")
    twitterAccessTokenKey = os.getenv("TwitterAccessTokenKey")
    twitterAccessTokenSecret = os.getenv("TwitterAccessTokenSecret")
    blueSkyAppNameCode = os.getenv("BlueSkyAppNameCode")
    blueSkyHandle = os.getenv("BlueSkyHandle")
    
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
        
        # Twitter
        url = 'https://api.twitter.com/2/tweets'
        auth = OAuth1(twitterConsumerKey, twitterConsumerSecret, twitterAccessTokenKey, twitterAccessTokenSecret)
        data = { 'text': f'{title} {link}'}
        requests.post(url, auth=auth, json=data)

        # BlueSky
        authUrl = 'https://bsky.social/xrpc/com.atproto.server.createSession'
        authData = { 'password': blueSkyAppNameCode, 'identifier': blueSkyHandle }
        response = requests.post(authUrl, json=authData)
        responseJson = json.loads(response.text)
        
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        postUrl = 'https://bsky.social/xrpc/com.atproto.repo.createRecord'

        post = {
            "$type": "app.bsky.feed.post",
            "text": f'{title} {link}',
            "createdAt": now,
        }

        record = {
            "repo": responseJson["did"],
            "collection": "app.bsky.feed.post",
            "record": post
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + responseJson["accessJwt"]
        }

        requests.post(postUrl, json=record, headers=headers)



        # Close issue
        requests.patch(f'https://api.github.com/repos/{repository}/issues/{issueNumber}', headers=headers, json={"state": "closed"})
        
        
if __name__ == "__main__":
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    run()
