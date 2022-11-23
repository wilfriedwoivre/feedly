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
    
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, FeedItem):
            return self.publishedDate == __o.publishedDate

    def writeRow(self):
        return [self.title, self.link, self.publishedDate, self.publish, self.ignore, self.isPublished]

def run():
    feedName = os.getenv("FeedName")
    feedLink = os.getenv("FeedLink")
    autoPublish = bool(os.getenv("AutoPublish"))

    feedData = feedparser.parse(feedLink)

    validItems =  []
    for item in feedData.entries:
        publishedDate = parse(item.published)

        if publishedDate.date() > (date.today() - timedelta(days = 7)):
            validItems.append(FeedItem(item.title, item.links[0].href, item.published, autoPublish, False, False))

    
    if validItems.__len__() > 0:
        existingItem = []
        print(os.path.exists(f'items/{feedName}.csv')) 

        if not os.path.exists(f'items/{feedName}.csv'):
            with open(f'items/{feedName}.csv', 'w', newline='',  encoding='utf-8') as file:
                csvWriter = csv.writer(file, delimiter=',')
                headers = ["Title", "Link", "PublishedDate", "Publish", "Ignore", "IsPublished"]
                csvWriter.writerow(headers)
            

        with open(f'items/{feedName}.csv', encoding='utf-8') as file:
            csvReader = csv.reader(file, delimiter=',')
            # Skip header
            next(csvReader, None)
            for row in csvReader:
                existingItem.append(FeedItem(row[0], row[1], row[2], row[3], row[4], row[5]))
        
        with open(f'items/{feedName}.csv', 'a+', newline='',  encoding='utf-8') as file:
            csvWriter = csv.writer(file, delimiter=',')
            for item in validItems:
                if not any(item for e in existingItem):
                    csvWriter.writerow(item.writeRow())

        
if __name__ == "__main__":
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    run()
