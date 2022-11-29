import csv
import os

class FeedSource:
    def __init__(self, siteName: str, link: str, type: str, isActive: bool, autoPublish: bool, siteLink: str):
        self.siteName = siteName
        self.link = link
        self.type = type
        self.autoPublish = autoPublish
        self.isActive = isActive
        self.siteLink = siteLink
    
    def __str__(self):
        return f'{self.siteName}({self.link}) - Type : {self.type} - AutoPublish : {self.autoPublish} - IsActive : {self.isActive}'

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return self

def run():

    outputFilePath = os.getenv("outputFilePath")

    sources = []
    with open(f'sources.csv', encoding='utf-8') as file:
        csvReader = csv.reader(file, delimiter=',')
        # Skip header
        next(csvReader, None)
        for item in csvReader:
            sources.append(FeedSource(item[0], item[1], item[2], item[3], item[4], item[5]))

    matrixOutput =  "name=matrix={\"include\":["
    
    for item in sources:
        matrixOutput += "{\"FeedName\":\""+item.siteName+"\", \"FeedLink\":\""+item.link+"\", \"AutoPublish\":\""+item.autoPublish+"\"},"

    matrixOutput = matrixOutput[:-1]
    matrixOutput += "]}"
    
    print(f'echo "{matrixOutput}" >> $GITHUB_OUTPUT')
        
if __name__ == "__main__":
    run()
