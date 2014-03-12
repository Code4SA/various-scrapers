import beanstalkc
from pymongo import MongoClient

beanstalk = beanstalkc.Connection(host='localhost', port=11300)

client = MongoClient()
db = client.article_db
articles = db.articles
