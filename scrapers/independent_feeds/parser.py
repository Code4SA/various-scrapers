from publications import publications
from ..scrapers import BasicFeedScraper

scraper = BasicFeedScraper(publications, "independent_feeds", "Independent")
def produce():
    return scraper.produce()

def consume(job):
    return scraper.consume(job)
