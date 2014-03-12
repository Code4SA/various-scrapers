from pprint import pprint
from scrapers.config import beanstalk

pprint(beanstalk.stats_tube('default'))
