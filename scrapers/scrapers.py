import json
import logging

import feedparser
from .config import beanstalk, articles, g

logger = logging.getLogger(__name__)

class OlderArticlesAlreadySeenException(Exception):
    pass

class FeedScraper(object):
    def __init__(self, publications):
        self.publications = publications

    def produce(self):
        for publication, feed_url in self.publications:
            feed = feedparser.parse(feed_url)
            try:
                for entry in feed["entries"]:
                    url = entry["link"]
                    if articles.find_one({"url" : url}):
                        raise OlderArticlesAlreadySeenException()
                    print url
                    msg = self._gen_prod_message(entry, publication)
                    beanstalk.put(json.dumps(msg))
            except OlderArticlesAlreadySeenException:
                pass

    def _gen_prod_message(self, entry, publication):
        raise NotImplementedError()

    def consume(self, job):
        url = job["url"]
        entry = job["entry"]
        print job["publication"]
        if not articles.find_one({"url" : url}):
            print url
            try:
                article = g.extract(url=url)

                data = self._gen_consumer_message(article, job)
                articles.insert(data)
            except IOError, e:
                logger.exception("Error extracting article")
            except Exception, e:
                logger.exception("Error extracting article")

    def _gen_consumer_message(self, article, job):
        raise NotImplementedError()

