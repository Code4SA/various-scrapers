from bs4 import BeautifulSoup
import requests
import logging

logger = logging.getLogger(__name__)

def url2soup(url):
    try:
        r = requests.get(url)
        content = r.content.decode("utf8")
        soup = BeautifulSoup(content, "html5lib")
        return soup
    except UnicodeEncodeError:
        logger.exception("Could not decode page: %s" % url)

