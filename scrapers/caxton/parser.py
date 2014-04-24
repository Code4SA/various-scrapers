from dateutil import parser as date_parser
from publications import publications
from ..scrapers import BasicFeedScraper, ScraperConsumer

class Consumer(ScraperConsumer):
    def get_title(self, soup):
        title = soup.select("h1.article-headline a")
        if title and len(title) == 1:
            return title[0].text.strip()
        return ""

    def get_publishdate(self, soup):
        date = soup.select(".page-lead-datetime")
        if date and len(date) >= 1: 
            return date_parser.parse(date[0].text)
        return None

    def get_body(self, soup):
        body = ""
        caption = soup.select(".wp-caption-text")
        for c in caption:
            body += c.text + "\n\n"

        content = soup.select(".article-content p")
        for p in content:
            body += p.text + "\n\n"
        return body.strip()

    def get_summary(self, soup):
        excerpt = soup.select(".article-excerpt")
        if excerpt and len(excerpt) == 1:
            return excerpt[0].text.strip()
        return ""

    def get_owner(self, soup):
        return "Caxton"

    def get_subtype(self, soup):
        return 2
    

scraper = BasicFeedScraper(publications, "caxton_local", "Caxton", sub_type=2)
consumer = Consumer()

def produce():
    return scraper.produce()

def consume(job):
    return consumer.consume(job)

