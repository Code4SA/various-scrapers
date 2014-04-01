import re
import logging
import requests
import datetime
from bs4 import BeautifulSoup 
import json
from ..config import db_insert, articles
from ..utils import url2soup, parse_date
from ..scrapers import BasicFeedScraper
from bs4 import BeautifulSoup
from publications import publications

logger = logging.getLogger(__name__)

class Scraper(BasicFeedScraper):
    re_author = re.compile("BY ([a-zA-Z\s]+)", re.I)
    re_date = re.compile("ON (\d\d? \w+ \d{4})", re.I)

    def _get_header(self, soup):
        article = soup.find("article")
        header = article.find("header")
        return header

    def _get_meta(self, soup):
        header = self._get_header(soup)
        meta = header.select("p.meta")[0].text
        return meta

    def get_title(self, soup):
        header = self._get_header(soup)
        return header.select("h1.title")[0].text

    def get_author(self, soup):
        meta = self._get_meta(soup)
        match = Scraper.re_author.search(meta)
        if match:
            return match.groups()[0]
        return ""

    def get_published_date(self, soup):
        meta = self._get_meta(soup)
        match = Scraper.re_date.search(meta)
        if match:
            return parse_date(match.groups()[0])
        return ""
        
    def consume(self, post):
        try:
            url = post["url"]
            entry = post["entry"]

            soup = url2soup(url)

            title = self.get_title(soup)
            author = self.get_author(soup)
            published_date = self.get_published_date(soup)

            body = ""
            for p in soup.select(".content p"):
                body += p.text + "\n\n"
            for div in soup.select(".content div"):
                body += div.text + "\n\n"

            entry.update(
                publication=post["publication"],
                owner="North West Papers",
                sub_type=1,
                url=url,
                title=entry.get("title", title),
                author=entry.get("author", author),
                published=entry.get("published", published_date),
                text=body,
                downloaded_at=datetime.datetime.now(),
            )
            return entry

        except Exception:
            logger.exception("Could not download url: %s" % url)

scraper = Scraper(publications, "northwest", "Northwest")
def consume(post):
    return scraper.consume(post)

def produce():
    return scraper.produce()
