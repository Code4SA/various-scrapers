import json
import datetime
import logging
import dateutil.parser as date_parser
from utils import url2soup

import feedparser
from .config import beanstalk, articles, g

logger = logging.getLogger(__name__)

class OlderArticlesAlreadySeenException(Exception):
    pass

class FakeFeeder(object):
    def __init__(self, publication, urls, scraper):
        self.publication = publication
        self.urls = urls
        self.scraper = scraper

    def produce(self):
        for url in self.urls:
            msg = {
                "url" : url,
                "scraper" : self.scraper,
                "publication" : self.publication,
                "entry" : {
                    "summary" : "",
                    "published" : "",
                    "title" : "",
                    "author" : "",
                }
            }

            yield json.dumps(msg)


class Feeder(object):
    def __init__(self, scraper, publications):
        self.publications = publications
        self.scraper = scraper

    def produce(self):
        for publication, feed_url in self.publications:
            feed = feedparser.parse(feed_url)
            try:
                for entry in feed["entries"]:
                    url = entry["link"]
                    logger.info("Pushing %s" % url)
                    if articles.find_one({"url" : url}):
                        raise OlderArticlesAlreadySeenException()


                    msg = {
                        "url" : url,
                        "scraper" : self.scraper,
                        "publication" : publication,
                        "entry" : {
                            "summary" : entry.get("description", ""),
                            "published" : entry.get("published", ""),
                            "title" : entry.get("title", ""),
                        }
                    }

                    if "author" in entry:
                        msg["entry"]["author"] = entry["author"]

                    yield json.dumps(msg)
            except OlderArticlesAlreadySeenException:
                pass

class ScraperConsumer(object):

    def get_title(self, soup):
        return ""

    def get_author(self, soup):
        return ""

    def get_publishdate(self, soup):
        return ""

    def get_body(self, soup):
        return ""

    def get_summary(self, soup):
        return ""

    def get_owner(self, soup):
        return NotImplementedException()

    def get_subtype(self, soup):
        return 1

    def consume(self, job):
        url = job["url"]
        entry = job["entry"]
        if not articles.find_one({"url" : url}):
            try:
                soup = url2soup(url)
                if not soup: return None

                data = {
                    "publication" : job["publication"],
                    "url" : job["url"],
                    "author" : self.get_author(soup),
                    "summary" : self.get_summary(soup),
                    "published" : self.get_publishdate(soup),
                    "title" : self.get_title(soup),
                    "text" : self.get_body(soup),
                    "owner" : self.get_owner(soup),
                    "sub_type" : self.get_subtype(soup),
                    "downloaded_at" : datetime.datetime.now()
                }
                return data
            except UnicodeEncodeError:
                logging.exception("Error parsing url - possibly unicode url")
            except RequestException:
                logging.exception("Error accessing url: %s" % job)
    
class FeedScraper(object):
    def __init__(self, publications):
        self.publications = publications

    def produce(self):
        for publication, feed_url in self.publications:
            feed = feedparser.parse(feed_url)
            try:
                for entry in feed["entries"]:
                    url = entry["link"]
                    logger.info("Pushing %s" % url)
                    if articles.find_one({"url" : url}):
                        raise OlderArticlesAlreadySeenException()
                    msg = self._gen_prod_message(entry, publication)
                    if not "author" in msg["entry"] and "author" in entry:
                        msg["entry"]["author"] = entry["author"]
                    yield json.dumps(msg)
            except OlderArticlesAlreadySeenException:
                pass

    def _gen_prod_message(self, entry, publication):
        raise NotImplementedError()

    def consume(self, job):
        url = job["url"]
        entry = job["entry"]
        if not articles.find_one({"url" : url}):
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
                return entry

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
                "summary" : entry.get("description", ""),
                "published" : entry.get("published", ""),
                "title" : entry.get("title", ""),
            }
        }

    def _gen_consumer_message(self, article, job):
        entry = job["entry"]

        published = ""
        if entry["published"]:
            published = date_parser.parse(entry["published"])

        return {
            "published" : published,
            "owner" : self.owner,
            "sub_type" : self.sub_type,
        }
