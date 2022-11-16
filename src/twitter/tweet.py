import tweepy
import os

max_tweets = 10000


def search_tweets(api: tweepy.API):
    query = ""
    distance = f"{int(os.environ['REVERSE_GEOCODE_DISTANCE_M']) / 1000}km"

    # TODO: FIX ME STOLEN CODE
    searched_tweets = []
    last_id = -1
    while len(searched_tweets) < max_tweets:
        count = max_tweets - len(searched_tweets)
        new_tweets = api.search_tweets(q=query, geocode=f"{os.environ['LAT']},{os.environ['LNG']},{distance}",
                                       count=count, max_id=str(last_id - 1))

        if not new_tweets:
            break

        new_tweets_list = new_tweets['statuses']

        searched_tweets.extend(new_tweets_list)
        last_id = new_tweets_list[:1][0]['id']
        print(f"Cached Tweets: {len(searched_tweets)} ")

    return searched_tweets
