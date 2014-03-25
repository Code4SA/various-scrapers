import requests
import datetime
from bs4 import BeautifulSoup 
from dateutil import parser
import json
from ..config import db_insert, articles
from bs4 import BeautifulSoup


feed_url = "http://www.thebugle.co.za/processors/getArticles.php"

def consume():
    pass

def produce():
    payload = {
        "num" : 30,
        "date" : "2014-03-21",
        "ajax" : ""
    }

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.post(feed_url, data=payload, headers=headers)
    js = r.json()

    

    for html in [js["artL"], js["artR"]]:
        soup = BeautifulSoup(html)
        for article in soup.select(".article_post"):
            entry = {
                "publication" : "The Bugle",
                "owner" : "Independent",
                "sub_type" : 1,
            }

            job = {
                "scraper" : "thebugle",
                "publication" : "The Bugle",
                "entry": entry
            }

            titles = article.select(".article_title")
            if len(titles) > 0:
                title = titles[0]
                entry["title"] = title.text

            authors = article.select(".article_author")
            if len(authors) > 0:
                authors = authors[0].findAll("b")
                if len(authors) > 0:
                    date = authors[0].text
                    entry["published"] = date

                if len(authors) > 1:
                    author = authors[1].text
                    entry["author"] = author

            summaries = article.select(".article_body")
            if len(summaries) > 0:
                summary = summaries[0]
                entry["summary"] = summary.text.strip()

            links = article.select("a")
            if len(links) > 0:
                link = links[0]
                job["url"] = link["href"]

            yield json.dumps(job)
