import os
import json
import logging.config

from goose import Goose
import beanstalkc
from pymongo import MongoClient

beanstalk = beanstalkc.Connection(host='localhost', port=11300)

client = MongoClient()
db = client.article_db
articles = db.articles
g = Goose()

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
