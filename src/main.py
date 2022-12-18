import json
import os
import time

import tweepy
from tweepy.parsers import JSONParser

from db.mongo import Datastore, store_geocodes, store_tweets
from twitter.geo import retrieve_places, pull_places
from twitter.tweet import search_tweets
from analyze.sentiment import sentiment_classifier, bert_classifier
import pandas as pd

os.environ['LAT'], os.environ['LNG'] = "45.425187", "-75.699813"
os.environ['REVERSE_GEOCODE_DISTANCE_M'] = "150000"

geocode_collection = Datastore('geo_codes')
tweet_collection = Datastore('tweets')

auth = tweepy.OAuth1UserHandler(
    os.environ.get('TWITTER_CONSUMER_KEY'), os.environ.get('TWITTER_CONSUMER_SECRET'),
    os.environ.get('TWITTER_ACCESS_TOKEN'), os.environ.get('TWITTER_ACCESS_TOKEN_SECRET'))

api = tweepy.API(auth, parser=JSONParser())


def retrieve_data():
    try:
        output_tweets = []
        tweets = search_tweets(api)
        for tweet in tweets:
            output = {
                'time': tweet['created_at'],
                'fav_count': tweet['favorite_count'],
                'id': tweet['id'],
                'lang': tweet['lang'],
                'possibly_sensitive': False,
                'source': tweet['source'],
                'text': tweet['text'],
                'user.id': tweet['user']['id'],
                'user.location': tweet['user']['location'],
                'user.name': tweet['user']['name'],
                'user.handle': tweet['user']['screen_name']
            }

            output_tweets.append(output)
        return output_tweets
    except Exception as e:
        print(e)


def sentiment_analysis(tweets: list):
    try:
        counter = 1
        output_tweets = []
        for tweet in tweets:
            # tweet = remove_data_tag(tweet)

            text = extract_value_if_key_exists('text', tweet)
            if text is None:
                continue
            tweet['classifier_dilbert.label'] = sentiment_classifier(text)[0]['label']
            tweet['classifier_dilbert.score'] = sentiment_classifier(text)[0]['score']
            tweet['classifier_bert.label'] = bert_classifier(text)[0]['label']
            tweet['classifier_bert.score'] = bert_classifier(text)[0]['score']

            output_tweets.append(tweet)

            print(f"tweet {counter}: annotated with sentiment")
            counter = counter + 1
        return output_tweets
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


def convert_places_to_csv(ds: Datastore):
    places = ds.collection.find({})
    df_list = []
    for place in places:
        bbox = place['data']['bounding_box']['coordinates'][0]
        name = place['data']['name']
        print(name)
        print(bbox)
        temp_frame = pd.DataFrame([pd.read_json(json.dumps({
            'name': name,
            'bounding_box': bbox
        }), typ='series')])

        df_list.append(temp_frame)

    master_df = pd.concat(df_list)
    return master_df


def convert_json_to_df(tweets: list):
    df_list = []
    for tweet in tweets:
        # temp_frame = pd.read_json(json.dumps(tweet))
        temp_frame = pd.DataFrame([pd.read_json(json.dumps(tweet), typ='series')])
        df_list.append(temp_frame)

    master_df = pd.concat(df_list)
    return master_df


def get_master_df(tweet_collection: Datastore):
    tweets = tweet_collection.retrieve_tweets()
    master_df = convert_json_to_df(tweets)
    print(master_df)
    return master_df


def main():
    print("OTTAWA COVID TWEET ANALYZER")
    print("Sourcing and Loading Tweets into DB")
    # retrieved_tweets = retrieve_data()
    # store_tweets(retrieved_tweets, tweet_collection)

    # convert_json_to_df(tweets=retrieved_tweets)
    # READ TWEETS FROM CSV
    # tweets = read_from_csv("tweets.csv")
    # tweets1 = read_from_csv("tweets1.csv")

    #all_tweets = [tweet for tweet in tweet_collection.retrieve_tweets()]

    #start = time.perf_counter()
    # Run sentiment pipeline
    #analyzed_tweets = sentiment_analysis(all_tweets)
    #end = time.perf_counter() - start
    #print(f'Sentiment analysis finished in: {end}')
    # store_tweets(all_tweets, tweet_collection)
    #master_df = get_master_df(tweet_collection)
    #print(master_df)

    # master_df.to_csv("tweet_dump1.csv")

    places = pull_places(api)
    store_geocodes(places, geocode_collection)
    places_df = convert_places_to_csv(geocode_collection)
    places_df.to_csv("places.csv")

if __name__ == "__main__":
    main()
