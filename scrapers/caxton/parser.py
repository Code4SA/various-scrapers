from publications import publications
from ..scrapers import BasicFeedScraper

scraper = BasicFeedScraper(publications, "caxton_local", "Caxton", sub_type=2)

def produce():
    return scraper.produce()

def consume(job):
    return scraper.consume(job)

