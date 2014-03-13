import json
import logging
import datetime
import feedparser
import os
import requests
from pymongo import MongoClient
from goose import Goose
from caxton import publications
from .. import config
from ..config import articles, beanstalk
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)
g = Goose()

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
                logger.error("Error putting a message into the queue", exc_info=True)


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
                "published" : date_parser.parse(entry["published"]),
                "title" : article.title,
                "meta_description" : article.meta_description,
                "text" : article.cleaned_text,
                "owner" : "Caxton",
                "sub_type" : 2,
                "downloaded_at" : datetime.datetime.now()
            }

            articles.insert(post)
        except IOError, e:
            logger.error("IOError running Goose", exc_info=True)
        except Exception, e:
            logger.error("General article scraping exception", exc_info=True)

