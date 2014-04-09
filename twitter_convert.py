from __future__ import print_function
import sys

from tweepy import OAuthHandler
import tweepy
import settings

from accounts import accounts
def run(handles, settings):
    with open(handles) as fp:
        for handle in fp:
            handle = handle.strip()
            auth = OAuthHandler(settings.consumer_key, settings.consumer_secret)
            auth.set_access_token(settings.access_token, settings.access_token_secret)
            api = tweepy.API(auth)
            id = api.get_user(handle).id
            print('("%s","%s"),' % (handle, id))

handles = sys.argv[1]
run(handles, settings)
