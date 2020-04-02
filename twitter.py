#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import Counter
from datetime import datetime
import argparse

import matplotlib.pyplot as plt
import twitter_scraper as tw

NUM_PAGES = 25


def cli():
    parser = argparse.ArgumentParser(description='Twitter scraper')
    parser.add_argument('username', metavar='NAME', type=str, help='target twitter profile')
    args = parser.parse_args()

    username = args.username
    plot_tweet_activity(username)


def plot_tweet_activity(username):
    profile = tw.Profile(username)
    print(f"Target: {username} ({profile.name}) | {profile.followers_count} followers\n")

    print("Downloading tweets...")
    tweets = list(tw.get_tweets(username, NUM_PAGES))
    print(f"Downloaded {len(tweets)} tweets...\n")

    print("Counting tweets per day...")
    tweets_per_day = Counter()
    for tweet in tweets:
        time = tweet['time']
        tweets_per_day[datetime(time.year, time.month, time.day)] += 1

    print(f"Plotting tweet activity")
    dates = list(tweets_per_day.keys())
    num_tweets = list(tweets_per_day.values())

    plt.plot_date(dates, num_tweets, '.')
    plt.gcf().autofmt_xdate()
    plt.title("Tweet activity")
    plt.xlabel("Time")
    plt.ylabel("Number of tweets")
    plt.show()


if __name__ == '__main__':
    cli()
