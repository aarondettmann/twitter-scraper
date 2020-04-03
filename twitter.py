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
    sub.add_argument("data", metavar='FOLDER', help="data to visualize", type=str)
    sub.add_argument("--show", "-s", metavar='PLOTNAME', help="available plots: 'activity'", type=str, default='activity')

    args = parser.parse_args()

    if args.exec_mode == 'down':
        username = args.username
        pages = args.pages

        download_history(username, pages)
        # plot_tweet_activity(username, pages)

    elif args.exec_mode == 'plot':
        pass


def mkdir(dir_path):
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def download_history(username, pages):
    """
    Download tweets. Data is stored on disk.

    Args:
        :username: (str) target twitter account
        :pages: (int) number of pages to download
    """

    profile = tw.Profile(username)
    logging.info(f"Target: {username} ({profile.name}) | {profile.followers_count} followers")

    logging.info(f"Downloading tweets ({pages} pages)...")
    tweets = list(tw.get_tweets(username, pages))
    logging.info(f"Downloaded {len(tweets)} tweets...")

    mkdir(DIR_DATA)
    now = datetime.now()
    dir_user_data = os.path.join(DIR_DATA, f"{username}_{now.strftime('%F_%H%M')}")
    mkdir(dir_user_data)
    file_user_data = os.path.join(dir_user_data, "tweets.json")

    with open(file_user_data, 'w') as fp:
        dump_pretty_json({"history": tweets}, fp)


def plot_tweet_activity(username, pages):
    profile = tw.Profile(username)
    logging.info(f"Target: {username} ({profile.name}) | {profile.followers_count} followers")

    logging.info(f"Downloading tweets ({pages} pages)...")
    tweets = list(tw.get_tweets(username, pages))
    logging.info(f"Downloaded {len(tweets)} tweets...")

    logging.info("Counting tweets per day...")
    tweets_per_day = Counter()
    for tweet in tweets:
        time = tweet['time']
        tweets_per_day[datetime(time.year, time.month, time.day)] += 1

    logging.info(f"Plotting tweet activity")
    dates = list(tweets_per_day.keys())
    num_tweets = list(tweets_per_day.values())

    plt.plot_date(dates, num_tweets, '.', color='black')
    plt.gcf().autofmt_xdate()
    plt.title(f"Tweet activity @{username} (total = {len(tweets)})")
    plt.xlabel("Time")
    plt.ylabel("Number of tweets")
    plt.show()


if __name__ == '__main__':
    cli()
