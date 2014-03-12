import requests
import datetime
from bs4 import BeautifulSoup 
from dateutil import parser
import json
from ..config import articles


feed_url = "http://mg.co.za/feeds/lexisnexis"

def consume():
    pass

def produce():
    xml = requests.get(feed_url).content
    soup = BeautifulSoup(xml, "html5lib") 
    count = 0

    for article in soup.select("newsitem"):
            count += 1
            if not articles.find_one({"id" : article.article_id.text}):
                soup2 = BeautifulSoup(article.text, "html5lib")
                post = {
                    "publication" : "Mail & Guardian",
                    "id" : article.article_id.text,
                    "author" : article.byline.text,
                    "summary" : article.blurb.text,
                    "published" : parser.parse(article.publicationdate.text),
                    "title" : article.headline.text,
                    "text" : soup2.text,
                    "owner" : "Mail & Guardian",
                    "sub_type" : 1,
                    "downloaded_at" : datetime.datetime.now()
                }
                articles.insert(post)
    print count
