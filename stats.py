from pprint import pprint
from scrapers.config import beanstalk, articles, db
from datetime import datetime
import dateutil
from dateutil.relativedelta import relativedelta
import mixpanel

token = "15000f3ad9e08a2b5ab1b3848f0a19c1"
today = datetime.today()
yesterday = today - relativedelta(days=1)
print yesterday
day_start = datetime(year=yesterday.year, month=yesterday.month, day=yesterday.day, hour=0, minute=0, second=0)
day_end = datetime(year=yesterday.year, month=yesterday.month, day=yesterday.day, hour=23, minute=59, second=59)
stats_db = db.stats

#pprint(beanstalk.stats_tube('default'))
for publication in articles.distinct("publication"):
    articles_yesterday = articles.find({
        "publication" : publication,
        "downloaded_at": {
            "$gte" : day_start,
            "$lte" : day_end
        }
    }).count()
    print publication, articles_yesterday, articles.find({"publication" : publication}).count()
