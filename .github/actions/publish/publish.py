import os
import ssl
import requests
import json
import tweepy

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

        # Authenticate to Twitter
        auth = tweepy.OAuthHandler(twitterConsumerKey, twitterConsumerSecret)
        auth.set_access_token(twitterAccessTokenKey, twitterAccessTokenSecret)


        # Create API object
        twitterApi = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        title = item['title']
        link = item['body']
        twitterApi.update_status(f'{title} {link}')

        requests.patch(f'https://api.github.com/repos/{repository}/issues/{issueNumber}', headers=headers, json={"state": "closed"})
        
        
if __name__ == "__main__":
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    run()
