from bs4 import BeautifulSoup
import requests
import logging
from dateutil import parser

logger = logging.getLogger(__name__)

def parse_date(date_str):
    try:
        return parser.parse(date_str)
    except Exception:
        return None

def url2soup(url):
    try:
        r = requests.get(url)
        content = r.content.decode("utf8")
        soup = BeautifulSoup(content, "html5lib")
        return soup
    except UnicodeEncodeError:
        logger.exception("Could not decode page: %s" % url)
    except Exception:
        logger.exception("An error occurred while downloading html from url: %s" % url)

