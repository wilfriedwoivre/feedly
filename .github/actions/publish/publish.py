import os
import ssl
import requests
from requests_oauthlib import OAuth1
import json
import re
from datetime import datetime, timezone
from typing import List, Dict
from bs4 import BeautifulSoup

def parse_urls(text: str) -> List[Dict]:
    spans = []
    # partial/naive URL regex based on: https://stackoverflow.com/a/3809435
    # tweaked to disallow some training punctuation
    url_regex = rb"[$|\W](https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*[-a-zA-Z0-9@%_\+~#//=])?)"
    text_bytes = text.encode("UTF-8")
    for m in re.finditer(url_regex, text_bytes):
        spans.append({
            "start": m.start(1),
            "end": m.end(1),
            "url": m.group(1).decode("UTF-8"),
        })
    return spans


def parse_facets(text: str) -> List[Dict]:
    facets = []
    for u in parse_urls(text):
        facets.append({
            "index": {
                "byteStart": u["start"],
                "byteEnd": u["end"],
            },
            "features": [
                {
                    "$type": "app.bsky.richtext.facet#link",
                    # NOTE: URI ("I") not URL ("L")
                    "uri": u["url"],
                }
            ],
        })
    return facets

def fetch_embed_url_card(access_token: str, url: str) -> Dict:

    # the required fields for every embed card
    card = {
        "uri": url,
        "title": "",
        "description": "",
    }

    # fetch the HTML
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # parse out the "og:title" and "og:description" HTML meta tags
    title_tag = soup.find("meta", property="og:title")
    if title_tag:
        card["title"] = title_tag["content"]
    description_tag = soup.find("meta", property="og:description")
    if description_tag:
        card["description"] = description_tag["content"]

    # if there is an "og:image" HTML meta tag, fetch and upload that image
    image_tag = soup.find("meta", property="og:image")
    if image_tag:
        img_url = image_tag["content"]
        # naively turn a "relative" URL (just a path) into a full URL, if needed
        if "://" not in img_url:
            img_url = url + img_url
        resp = requests.get(img_url)
        resp.raise_for_status()

        blob_resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
            headers={
                "Content-Type": "image/png",
                "Authorization": "Bearer " + access_token,
            },
            data=resp.content,
        )
        blob_resp.raise_for_status()
        card["thumb"] = blob_resp.json()["blob"]

    return {
        "$type": "app.bsky.embed.external",
        "external": card,
    }

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

        text = f'{title} {link}'
        post = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": now,
            "facets": parse_facets(text),
            "embed": fetch_embed_url_card(responseJson["accessJwt"], "https://bsky.app")
        }

        record = {
            "repo": responseJson["did"],
            "collection": "app.bsky.feed.post",
            "record": post
        }

        bluSkyheaders = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + responseJson["accessJwt"]
        }

        requests.post(postUrl, json=record, headers=bluSkyheaders)



        # Close issue
        requests.patch(f'https://api.github.com/repos/{repository}/issues/{issueNumber}', headers=headers, json={"state": "closed"})
        
        
if __name__ == "__main__":
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    run()
