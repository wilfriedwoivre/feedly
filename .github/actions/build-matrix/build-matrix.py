import csv
import os

class FeedSource:
    def __init__(self, siteName: str, link: str, type: str, isActive: bool, autoPublish: bool, siteLink: str, prefix: str):
        self.siteName = siteName
        self.link = link
        self.type = type
        self.autoPublish = autoPublish
        self.isActive = isActive
        self.siteLink = siteLink
        self.prefix = prefix
    
    def __str__(self):
        return f'{self.siteName}({self.link}) - Type : {self.type} - AutoPublish : {self.autoPublish} - IsActive : {self.isActive}'

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return self

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
    sources = []
    with open(f'sources.csv', encoding='utf-8') as file:
        csvReader = csv.reader(file, delimiter=',')
        # Skip header
        next(csvReader, None)
        for item in csvReader:
            sources.append(FeedSource(item[0], item[1], item[2], item[3], item[4], item[5], item[6]))

    matrixOutput =  "matrix={\"include\":["
    
    for item in sources:
        if (to_bool(item.isActive)):
            matrixOutput += "{\"FeedName\":\""+item.siteName+"\", \"FeedLink\":\""+item.link+"\", \"FeedType\":\""+item.type+"\", \"Prefix\":\""+item.prefix+"\"},"

    matrixOutput = matrixOutput[:-1]
    matrixOutput += "]}"
    
    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
        output.write(f"{matrixOutput}\n")
        
if __name__ == "__main__":
    run()
