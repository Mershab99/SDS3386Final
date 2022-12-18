import os

import tweepy


def retrieve_places(api: tweepy.API):
    places = api.reverse_geocode(lat=os.environ['LAT'], long=os.environ['LNG'],
                                 accuracy=int(os.environ['REVERSE_GEOCODE_DISTANCE_M']), granularity='neighborhood')
    return places['result']


def pull_places(api: tweepy.API):
    places = api.search_geo(lat=os.environ['LAT'], long=os.environ['LNG'])
    return places['result']
