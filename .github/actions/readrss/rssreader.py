import feedparser
import os
import csv
import ssl
from dateutil.parser import parse
from datetime import *

class FeedItem:
    def __init__(self, title: str, link: str, publishedDate: str, publish: bool, ignore: bool, isPublished: bool):
        self.title = title
        self.link = link
        self.publishedDate = publishedDate
        self.publish = publish
        self.ignore = ignore
        self.isPublished = isPublished
    
    def __str__(self):
        return f'{self.title}({self.link}) - ToPublish : {self.publish} - ToIgnore : {self.ignore} - Published : {self.isPublished}'

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return self

    def writeRow(self):
        return [self.title, self.link, self.publishedDate, self.publish, self.ignore, self.isPublished]

def run():
    feedName = os.getenv("FeedName")
    feedLink = os.getenv("FeedLink")

    feedData = feedparser.parse(feedLink)

    validItems =  []
    for item in feedData.entries:
        publishedDate = parse(item.published)

        if publishedDate.date() > (date.today() - timedelta(days = 60)):
            validItems.append(FeedItem(item.title, item.links[0].href, item.published, False, False, False))

    print(validItems)

    if validItems.__len__() > 0:
        with open(f'items/{feedName}.csv', 'w', newline='',  encoding='utf-8') as file:
            csvWriter = csv.writer(file, delimiter=',')
            headers = ["Title", "Link", "PublishedDate", "Publish", "Ignore", "IsPublished"]
            csvWriter.writerow(headers)
            for item in validItems:
                csvWriter.writerow(item.writeRow())

        


if __name__ == "__main__":
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    run()
