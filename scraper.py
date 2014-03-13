import json
import argparse
import beanstalkc
import sys
import time
from scrapers.config import beanstalk
from publications import scrapermap

def consumer():
    while True:
        print "Waiting for job" 
        job = beanstalk.reserve()
        scrape_job = json.loads(job.body)
        scraper_name = scrape_job["scraper"]
        scraper = scrapermap[scraper_name]
        
        scraper.consume(scrape_job)
        job.delete()

def producer():
    for publication, scraper in scrapermap.items():
        print "Producer is running: %s" % publication
        scraper.produce()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task", help="Select either producer or consumer. Producers collect urls and place them in a queue. Consumers scrape those urls.")
    args = parser.parse_args()

    if args.task == "consumer":
        consumer()
    elif args.task == "producer":
        producer()
    else:
        # TODO - figure out how to throw an argparse error
        print "Invalid option"
        sys.exit()
