import os

import tweepy


def reverse_geocode_ottawa(api: tweepy.API):
    places = api.reverse_geocode(os.environ['LAT'], os.environ['LNG'],
                                 accuracy=os.environ['REVERSE_GEOCODE_DISTANCE_M'])
    return places['result']
