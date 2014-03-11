import json
import feedparser
import os
import requests
from pymongo import MongoClient
from goose import Goose
from caxton import publications
#import beanstalkc
from .. import config

#beanstalk = beanstalkc.Connection(host='localhost', port=11300)
beanstalk = config.beanstalk

g = Goose()
client = MongoClient()
db = client.article_db
articles = db.articles

def produce():
    for publication, feed_url in publications:
        feed = feedparser.parse(feed_url)
        for entry in feed["entries"]:
            try:
                url = entry["link"]
                print url
                beanstalk.put(json.dumps({
                    "url" : url,
                    "scraper" : "caxton_local",
                    "publication" : publication,
                    "entry" : {
                        "author" : entry["author"],
                        "summary" : entry["summary"],
                        "published" : entry["published"],
                    }
                }))
            except Exception, e:
                import traceback
                traceback.print_exc()


def consume(job):
    url = job["url"]
    entry = job["entry"]
    print url
    if not articles.find_one({"url" : url}):
        try:
            article = g.extract(url=url)

            post = {
                "publication" : job["publication"],
                "url" : url,
                "author" : entry["author"],
                "summary" : entry["summary"],
                "published" : entry["published"],
                "title" : article.title,
                "meta_description" : article.meta_description,
                "text" : article.cleaned_text
            }

            articles.insert(post)
        except IOError, e:
            print e.message
            print url
        except Exception, e:
            import traceback
            traceback.print_exc()

def parse():
    g = Goose()
    client = MongoClient()
    db = client.article_db
    articles = db.articles

    for publication, feed_url in publications:
        count = 0
        feed = feedparser.parse(feed_url)
        for entry in feed["entries"]:
            try:
                url = entry["link"]
                if not articles.find_one({"url" : url}):
                    count += 1
                    article = g.extract(url=url)

                    post = {
                        "publication" : publication,
                        "url" : url,
                        "author" : entry["author"],
                        "summary" : entry["summary"],
                        "published" : entry["published"],
                        "title" : article.title,
                        "meta_description" : article.meta_description,
                        "text" : article.cleaned_text
                    }

                    articles.insert(post)
            except IOError, e:
                print e.message
                print url
            except Exception, e:
                import traceback
                traceback.print_exc()

        print "%s: %d articles added" % (publication, count)
