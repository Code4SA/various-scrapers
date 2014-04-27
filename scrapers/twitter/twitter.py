from __future__ import print_function
import json
from datetime import datetime
import logging

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy

from ..config import db_insert, articles
from accounts import accounts

logger = logging.getLogger(__name__)

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def __init__(self, accounts):
        self.accounts = accounts

    def create_post(self, data):
        msg_id = data["id"]
        tweet_url = "https://twitter.com/%s/status/%s" % (data["user"]["screen_name"], msg_id)
        logger.info(data["text"])

        post = {
            "publication" : "Twitter",
            "id" : msg_id,
            "author" : data["user"]["screen_name"],
            "summary" : "",
            "published" : data["created_at"],
            "title" : "",
            "text" : data["text"],
            "owner" : "Twitter",
            "sub_type" : 1,
            "url" : tweet_url, 
            "downloaded_at" : datetime.now()
        }
        if not articles.find_one({"url" : tweet_url}):
            db_insert(post)

    def on_data(self, data):
        js = json.loads(data)
        try:
            if "delete" in js: return False
            post = self.create_post(js)
            db_insert(post)
        except Exception:
            logger.exception("Error when processing tweet: %s" % data)
        return True

    def on_error(self, status):
        logger.warn("Twitter stream error: %s" % status)

def run(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    ids = set(t[1] for t in accounts)
    l = StdOutListener(ids)
    stream = Stream(auth, l)
    js = stream.filter(follow=list(ids))
