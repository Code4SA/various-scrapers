import feedparser
from .config import beanstalk, articles, g
import json

class FeedScraper(object):
    def __init__(self, publications):
        self.publications = publications

    def produce(self):
        for publication, feed_url in self.publications:
            feed = feedparser.parse(feed_url)
            for entry in feed["entries"]:
                try:
                    url = entry["link"]
                    print url
                    msg = self._gen_prod_message(entry, publication)
                    beanstalk.put(json.dumps(msg))
                except Exception, e:
                    import traceback
                    traceback.print_exc()

    def _gen_prod_message(self, entry, publication):
        raise NotImplementedError()

    def consume(self, job):
        url = job["url"]
        entry = job["entry"]
        if not articles.find_one({"url" : url}):
            print url
            try:
                article = g.extract(url=url)

                data = self._gen_consumer_message(article, job)
                articles.insert(data)
            except IOError, e:
                print e.message
                print url
            except Exception, e:
                import traceback
                traceback.print_exc()

    def _gen_consumer_message(self, article, job):
        raise NotImplementedError()

