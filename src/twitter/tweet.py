import tweepy
import os

MAX_TWEETS = int(os.environ.get('MAX_TWEETS', 1000))


def search_tweets(api: tweepy.API):
    query = ""
    distance = f"{int(os.environ['REVERSE_GEOCODE_DISTANCE_M']) / 1000}km"

    searched_tweets = []
    last_id = -1
    try:
        while len(searched_tweets) < MAX_TWEETS:
            count = MAX_TWEETS - len(searched_tweets)
            new_tweets = api.search_tweets(q=query, geocode=f"{os.environ['LAT']},{os.environ['LNG']},{distance}",
                                           count=count, max_id=str(last_id - 1))

            if not new_tweets:
                break

            new_tweets_list = new_tweets['statuses']

            searched_tweets.extend(new_tweets_list)
            last_id = new_tweets_list[:1][0]['id']
            print(f"Cached Tweets: {len(searched_tweets)} ")
    except Exception:
        pass
    return searched_tweets
