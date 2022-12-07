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
            sentiment = extract_value_if_key_exists('sentiment', tweet)
            # OPTIONALLY CHANGE TO SENTIMENT SIZE FOR MORE CLASSIFIERS
            if sentiment is None:
                text = extract_value_if_key_exists('text', tweet)
                tweet['sentiment'] = [sentiment_classifier(text), bert_classifier(text)]

                _id = extract_value_if_key_exists('id', tweet)
                tweet_collection.flow_in(key=_id, data=tweet)

                print(f"tweet {counter}: annotated with sentiment")
            else:
                print(f"SKIP: Tweet {counter}: already annotated with sentiment")
            counter = counter + 1
    except Exception as e:
        print(e)


def unpack_data(input_dict: dict):
    if 'data' in input_dict.keys():
        return unpack_data(input_dict.pop('data'))
    else:
        return input_dict


def read_from_csv(csv_filename: str):
    df = pd.read_csv(csv_filename)
    print(df)
    list_of_jsons = df.to_json(orient='records', lines=True).splitlines()
    return [json.loads(tweet) for tweet in list_of_jsons]


def extract_value_if_key_exists(key: str, input_dict: dict):
    if input_dict is None:
        return None

    if f'{key}' in input_dict.keys():
        val = input_dict[f'{key}']
    elif f'data.{key}' in input_dict.keys():
        val = input_dict[f'data.{key}']
    else:
        val = input_dict
    return val


def create_heatmap():
    pass


def curate_tweets():
    curated_tweet_list = []
    for tweet in tweet_collection.flow_out():
        data = unpack_data(tweet)
        sentiment = extract_value_if_key_exists('sentiment', data)
        user = extract_value_if_key_exists('user', data)
        user_loc = extract_value_if_key_exists('location', user)

        geo = extract_value_if_key_exists('geo', data)
        coordinates = extract_value_if_key_exists('coordinates', data)

        output = {
            'sentiment': sentiment,
            'location': user_loc,
            'geo': geo,
            'coordinates': coordinates
            # add fields here
        }
        curated_tweet_list.append(output)


def main():
    print("OTTAWA COVID TWEET ANALYZER")
    print("Sourcing and Loading Tweets into DB")
    # retrieve_data()
    # READ TWEETS FROM CSV
    # tweets = read_from_csv("all_tweets.csv")
    # store_tweets(tweets, tweet_collection)

    # Run sentiment pipeline
    sentiment_analysis(tweet_collection)

    # Visualize Data
    # create_heatmap()
    # Heatmap
    curate_tweets()


if __name__ == "__main__":
    main()
