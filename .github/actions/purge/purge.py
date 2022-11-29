import os
import csv
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

    if os.path.exists(f'items/{feedName}.csv'):
        lines = list()

        with open (f'items/{feedName}.csv', 'r') as readFile:
            reader = csv.reader(readFile, delimiter=',')
            for row in reader:
                if row[2] == "PublishedDate": 
                    lines.append(row)
                else:
                    publishedDate = parse(row[2])

                    if publishedDate.date() > (date.today() - timedelta(days = 7)):
                        lines.append(row)

        with open (f'items/{feedName}.csv', 'w') as writeFile:
            writer = csv.writer(writeFile, delimiter=',')
            writer.writerows(lines)
        
if __name__ == "__main__":
    run()
