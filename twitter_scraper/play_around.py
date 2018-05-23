import tweepy
from twitter_scraper.config import *
from tweepy.streaming import StreamListener
from tweepy import Stream
import json


class twitter_listener(StreamListener):

    def on_data(self, data):
        j = json.loads(data)
        print(j["text"])
        return True

    def on_error(self, status):
        print(status)

if __name__ == "__main__":
    auth = tweepy.OAuthHandler(consumer_key=consumer_key, consumer_secret=consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    twitter_api = tweepy.API(auth)
    auth2 = tweepy.API(auth)

    twitter_stream = Stream(auth, twitter_listener())
    twitter_stream.filter(track=['mauriciomacri'])
    try:
        twitter_stream.sample()
    except:
        pass