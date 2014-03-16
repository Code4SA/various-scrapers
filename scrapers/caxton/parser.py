from publications import publications
from ..scrapers import BasicFeedScraper

scraper = BasicFeedScraper(publications, "caxton_local", "Caxton", sub_type=2)

def produce():
    scraper.produce()

def consume(job):
    scraper.consume(job)

