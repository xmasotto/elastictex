#!/usr/bin/env python

# TODO: disallow tag urls
# TODO: instead of done set and queue_set, just query mongo for existence

import traceback
import random
from Queue import Queue
from bs4 import BeautifulSoup
from urllib2 import urlopen
from urlparse import urlparse
from pymongo import MongoClient
from pymongo.errors import AutoReconnect

queue = Queue()
queue_set = set()

starters = [
    "http://math.stackexchange.com/questions/309267/quadratic-equation"
]

client = MongoClient()
data = client['crawler']['data']


def main():
    if data.count() > 1:
        print("Recovering from last crawling session.")
        maxlevel = data.find_one(sort=[("$natural", -1)])['level']
        docs = data.find({'level': maxlevel - 1},
                         sort=[("rand", 1)], limit=25)
        for doc in docs:
            add_links(doc['_id'], doc['body'], doc['level'])
    else:
        for starter in starters:
            queue.put((starter, 0))

    # Start the crawl loop
    while not queue.empty():
        (url, level) = queue.get()

        crawl(url, level)


def clean_link(link):
    if urlparse(link).netloc:
        return None
    if "questions" not in link:
        return None
    if "ask" in link:
        return None
    if "login" in link:
        return None
    if "tagged" in link:
        return None
    if "?" in link:
        link = link.split("?", 1)[0]
    return link


def add_links(url, body, level):
    url_struct = urlparse(url)
    html = BeautifulSoup(body)
    links = [a.get('href') for a in html.find_all("a")]
    for link in links:
        if not link:
            continue

        link = clean_link(link)
        if link:
            full = url_struct.scheme + "://" + url_struct.netloc + link
            if full:
                queue.put((full, level+1))


def crawl(url, level):
    try:
        doc = data.find({'_id': url}, {'_id': 1})
        if doc.count() > 0:
            print("Skipped %s (%d)" % (url, level))
            return

        body = urlopen(url).read()
        add_links(url, body, level)

        data.update({
            '_id': url
        }, {
            'level': level,
            'body': body,
            'rand': random.random()
        }, upsert=True)
        print("Crawled %s (%d)" % (url, level))

    except KeyboardInterrupt:
        print("Bye Bye")
        exit(0)

    except AutoReconnect:
        print("AutoReconnect")
        crawl(url, level)

    except:
        traceback.print_exc()

if __name__ == "__main__":
    main()
