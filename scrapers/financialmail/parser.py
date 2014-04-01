import json
import datetime
import logging
from urlparse import urljoin

from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException
from dateutil import parser as date_parser
from ..config import articles
from ..scrapers import FeedScraper
from urlparse import urljoin
from publications import publications
from ..utils import url2soup

class Scraper(object):

    def __init__(self, publications):
        self.publications = publications

    def produce(self):
        for publication, url in self.publications:
            soup = url2soup(url)

            for article in soup.select(".article"):
                if hasattr(article, "h4") and hasattr(article.h4, "a"):
                    url = article.h4.a["href"]
                    title = article.h4.a.text
                    print url

                    msg = {
                        "url" : url,
                        "scraper" : "financial_mail",
                        "publication" : publication,
                        "entry" : {
                            "title" : title,
                        }
                    }

                    yield json.dumps(msg)

    def consume(self, job):
        url = job["url"]
        entry = job["entry"]
        if not articles.find_one({"url" : url}):
            try:
                soup = url2soup(url)
                if not soup: return None
                title = soup.select(".articletitle h1")[0].text
                meta = soup.select(".articletitle .meta")[0].text

                try:
                    author, date = meta.split(",", 1)
                    author = author.strip().replace("by ", "").strip()
                    date = date_parser.parse(date)
                except ValueError:
                    author = ""
                    date = date_parser.parse(meta)

                body_root = soup.select(".articlebody .body")[0]
                [el.extract() for el in body_root.select(".image")]
                [el.extract() for el in body_root.select(".teaser")]

                body = ""
                for p in body_root.select("p"):
                    body += p.text + "\n"
                
                data = {
                    "publication" : job["publication"],
                    "url" : job["url"],
                    "author" : author,
                    "summary" : "",
                    "published" : date,
                    "title" : title,
                    "text" : body,
                    "owner" : "Financial Mail",
                    "sub_type" : 1,
                    "downloaded_at" : datetime.datetime.now()
                }
                return data
            except UnicodeEncodeError:
                logging.exception("Error parsing url - possibly unicode url")
            except RequestException:
                logging.exception("Error accessing url: %s" % job)

scraper = Scraper(publications)
def produce():
    return scraper.produce()

def consume(job):
    return scraper.consume(job)
