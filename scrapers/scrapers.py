import json
import datetime
import logging
import dateutil.parser as date_parser

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
                    if not "author" in msg["entry"] and "author" in entry:
                        msg["entry"]["author"] = entry["author"]
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

                entry.update(
                    url=url, downloaded_at=datetime.datetime.now(), publication=job["publication"],
                    text=article.cleaned_text
                )
                if not "author" in entry and hasattr(article, "author"):
                    entry["author"] = article.author

                data = self._gen_consumer_message(article, job)
                entry.update(data)
                articles.insert(entry)

            except IOError, e:
                logger.exception("Error extracting article :%s" % url)
            except Exception, e:
                logger.exception("Error extracting article: %s" % url)

    def _gen_consumer_message(self, article, job):
        raise NotImplementedError()

class BasicFeedScraper(FeedScraper):
    def __init__(self, publications, scraper, owner, sub_type=1):
        super(BasicFeedScraper, self).__init__(publications)
        self.scraper = scraper
        self.owner = owner
        self.sub_type = sub_type

    def _gen_prod_message(self, entry, publication):
        url = entry["link"]
        return {
            "url" : url,
            "scraper" : self.scraper,
            "publication" : publication,
            "entry" : {
                "summary" : entry["description"],
                "published" : entry["published"],
                "title" : entry["title"],
            }
        }

    def _gen_consumer_message(self, article, job):
        entry = job["entry"]

        return {
            "published" : date_parser.parse(entry["published"]),
            "owner" : self.owner,
            "sub_type" : self.sub_type,
        }
