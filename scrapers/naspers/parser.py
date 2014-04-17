import json
import logging
import datetime
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from urlparse import urlparse, urljoin
from publications import publications
from requests.exceptions import ConnectionError
from dateutil import parser as date_parser
from ..config import articles, db_insert
from ..scrapers import ScraperConsumer

logger = logging.getLogger(__name__)
def new_url(path):
    return urljoin(host, path)

class Pager(object):
    def __init__(self, first_page):
        self.url = first_page
        self.host = urlparse(self.url).scheme + "://" + urlparse(self.url).hostname

    def _new_url(self, path):
        return urljoin(self.host, path)

    @property
    def urls(self):
        url = self.url
        while True:
            try:
                content = requests.get(url)
                html = content.text

                soup = BeautifulSoup(html, "html5lib")
                for el in soup.select(".pod-title"):
                    yield self._new_url(el.a["href"])
            
                url = self._next_page(html)
                if not url: break
            except ConnectionError:
                logger.exception("Could not connect to: %s" % url)
                break
        

    def _next_page(self, html):
        try:
            soup = BeautifulSoup(html)
            next = soup.select(".next.active")[0]
            path = next.a["href"]
            return urljoin(self.host, path)
        except IndexError:
            return None
        except Exception, e:
            logging.exception(e)

class Consumer(ScraperConsumer):
    @staticmethod
    def first_or_none(el):
        if len(el) > 0:
            return el[0]
        return None

    @staticmethod
    def text_or_none(el):
        if len(el) > 0:
            return el[0].text.strip()
        return None

    def _get_article(self, soup):
        article = \
            Consumer.first_or_none(soup.select(".article-fullview")) \
            or Consumer.first_or_none(soup.select(".article-content"))
        return article

    def get_caption(self, soup):
        return Consumer.text_or_none(soup.select(".wp-caption-text"))

    def get_body(self, soup):
        article = self._get_article(soup)
        allowed_classes = ["p", "s1"]

        content = []
        for el in ["p", "div"]:
            ps = article.select(el)
            for p in ps:
                is_content = False

                class_is_list = "class" in p.attrs and type(p.attrs["class"]) == list
                has_class = "class" in p.attrs

                if class_is_list and p.attrs["class"][0] in allowed_classes:
                    is_content = True
                elif has_class and p.attrs["class"] in allowed_classes:
                    is_content = True
                    
            
                if not has_class or is_content:
                    content.append(p.text)
        text =  "\n".join(content)

        caption = self.get_caption(soup)
        if caption:
            text += "\n\n" + caption

        return text

    def get_publishdate(self, soup):
        article = self._get_article(soup)

        try:
            published_date = article.select(".publish-date")[0].text
            if ":" in published_date:
                published_date = published_date.split(":")[1].strip()
            published_date = date_parser.parse(published_date)
        except Exception:
            published_date = None
        return published_date

    def get_author(self, soup):
        article = self._get_article(soup)

        meta = article.select(".meta")
        author = ""
        if len(meta) == 1: author = meta[0].text
        if ":" in author: author = author.split(":")[1].strip()
        return author

    def get_summary(self, soup):
        body = self.get_body(soup)
        return body[0:60]

    def get_title(self, soup):
        article = self._get_article(soup)

        heading = Consumer.text_or_none(article.select("h2.sub-heading"))
        if heading: return heading

        heading = Consumer.text_or_none(soup.select("h1[itemprop=headline]"))
        if heading: return heading

        return ""

    def get_owner(self, soup):
        return "Naspers/Media24"

def produce():
    for publication, base_url in publications:
        if not base_url.endswith("/"): base_url += "/"
        url = base_url + "news/page:1/category:0"

        pager = Pager(url)
        for url in pager.urls:
            yield json.dumps({
                "url" : url,
                "scraper" : "naspers_local",
                "publication" : publication,
                "entry" : { },
            })

consumer = Consumer()
def consume(job):
    print job
    return consumer.consume(job)

