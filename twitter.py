#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import Counter
from datetime import datetime
from functools import partial
from pathlib import Path
import argparse
import json
import logging
import os
import sys

import matplotlib.pyplot as plt
import twitter_scraper as tw

__prog_name__ = 'TwitterScraper'

HERE = os.path.abspath(os.path.dirname(__file__))
DIR_DATA = os.path.join(HERE, 'data')

LOG_FMT = '%(asctime)s | %(levelname)s | %(message)s'
LOG_DATE_FMT = '%F %H:%M:%S'
logging.basicConfig(level=logging.INFO, format=LOG_FMT, datefmt=LOG_DATE_FMT)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


dump_pretty_json = partial(json.dump, cls=DateTimeEncoder, indent=4, separators=(',', ': '))


def cli():
    parser = argparse.ArgumentParser(prog=f'{__prog_name__}')
    subparsers = parser.add_subparsers(help='execution modes', dest='exec_mode')

    # ----- Mode 'down' -----
    sub = subparsers.add_parser('down', help='download target twitter feed')
    sub.add_argument('username', metavar='NAME', type=str, help='target twitter profile')
    sub.add_argument('--pages', '-p', metavar='PAGES', type=int, help='number of pages to fetch', default=20)

    # ----- Mode plot -----
    sub = subparsers.add_parser('plot', help='plot twitter feed data')
    sub.add_argument("filename", metavar='FILE', help="data to visualize", type=str)
    sub.add_argument("--show", "-s", metavar='PLOTNAME', help="available plots: 'activity'", type=str, default='activity')

    args = parser.parse_args()

    if args.exec_mode == 'down':
        download_history(args.username, args.pages)
    elif args.exec_mode == 'plot':
        filename = os.path.abspath(args.filename)
        twitter_data = load_twitter_data(filename)
        plot_tweet_activity(twitter_data)
    else:
        parser.print_help()


def mkdir(dirname):
    """
    Make a directory

    Args:
        :dirname: (str) path name
    """

    Path(dirname).mkdir(parents=True, exist_ok=True)


def load_twitter_data(filename):
    """
    Load twitter data from a file

    Args:
        :filename: (str) path of the file to load

    Returns:
        :twitter_data: (dict) dictionary with twitter data
    """

    with open(str(filename), "r") as fp:
        twitter_data = json.load(fp)
    return twitter_data


def download_history(username, pages):
    """
    Download tweets and save data on disk

    Args:
        :username: (str) target twitter account
        :pages: (int) number of pages to download
    """

    profile = tw.Profile(username)
    logging.info(f"Target: {username} ({profile.name}) | {profile.followers_count:,} followers")

    logging.info(f"Downloading tweets ({pages} pages)...")
    tweets = list(tw.get_tweets(username, pages))
    logging.info(f"Downloaded {len(tweets)} tweets...")

    mkdir(DIR_DATA)
    now = datetime.now()
    dir_user_data = os.path.join(DIR_DATA, f"{username}_{now.strftime('%F_%H%M')}")
    mkdir(dir_user_data)
    file_user_data = os.path.join(dir_user_data, "data.json")

    data = {
        "profile": profile.to_dict(),
        "history": tweets,
    }
    logging.info(f"Saving data: {file_user_data}...")
    with open(file_user_data, 'w') as fp:
        dump_pretty_json(data, fp)


def plot_tweet_activity(twitter_data):
    """
    Visualize daily tweet activity

    Args:
        :twitter_data: (dict) twitter data
    """

    tweets = twitter_data['history']
    profile = twitter_data['profile']
    username = profile['username']

    tweets_per_day = Counter()
    for tweet in tweets:
        time = datetime.fromisoformat(tweet['time'])
        tweets_per_day[datetime(time.year, time.month, time.day)] += 1

    logging.info(f"Plotting tweet activity for {username}...")
    dates = list(tweets_per_day.keys())
    num_tweets = list(tweets_per_day.values())

    plt.plot_date(dates, num_tweets, '.', color='black')
    plt.gcf().autofmt_xdate()
    plt.title(f"Tweet activity @{username} (total = {len(tweets)})")
    plt.xlabel("Time")
    plt.ylabel("Number of tweets")
    plt.show()


if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        logging.error(f"Exit...")
        sys.exit(1)
