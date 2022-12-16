from db.mongo import Datastore

geocode_collection = Datastore('geo_codes')
tweet_collection = Datastore('tweets')


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


def remove_data_tag(input_dict: dict):
    new_dict = {}
    for key, value in input_dict.items():
        if key.startswith('data.'):
            new_key = key.replace('data.', '')
            new_dict[new_key] = input_dict[key]
        else:
            new_dict[key] = input_dict[key]
    return new_dict


curated_tweet_list = []
for tweet in tweet_collection.retrieve_tweets():
    try:
        tweet = remove_data_tag(tweet)
        sentiment_bert = extract_value_if_key_exists('classifier_dilbert', tweet)
        sentiment_dilbert = extract_value_if_key_exists('classifier_bert', tweet)

        user = extract_value_if_key_exists('user', tweet)
        user_loc = extract_value_if_key_exists('location', user)
        user_id = extract_value_if_key_exists('id', user)
        user_name = extract_value_if_key_exists('name', user)
        user_screen_name = extract_value_if_key_exists('screen_name', user)

        geo = extract_value_if_key_exists('geo', tweet)
        coordinates = extract_value_if_key_exists('coordinates', tweet)

        text = extract_value_if_key_exists('text', tweet)

        output = {
            'sentiment_bert': sentiment_bert[0] if type(sentiment_bert) is list else sentiment_bert,
            'sentiment_dilbert': sentiment_dilbert[0] if type(sentiment_dilbert) is list else sentiment_dilbert,
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
    except Exception as e:
        print(e)

x = 1