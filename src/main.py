import os

import tweepy
from tweepy.parsers import JSONParser

from db.mongo import Datastore, store_geocodes, store_tweets
from twitter.geo import reverse_geocode_ottawa
from twitter.tweet import search_tweets
from analyze.sentiment import sentiment_classifier, bert_classifier

os.environ['LAT'], os.environ['LNG'] = "45.425187", "-75.699813"
os.environ['REVERSE_GEOCODE_DISTANCE_M'] = "15000"

geocode_collection = Datastore('geo_codes')
tweet_collection = Datastore('tweets')


def retrieve_data():
    try:
        auth = tweepy.OAuth1UserHandler(
            os.environ.get('TWITTER_CONSUMER_KEY'), os.environ.get('TWITTER_CONSUMER_SECRET'),
            os.environ.get('TWITTER_ACCESS_TOKEN'), os.environ.get('TWITTER_ACCESS_TOKEN_SECRET'))

        api = tweepy.API(auth, parser=JSONParser())

        places = reverse_geocode_ottawa(api)

        store_geocodes(places, geocode_collection)

        tweets = search_tweets(api)
        store_tweets(tweets, tweet_collection)

    except Exception as e:
        print(e)


def sentiment_analysis(tweet_store: Datastore):
    try:
        retrieve_tweets = tweet_store.flow_out()

        for tweet in retrieve_tweets:
            # OPTIONALLY CHANGE TO SENTIMENT SIZE FOR MORE CLASSIFIERS
            if 'sentiment' not in tweet['data'].keys():
                text = tweet['data']['text']
                tweet['data']['sentiment'] = [sentiment_classifier(text), bert_classifier(text)]

                tweet_store.flow_in(key=tweet['data']['id'], data=tweet)
                print("tweet annotated with sentiment")
    except Exception as e:
        print(e)


def main():
    print("OTTAWA COVID TWEET ANALYZER")
    print("Sourcing and Loading Tweets into DB")
    retrieve_data()
    # Run sentiment pipeline
    sentiment_analysis(tweet_collection)

    # Visualize Data


if __name__ == "__main__":
    main()
