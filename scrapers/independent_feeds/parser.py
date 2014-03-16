from publications import publications
from ..scrapers import BasicFeedScraper

scraper = BasicFeedScraper(publications, "independent_feeds", "Independent")
def produce():
    scraper.produce()

def consume(job):
    scraper.consume(job)
