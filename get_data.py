# -*- coding: utf-8 -*-
from __future__ import print_function
import re
import os
import random
import twitter
import markov

twitter = twitter.Api(
    consumer_key='g8h3IQfynzRHhasTevaaP3u0W',
    consumer_secret='rrpVpTfHaolGjBY83uGcCdrEiTdlm4NSiOECZJVdSaFZlTWqWU',
    access_token_key='818849823239655424-pLirMKDD87LoQDVVxLoNlhudPiHqeKU',
    access_token_secret='4L7QjjnEBflnlhseAm8WeyEoCArwcXiGFLmCP2lGtHJUI')


def generate_tweet(file):
    table = markov.generate_table(file)
    tweet_text = "".join(markov.generate_markov_text(10, 3, table))
    return tweet_text


def clean(tweet_text):
    # url_regex = r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"
    # pattern = re.compile(url_regex)
    # result = pattern.match(tweet_text)
    cleaned = tweet_text.replace('&amp;', '&')
    cleaned = tweet_text.replace('…', ' ')
    return cleaned


def save_tweets(handle, num_results):
    output_dir = "tweets/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    query_handle = "%3A" + handle
    num_results = str(num_results)
    results = twitter.GetSearch(raw_query="q=from%s&count=%s" %
                                (query_handle, num_results))

    output_file = "%s%s_tweets.txt" % (output_dir, handle)

    with open(output_file, 'a') as out:
        for tweet in results:
            text = (tweet.AsDict()['text']).encode('utf-8')
            print(text, file=out, end=' ')
    out.close()


def get_user_metadata(handle):
    query_handle = "%3A" + handle
    num_results = "1"
    results = twitter.GetSearch(raw_query="q=from%s&count=%s" %
                                (query_handle, num_results))

    print(results)
    first_tweet = results[0].AsDict()
    name = first_tweet['user']['name'].decode('utf-8')
    handle = first_tweet['user']['screen_name'].decode('utf-8')
    pic_url = first_tweet['user']['profile_image_url']
    metadata = {'name': name, 'handle': handle, 'pic_url': pic_url}
    return metadata


#Call this function to get all the data needed to write a random tweet
def get_tweet(handle):
    src_dir = "tweets/"
    if not os.path.exists(src_dir + handle + "_tweets.txt"):
        save_tweets(handle, 1000)

    tweet_data = get_user_metadata(handle)
    tweet_text = generate_tweet(["tweets/" + handle + "_tweets.txt"])
    tweet_data['tweet_text'] = clean(tweet_text)
    return tweet_data
