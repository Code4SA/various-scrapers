from publications import publications
from ..scrapers import BasicFeedScraper

scraper = BasicFeedScraper(publications, "naspers_feeds", "Naspers/Media24")

def produce():
    scraper.produce()

def consume(job):
    scraper.consume(job)
