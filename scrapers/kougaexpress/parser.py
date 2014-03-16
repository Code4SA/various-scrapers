import json
import datetime
import logging
from urlparse import urljoin

from bs4 import BeautifulSoup
import requests
from dateutil import parser as date_parser
from publications import publications
from ..config import beanstalk, articles, g
from ..scrapers import FeedScraper

class Scraper(object):
    def __init__(self, publications):
        self.publications = publications

    def produce(self):
        for publication, url in self.publications:
            r = requests.get(url)
            content = r.content
            soup = BeautifulSoup(content, "html5lib")
            for article in soup.select(".edition_box"):

                el = article.select(".newslist_title_text")[0]
                title = el.text.strip()
                article_url = el["href"]
                print article_url

                date = article.select(".newslist_date_text")[0].text.strip()
                text = article.select(".grey_font12px")[0].text.strip()

                msg = {
                    "url" : urljoin(url, article_url),
                    "scraper" : "kougaexpress",
                    "publication" : publication,
                    "entry" : {
                        "title" : title,
                        "published" : date,
                        "summary" : text
                    }
                }

                beanstalk.put(json.dumps(msg))

    def consume(self, job):
        url = job["url"]
        entry = job["entry"]
        print job["publication"]
        if not articles.find_one({"url" : url}):
            try:
                print url
                article = g.extract(url=url)
                return {
                    "publication" : job["publication"],
                    "url" : job["url"],
                    "author" : article.author if hasattr(article, "author") else "",
                    "summary" : entry["summary"],
                    "published" : date_parser.parse(entry["published"]),
                    "title" : entry["title"],
                    "text" : article.cleaned_text,
                    "owner" : "Naspers/Media24",
                    "downloaded_at" : datetime.datetime.now()
                }
            except UnicodeEncodeError:
                logging.exception("Error parsing url - possibly unicode url")
 
scraper = Scraper(publications)
def produce():
    scraper.produce()

def consume(job):
    scraper.consume(job)
