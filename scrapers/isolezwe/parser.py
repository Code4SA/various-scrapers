import json
import datetime
import logging
from urlparse import urljoin

from bs4 import BeautifulSoup
import requests
from dateutil import parser as date_parser
from ..config import articles
from ..scrapers import BasicFeedScraper
from urlparse import urljoin
from ..utils import url2soup

class Scraper(BasicFeedScraper):

    def __init__(self):
        super(Scraper, self).__init__([("Isolezwe", "http://www.iol.co.za/cmlink/1.1116601")], "isolezwe", "Isolezwe")

    def consume(self, job):
        url = job["url"]
        entry = job["entry"]
        if not articles.find_one({"url" : url}):
            try:
                soup = url2soup(url)
                if not soup: return None

                byline = soup.select(".byline")
                if len(byline) > 0:
                    parts = byline[0].text.strip().split("\n")
                    published = date_parser.parse(parts[0].strip())
                    if len(parts) > 1:
                        author = parts[1].replace("by", "").strip()
                    

                body = ""
                for chunks in soup.select(".arcticle_text"):
                    body += "\n" + chunks.text
                body = body.strip()

                data = {
                    "publication" : job["publication"],
                    "url" : job["url"],
                    "author" : author,
                    "summary" : entry.get("summary", ""),
                    "published" : published,
                    "title" : entry.get("title", ""),
                    "text" : body,
                    "owner" : "IOL",
                    "sub_type" : 1,
                    "downloaded_at" : datetime.datetime.now()
                }
                return data
            except UnicodeEncodeError:
                logging.exception("Error parsing url - possibly unicode url")

scraper = Scraper()
def produce():
    return scraper.produce()

def consume(job):
    return scraper.consume(job)
