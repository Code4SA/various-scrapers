from publications import publications
from ..scrapers import BasicFeedScraper

scraper = BasicFeedScraper(publications, "iol", "IOL")
def produce():
    scraper.produce()

def consume(job):
    scraper.consume(job)
