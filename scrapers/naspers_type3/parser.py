import json
import datetime
import logging
from urlparse import urljoin

from bs4 import BeautifulSoup
import requests
from dateutil import parser as date_parser
from publications import publications
from ..config import articles, g
from ..scrapers import FeedScraper
from ..utils import url2soup

class Scraper(object):
    def __init__(self, publications):
        self.publications = publications

    def produce(self):
        for publication, url in self.publications:
            soup = url2soup(url)
            for article in soup.select(".edition_box"):

                el = article.select(".newslist_title_text")[0]
                title = el.text.strip()
                article_url = el["href"]

                date = article.select(".newslist_date_text")[0].text.strip()
                text = article.select(".grey_font12px")[0].text.strip()

                msg = {
                    "url" : urljoin(url, article_url),
                    "scraper" : "naspers_type3",
                    "publication" : publication,
                    "entry" : {
                        "title" : title,
                        "published" : date,
                        "summary" : text
                    }
                }

                yield json.dumps(msg)

    def consume(self, job):
        url = job["url"]
        entry = job["entry"]
        if not articles.find_one({"url" : url}):
            try:
                soup = url2soup(url)
                if soup:
                    info = soup.select(".article_info")
                    if not info: return None
                    info = info[0]
                    divs = info.select("div")
                    if not len(divs) > 1: return None

                    info2 = info.select("div")[1]
                    divs = info2.select("div")
                    if not len(divs) > 2: return None

                    info3 = divs[4]
                    divs = info3.select("div")
                    title = divs[0].text
                    author = divs[1].text
                    try:
                        publish_date = date_parser.parse(divs[3].text)
                    except TypeError:
                        logging.exception("Error parsing published date: %s" % url)
                    summary = divs[4].text

                    body = ""
                    ps = soup.select(".article_body_font p")
                    for p in ps:
                        body += p.text + "\n\n"
                     
                article = g.extract(url=url)
                return {
                    "publication" : job["publication"],
                    "url" : job["url"],
                    "author" : author, 
                    "summary" : entry.get("summary", "") or summary,
                    "published" : date_parser.parse(entry["published"]),
                    "title" : entry["title"],
                    "text" : body,
                    "owner" : "Naspers/Media24",
                    "sub_type" : 3,
                    "downloaded_at" : datetime.datetime.now()
                }
            except UnicodeEncodeError:
                logging.exception("Error parsing url - possibly unicode url: %s" % url)
 
scraper = Scraper(publications)
def produce():
    return scraper.produce()

def consume(job):
    return scraper.consume(job)
