import json
import datetime

import feedparser
from dateutil import parser as date_parser
from publications import publications
from ..config import beanstalk, articles
from goose import Goose

g = Goose()
class produce():
    for publication, feed_url in publications:
        feed = feedparser.parse(feed_url)
        for entry in feed["entries"]:
            try:
                url = entry["link"]
                print url
                beanstalk.put(json.dumps({
                    "url" : url,
                    "scraper" : "iol",
                    "publication" : publication,
                    "entry" : {
                        "summary" : entry["description"],
                        "published" : entry["published"],
                        "title" : entry["title"],
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
                "author" : article.author if hasattr(article, "author") else "",
                "summary" : entry["summary"],
                "published" : date_parser.parse(entry["published"]),
                "title" : entry["title"],
                "text" : article.cleaned_text,
                "owner" : "IOL",
                "sub_type" : 1,
                "downloaded_at" : datetime.datetime.now()
            }

            articles.insert(post)
        except IOError, e:
            print e.message
            print url
        except Exception, e:
            import traceback
            traceback.print_exc()

