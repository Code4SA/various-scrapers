from goose import Goose
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from urlparse import urlparse, urljoin
from publications import publications

g = Goose()
client = MongoClient()
db = client.article_db
articles = db.articles

def new_url(path):
    return urljoin(host, path)

class Pager(object):
    def __init__(self, first_page):
        self.url = first_page
        self.host = urlparse(url).scheme + "://" + urlparse(url).hostname

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
        
            url = pager._next_page(html)
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

        post = {
            "author" : article.select(".meta")[0].text,
            "summary" : text[0:60],
            "published" : published_date,
            "title" : article.select("h2.sub-heading")[0].text,
            "meta_description" : "",
            "text" : text
        }

        
        return post 

for (publication, base_url) in publications:
    if not base_url.endswith("/"): base_url += "/"
    url = base_url + "news/page:1/category:0"

    pager = Pager(url)
    parser = ArticleParser()
    count = 0

    for url in pager.urls:
        if not articles.find_one({"url" : url}):
            count += 1
            content = requests.get(url)
            post = parser.parse_html(content.text)
            post["publication"] = publication
            post["url"] = url

            articles.insert(post)
            count += 1
        print url
    print "%s: %d articles added" % (publication, count)
