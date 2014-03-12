import json
import datetime
from goose import Goose
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from urlparse import urlparse, urljoin
from publications import publications
#import beanstalkc
from .. import config

#beanstalk = beanstalkc.Connection(host='localhost', port=11300)
beanstalk = config.beanstalk

g = Goose()
client = MongoClient()
db = client.article_db
articles = db.articles

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
            content = requests.get(url)
            html = content.text

            soup = BeautifulSoup(html)
            for el in soup.select(".pod-title"):
                yield self._new_url(el.a["href"])
        
            url = self._next_page(html)
            if not url: break
        

    def _next_page(self, html):
        try:
            soup = BeautifulSoup(html)
            next = soup.select(".next.active")[0]
            path = next.a["href"]
            return urljoin(self.host, path)
        except IndexError:
            return None
        except Exception, e:
            import traceback
            traceback.print_exc()

class ArticleParser(object):
    def parse_html(self, html):
        soup = BeautifulSoup(html)
        article = soup.select(".article-fullview")[0]
        content = []

        ps = article.select("p")
        for p in ps:
            if not "class" in p.attrs:
                content.append(p.text)
        text =  "\n".join(content)

        published_date = article.select(".publish-date")[0].text
        if ":" in published_date:
            published_date = published_date.split(":")[1].strip()

        meta = article.select(".meta")
        author = ""
        if len(meta) == 1: author = meta[0].text

        post = {
            "author" : author,
            "summary" : text[0:60],
            "published" : published_date,
            "title" : article.select("h2.sub-heading")[0].text,
            "meta_description" : "",
            "text" : text
        }

        
        return post 

def produce():
    for publication, base_url in publications:
        if not base_url.endswith("/"): base_url += "/"
        url = base_url + "news/page:1/category:0"

        pager = Pager(url)
        for url in pager.urls:
            print url
            beanstalk.put(json.dumps({
                "url" : url,
                "scraper" : "naspers_local",
                "publication" : publication,
            }))

def consume(job):
    url = job["url"]
    print url
    parser = ArticleParser()
    
    if not articles.find_one({"url" : url}):
        content = requests.get(url)
        post = parser.parse_html(content.text)
        post["publication"] = job["publication"]
        post["url"] = url
        post["downloaded_at"] = datetime.datetime.now()
        articles.insert(post)


