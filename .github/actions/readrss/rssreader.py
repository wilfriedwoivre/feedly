import feedparser
import os

def test():
    data = feedparser.parse(os.getenv("feedlink"))
    print(data)

def run():
    test()


if __name__ == "__main__":
    run()
