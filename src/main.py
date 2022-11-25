import os

import tweepy
from tweepy.parsers import JSONParser

from db.mongo import Datastore, store_geocodes, store_tweets
from twitter.geo import reverse_geocode_ottawa
from twitter.tweet import search_tweets

os.environ['LAT'], os.environ['LNG'] = "45.425187", "-75.699813"
os.environ['REVERSE_GEOCODE_DISTANCE_M'] = "15000"


def main():
    try:
        auth = tweepy.OAuth1UserHandler(
            os.environ.get('TWITTER_CONSUMER_KEY'), os.environ.get('TWITTER_CONSUMER_SECRET'),
            os.environ.get('TWITTER_ACCESS_TOKEN'), os.environ.get('TWITTER_ACCESS_TOKEN_SECRET'))

        api = tweepy.API(auth, parser=JSONParser())

        geocode_collection = Datastore('geo_codes')
        tweet_collection = Datastore('tweets')

        print("OTTAWA COVID TWEET ANALYZER")

        places = reverse_geocode_ottawa(api)

        store_geocodes(places, geocode_collection)

        tweets = search_tweets(api)
        store_tweets(tweets, tweet_collection)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
