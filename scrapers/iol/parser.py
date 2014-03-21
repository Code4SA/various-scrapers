from publications import publications
from ..scrapers import BasicFeedScraper

scraper = BasicFeedScraper(publications, "iol", "IOL")
def produce():
    return scraper.produce()

def consume(job):
    return scraper.consume(job)
