import feedparser
import os
import csv
import ssl
from dateutil.parser import parse
from datetime import *
import requests
import json

class FeedItem:
    def __init__(self, title: str, link: str, publishedDate: str):
        self.title = title
        self.link = link
        self.publishedDate = publishedDate
    
    def __str__(self):
        return f'{self.title}({self.link})'

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return self
    
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, FeedItem):
            return self.publishedDate == __o.publishedDate

    def writeRow(self):
        return [self.title, self.link, self.publishedDate]

def to_bool(value: str):
    valid = {'true': True, '1': True, 'false': False, '0': False }   

    if isinstance(value, bool):
        return value

    lower_value = value.lower()
    if lower_value in valid:
        return valid[lower_value]
    else:
        raise ValueError('invalid literal for boolean: "%s"' % value)


def run():
    feedName = os.getenv("FeedName")
    feedLink = os.getenv("FeedLink")
    feedType = os.getenv("FeedType")
    prefix = os.getenv("FeedPrefix")
    suffix = os.getenv("FeedSuffix")
    repository = os.getenv("GithubRepository")
    githubToken = os.getenv("GithubToken")

    feedData = feedparser.parse(feedLink)

    validItems =  []
    for item in feedData.entries:
        if feedType == "rss":
            publishedDate = parse(item.published)

            print(f'{item.title}')

            if publishedDate.date() > (date.today() - timedelta(days = 7)):
                validItems.append(FeedItem(item.title, item.links[0].href, item.published))
        elif feedType == "atom":
            publishedDate = parse(item.updated)

            print(f'{item.title}')

            if publishedDate.date() > (date.today() - timedelta(days = 7)):
                validItems.append(FeedItem(item.title, item.links[0].href, item.updated))
        

    print("Valid Items")
    print(validItems)
    
    if validItems.__len__() > 0:
        existingItem = []
        print(os.path.exists(f'items/{feedName}.csv')) 

        if not os.path.exists(f'items/{feedName}.csv'):
            print(f'Create file for {feedName}') 
            with open(f'items/{feedName}.csv', 'x', newline='',  encoding='utf-8') as file:
                csvWriter = csv.writer(file, delimiter=',')
                headers = ["Title", "Link", "PublishedDate"]
                csvWriter.writerow(headers)
        
         

        with open(f'items/{feedName}.csv', encoding='utf-8') as file:
            csvReader = csv.reader(file, delimiter=',')
            # Skip header
            next(csvReader, None)
            for row in csvReader:
                existingItem.append(FeedItem(row[0], row[1], row[2]))
        
        print("Existing Items")
        print(existingItem)
        
        with open(f'items/{feedName}.csv', 'a+', newline='',  encoding='utf-8') as file:
            csvWriter = csv.writer(file, delimiter=',')
            for item in validItems:
                exist = False
                for exItem in existingItem:
                    if exItem.link == item.link and exItem.title == item.title:
                        exist = True
                if not exist:
                    csvWriter.writerow(item.writeRow())
                    headers = {
                        'Accept': 'application/json',
                        'Authorization': f'Bearer {githubToken}'
                    }
                    print(item.link)
                    title = item.title
                    if prefix != "":
                        title = f'{prefix} - {item.title}'
                    url = build_url(item.link, suffix)
                    r = requests.post(f'https://api.github.com/repos/{repository}/issues', json={"title": title, "body": url, "labels": ["triage"]}, headers=headers)


def build_url(url: str, suffix: str):
    if suffix == "":
        return url
    if not url.__contains__("?"):
        return f'{url}{suffix}'
    else:
        parts = url.split("?")
        return f'{parts[0]}{suffix}&{parts[1]}'

        
if __name__ == "__main__":
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    run()
