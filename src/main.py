import json
import os

import tweepy
from tweepy.parsers import JSONParser

from db.mongo import Datastore, store_geocodes, store_tweets
from twitter.geo import reverse_geocode_ottawa
from twitter.tweet import search_tweets
from analyze.sentiment import sentiment_classifier, bert_classifier
import pandas as pd

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
        counter = 1
        for tweet in retrieve_tweets:
            tweet = unpack_data(tweet)

            # OPTIONALLY CHANGE TO SENTIMENT SIZE FOR MORE CLASSIFIERS
            if 'sentiment' not in tweet.keys():
                if 'text' in tweet.keys():
                    text = tweet['text']
                elif 'data.text' in tweet.keys():
                    text = tweet['data.text']
                tweet['sentiment'] = [sentiment_classifier(text), bert_classifier(text)]

                if 'id' in tweet.keys():
                    _id = tweet['id']
                elif 'data.id' in tweet.keys():
                    _id = tweet['data.id']
                tweet_collection.flow_in(key=_id, data=tweet)

                print(f"tweet {counter}: annotated with sentiment")
            else:
                print(f"SKIP: Tweet {counter}: already annotated with sentiment")
            counter = counter + 1
    except Exception as e:
        print(e)


def unpack_data(input: dict):
    if 'data' in input.keys():
        return unpack_data(input.pop('data'))
    else:
        return input


def read_from_csv(csv_filename: str):
    df = pd.read_csv(csv_filename)
    print(df)
    list_of_jsons = df.to_json(orient='records', lines=True).splitlines()
    return [json.loads(tweet) for tweet in list_of_jsons]

def main():
    print("OTTAWA COVID TWEET ANALYZER")
    print("Sourcing and Loading Tweets into DB")
    # retrieve_data()
    # READ TWEETS FROM CSV
    tweets = read_from_csv("tweets.csv")
    store_tweets(tweets, tweet_collection)

    # Run sentiment pipeline
    sentiment_analysis(tweet_collection)

    # Visualize Data


if __name__ == "__main__":
    main()
