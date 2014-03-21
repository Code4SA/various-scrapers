from publications import publications
from ..scrapers import BasicFeedScraper

scraper = BasicFeedScraper(publications, "naspers_feeds", "Naspers/Media24")

def produce():
    return scraper.produce()

def consume(job):
    return scraper.consume(job)
