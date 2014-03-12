import json
import argparse
import beanstalkc
import sys
import scrapers.caxton as caxton
import scrapers.naspers as naspers
import scrapers.mg as mg
import scrapers.iol as iol
import time
from scrapers.config import beanstalk

consumer_map = {
    "caxton_local" : caxton,
    "naspers_local" : naspers,
    "iol" : iol,
}

def consumer():
    while True:
        print "Waiting for job" 
        job = beanstalk.reserve()
        scrape_job = json.loads(job.body)
        scraper_name = scrape_job["scraper"]
        scraper = consumer_map[scraper_name]
        
        scraper.consume(scrape_job)
        job.delete()

def producer():
    caxton.produce()
    naspers.produce()
    mg.produce()
    iol.produce()

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
