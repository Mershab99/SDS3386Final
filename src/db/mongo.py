import os
from datetime import datetime

from pymongo import MongoClient


class Datastore:
    def __init__(self, collection):
        self.db = MongoClient(
            host=os.environ['MONGO_HOST'], port=int(os.environ.get('MONGO_PORT', 27017)),
            username=os.environ.get('MONGO_USERNAME', ""), password=os.environ.get('MONGO_PASSWORD', "")
        ).get_database(os.environ['MONGO_DB'])
        self.collection = self.db.get_collection(collection)

    def flow_in(self, key, data):
        flow = {
            'key': key,
            'data': data,
            'insert_time': datetime.now().__str__()
        }

        if self.collection.find_one({'key': key}) is None:
            self.collection.insert_one(flow)
        else:
            self.collection.replace_one({'key': key}, flow)
        return flow

    def find_by_key(self, key):
        obj = self.collection.find_one({
            'key': key
        })
        if obj is None:
            raise KeyError("No object found for key:{}".format(key))
        obj.pop('_id')
        return obj

    def find_by_field(self, field_name, field_value):
        obj = self.collection.find_one({
            f'data.{field_name}': field_value
        })
        if obj is None:
            raise KeyError("No object found for value: {} in field :{}".format(field_value, field_name))
        obj.pop('_id')
        return obj

    def find_many_by_key(self, key):
        obj = self.collection.find({
            'key': key
        })
        if obj is None:
            raise KeyError("No object found for key:{}".format(key))
        obj.pop('_id')
        return obj

    def find_many_by_field(self, field_name, field_value):
        obj = self.collection.find({
            f'data.{field_name}': field_value
        })
        if obj is None:
            raise KeyError("No object found for value: {} in field :{}".format(field_value, field_name))
        obj.pop('_id')
        return obj


def store_tweets(tweets: list, tweet_collection: Datastore):
    counter = 0
    for tweet in tweets:
        tweet_collection.flow_in(key=tweet['id'], data=tweet)
        print(f"Tweet {counter} Stored")
        counter = counter + 1


def store_geocodes(places, geocode_store):
    for place in places['places']:
        geocode_store.flow_in(key=place['id'], data=place)
        print("Place Stored")
