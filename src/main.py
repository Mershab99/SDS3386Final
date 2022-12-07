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
        retrieve_tweets = tweet_store.retrieve_tweets()
        counter = 1
        for tweet in retrieve_tweets:
            tweet = remove_data_tag(tweet)
            if 'sentiment' in tweet.keys():
                tweet.pop('sentiment')

            text = extract_value_if_key_exists('text', tweet)
            tweet['classifier_dilbert'] = sentiment_classifier(text)[0]
            tweet['classifier_bert'] = bert_classifier(text)[0]

            _id = int(extract_value_if_key_exists('id', tweet))
            tweet_collection.flow_in(key=_id, data=tweet)

            print(f"tweet {counter}: annotated with sentiment")
            counter = counter + 1
    except Exception as e:
        print(e)



def read_from_csv(csv_filename: str):
    df = pd.read_csv(csv_filename)
    print(df)
    list_of_jsons = df.to_json(orient='records', lines=True).splitlines()
    jsonified_tweets = [remove_data_tag(json.loads(tweet)) for tweet in list_of_jsons]
    return jsonified_tweets
def remove_data_tag(input_dict: dict):
    new_dict = {}
    for key, value in input_dict.items():
        if key.startswith('data.'):
            new_key = key.replace('data.', '')
            new_dict[new_key] = input_dict[key]
        else:
            new_dict[key] = input_dict[key]
    return new_dict

def extract_value_if_key_exists(key: str, input_dict: dict):
    if input_dict is None:
        return None

    if f'{key}' in input_dict.keys():
        val = input_dict[f'{key}']
    elif f'data.{key}' in input_dict.keys():
        val = input_dict[f'data.{key}']
    else:
        val = None
    return val


def create_heatmap():
    curated_tweets = curate_tweets()
    curated_ds = Datastore('curated')
    curated_ds.flow_in()
    x = 1

def curate_tweets():
    curated_tweet_list = []
    for tweet in tweet_collection.retrieve_tweets():
        tweet = remove_data_tag(tweet)
        sentiment_bert = extract_value_if_key_exists('classifier_dilbert', tweet)
        sentiment_dilbert = extract_value_if_key_exists('classifier_bert', tweet)

        user = extract_value_if_key_exists('user', tweet)
        user_loc = extract_value_if_key_exists('location', user)
        user_id = extract_value_if_key_exists('location', user)
        user_name = extract_value_if_key_exists('name', user)
        user_screen_name = extract_value_if_key_exists('screen_name', user)

        geo = extract_value_if_key_exists('geo', tweet)
        coordinates = extract_value_if_key_exists('coordinates', tweet)

        text = extract_value_if_key_exists('text', tweet)

        output = {
            'sentiment_bert': sentiment_bert[0] if type(sentiment_bert) is list else sentiment_bert,
            'sentiment_dilbert': sentiment_dilbert[0]if type(sentiment_dilbert) is list else sentiment_dilbert,
            'location': user_loc,
            'geo': geo,
            'coordinates': coordinates,
            'retweet_count': extract_value_if_key_exists('retweet_count', tweet),
            'user.location': user_loc,
            'user.screen_name': user_screen_name,
            'user.name': user_name,
            'user.id': user_id
            # add fields here
        }
        curated_tweet_list.append(output)
    return curated_tweet_list

def cp(ds1: Datastore, ds2: Datastore):
    ds1_tweets = ds1.retrieve_tweets()
    tweets_for_ds2 = []
    for tweet in ds1_tweets:
        tweet = remove_data_tag(tweet)
        if 'user' in tweet.keys():
            user = extract_value_if_key_exists('user', tweet)
            tweet['user.location'] = extract_value_if_key_exists('location', user)
            tweet['user.screen_name'] = extract_value_if_key_exists('screen_name', user)
            tweet['user.name'] = extract_value_if_key_exists('name', user)
            tweet['user.id'] = extract_value_if_key_exists('id', user)

        tweets_for_ds2.append(tweet)
    for tweet in tweets_for_ds2:
        ds2.flow_in(tweet['id'], tweet)
        print('copied tweet')
    x = 1
def main():
    print("OTTAWA COVID TWEET ANALYZER")
    print("Sourcing and Loading Tweets into DB")
    # retrieve_data()
    # READ TWEETS FROM CSV
    #tweets = read_from_csv("tweets.csv")
    #tweets1 = read_from_csv("tweets1.csv")
    #store_tweets(tweets, tweet_collection)
    #store_tweets(tweets1, tweet_collection)

    # Run sentiment pipeline
    #sentiment_analysis(tweet_collection)

    # Visualize Data
    #create_heatmap()
    # Heatmap
    #curate_tweets()
    cp(tweet_collection, Datastore('output_tweets'))

if __name__ == "__main__":
    main()
