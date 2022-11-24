import os

import tweepy
from db.mongo import Datastore
from tweepy.parsers import JSONParser
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

        geo_codes = Datastore('geo_codes')
        tweet_collection = Datastore('tweets')

        print("OTTAWA COVID TWEET ANALYZER")

        places = reverse_geocode_ottawa(api)
        for place in places['places']:
            geo_codes.flow_in(key=place['id'], data=place)
            print("Place Stored")
        tweets = search_tweets(api)
        counter = 0
        # TODO: test counter impl
        for tweet in tweets:
            tweet_collection.flow_in(key=tweet['id'], data=tweet)
            print(f"Tweet {counter} Stored")
            counter += 1

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
