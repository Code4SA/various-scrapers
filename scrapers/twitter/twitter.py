from __future__ import print_function
import json

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy


from accounts import accounts

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def __init__(self, accounts):
        self.accounts = accounts

    def on_data(self, data):
        js = json.loads(data)
        if js["user"]["id_str"] in self.accounts:
            text = js["text"].encode("utf8")
            print("%s> %s" % (js["user"]["screen_name"], text))
        return True

    def on_error(self, status):
        print(status)

consumer_key = "rawN6bVWzbsvdKh9R1BYw"
consumer_secret = "yv0YWyommuac4caIlqd5245spIeAnegIZlb4Q5iRk"
access_token = "21011010-rmh8p683Hs8ljNJFKnKdhnxj84dVBF30KeGKJT9MI"
access_token_secret = "Ad5eZ3j9AmAkrvZpGVzICWKbzHOnJ8FaznDVD06xXWcMr"

if __name__ == '__main__':
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    ids = set()
    for u in accounts:
        if type(u) == tuple:
            id = u[1]
        else:
            u = u.strip()
            id = api.get_user(u).id
            print('("%s", "%s")' % (u, id))
        ids.add(id)
    l = StdOutListener(ids)
    stream = Stream(auth, l)
    js = stream.filter(follow=list(ids))
