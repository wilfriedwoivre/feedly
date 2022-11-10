import feedparser
import os

def test():
    feedparser.parse(os.getenv("feedlink"))


def run():
    test()


if __name__ == "__main__":
    run()
