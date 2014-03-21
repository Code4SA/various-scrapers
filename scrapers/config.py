import os
import json
import logging.config
import requests

from goose import Goose
from goose.configuration import Configuration
import beanstalkc
from pymongo import MongoClient
from mixpanel import Mixpanel

token = "15000f3ad9e08a2b5ab1b3848f0a19c1"
mp = Mixpanel(token)

beanstalk = beanstalkc.Connection(host='localhost', port=11300)

client = MongoClient()
db = client.article_db
articles = db.articles
config = Configuration()
config.enable_image_fetching = False

def extract(self, url):
    r = requests.get(url)
    raw_html = r.content
    return self.extract(raw_html=raw_html)

class MyGoose(Goose):
    def extract(self, url=None, raw_html=None):
        if raw_html:
            return super(MyGoose, self).extract(raw_html=raw_html)
        else:
            r = requests.get(url)
            raw_html = r.content
            return self.extract(raw_html=raw_html)

g = MyGoose(config)
    
def db_insert(post):
    if post:
        print post['publication']
        mp.track(None, post["publication"])
        articles.insert(post)

def setup_logging(
    default_path='logging.json', 
    default_level=logging.DEBUG,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.loads(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

setup_logging()
