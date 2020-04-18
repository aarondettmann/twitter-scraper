#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Download the Twitter history for a certain user account

Copyright (c) 2020 Aaron Dettmann
License: MIT
 _________________________________________
/ Fame is a vapor; popularity an          \
| accident; the only earthly certainty is |
\ oblivion. -- Mark Twain                 /
 -----------------------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
"""

from collections import Counter, OrderedDict
from functools import partial
from importlib import import_module
from pathlib import Path
import argparse
import datetime
import json
import logging
import os
import re
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%F %H:%M:%S',
)
logger = logging.getLogger(__name__)


COUNT = 0
def get_unique_id():
    """Return a unique number as string from a global counter"""
    global COUNT
    return (COUNT := COUNT + 1)


def truncate_filepath(filepath, max_len=50, basename_only=False):
    """
    Truncate a long filepath

    Args:
        :filepath: filepath to truncate
        :max_len: maximum string lenght to return
        :basename_only: if True, only use the basename of 'filepath'

    Returns:
        :trunc_string: truncated filepath
    """

    filepath = str(filepath)
    pathname = os.path.basename(filepath) if basename_only else filepath

    if len(pathname) > max_len:
        pathname = pathname[-max_len:]
        prefix = '...'
    else:
        prefix = '.../'

    return prefix + pathname


def import_module_by_name(module_name):
    """
    Import a module from a string

    Args:
        :module_name: (str) name of the module

    Returns:
        :module: (obj) loaded module (or None in case of error)
    """

    try:
        module = import_module(module_name)
    except ModuleNotFoundError:
        logger.error(f"Module {module_name!r} not found. Please install the module.")
        return None
    else:
        return module


error = False
# ----- Import non-standard libraries -----
xl = import_module_by_name("openpyxl")
tw = import_module_by_name("twitter_scraper")
if None in (xl, tw):
    error = True

# ----- Only support Python 3.8.x -----
PY_VERSION = sys.version_info
if not (PY_VERSION[0] == 3 and PY_VERSION[1] >= 8):
    logger.error("Python version 3.8.0 or higher is needed.")
    error = True

if error:
    sys.exit(1)

PROG_NAME = 'TwitterHistory'
HERE = os.path.abspath(os.path.dirname(__file__))
DIR_DATA = os.path.join(HERE, 'data')

XL_FILL_GREEN = xl.styles.PatternFill(
    start_color='A0D6B4',
    end_color='A0D6B4',
    fill_type='solid',
)

XL_FILL_RED = xl.styles.PatternFill(
    start_color='FFBABA',
    end_color='FFBABA',
    fill_type='solid',
)

XL_FONT_BOLD = xl.styles.Font(bold=True)


# See https://stackoverflow.com/questions/12122007/python-json-encoder-to-support-datetime
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        return super(DateTimeEncoder, self).default(obj)


dump_pretty_json = partial(
    json.dump,
    cls=DateTimeEncoder,
    indent=4,
    separators=(',', ': ')
)


def cli():
    parser = argparse.ArgumentParser(prog=f'{PROG_NAME}')
    subparsers = parser.add_subparsers(help='execution modes', dest='exec_mode')

    # Filter argument applies to mode 'xl' and mode 'down'
    filter_args = ['--filter', '-f']
    filter_kwargs = {
        'metavar': 'HASHTAGS or KEYWORDS',
        'nargs': '+',
        'type': str,
        'help': 'filter tweets by #hashtag or keyword (text and hashtags)',
    }

    # ----- Mode 'down' -----
    sub = subparsers.add_parser('down', help='download target twitter feed')
    sub.add_argument('usernames', metavar='NAMES', nargs='+', type=str, help='target twitter profile')
    sub.add_argument('--pages', '-p', metavar='PAGES', type=int, help='number of pages to fetch', default=200)
    sub.add_argument('--no-excel', action='store_true', help='do not convert data to exel file')
    sub.add_argument(*filter_args, **filter_kwargs)

    # ----- Mode 'xl' -----
    sub = subparsers.add_parser('xl', help='convert data to excel spreadsheet')
    sub.add_argument("path", metavar='FILE or DIRECTORY', help="data to convert", type=str)
    sub.add_argument(*filter_args, **filter_kwargs)

    args = parser.parse_args()

    if args.exec_mode == 'down':
        for username in args.usernames:
            username = username.strip().strip(',')  # Remove commas
            json_file = download_history(username, args.pages)
            excel_file = json_file.replace('.json', '.xlsx')
            # Convert data to Excel spreadsheet by default
            if not args.no_excel:
                twitter_data = load_twitter_data(json_file)
                convert_to_excel(twitter_data, excel_file, filters=args.filter)
    elif args.exec_mode == 'xl':
        if Path(args.path).is_file():
            if not args.path.endswith('.json'):
                logger.error(f"{truncate_filepath(args.path)!r} seems to be a file, but not recognized as JSON...")
                sys.exit(1)
            filenames = (args.path,)
        elif Path(args.path).is_dir():
            logger.info("Trying to locate JSON files...")
            filenames = list(Path(args.path).rglob('*.json'))
            if not filenames:
                logger.error(f"No JSON files found in {truncate_filepath(args.path)!r}...")
                sys.exit(1)
            for filename in filenames:
                logger.info(f"Found {truncate_filepath(filename)}...")
        else:
            logger.error(f"Input {truncate_filepath(args.path)!r} not recognized as file or directory")
            sys.exit(1)

        # Convert JSON to XLSX (Excel files)
        for filename in filenames:
            json_file = os.path.abspath(filename)
            excel_file = json_file.replace('.json', '.xlsx')
            twitter_data = load_twitter_data(json_file)
            convert_to_excel(twitter_data, excel_file, filters=args.filter)
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

    logger.info(f"Importing twitter data from file: {truncate_filepath(filename)}")
    with open(str(filename), "r") as fp:
        twitter_data = json.load(fp)

    logger.info(f"Found {len(twitter_data['history'])} tweets in imported file...")
    return twitter_data


def get_tweet_url(username, tweet_id):
    return f"https://twitter.com/{username}/status/{tweet_id}"


def download_history(username, pages):
    """
    Download tweets and save data on disk

    Args:
        :username: (str) target twitter account
        :pages: (int) number of pages to download

    Returns:
        :file_user_data: (str) file path for the downloaded user data
    """

    try:
        profile = tw.Profile(username)
        logger.info(f"Target: {username} ({profile.name}) | {profile.followers_count:,} followers")
    except:
        if username.startswith('#'):
            logger.info(f"Interpreting {username!r} as a hashtag...")
        else:
            logger.error(f"Failed to fetch username data for {username!r}")
        profile = None

    logger.info(f"Downloading tweets ({pages} pages)...")
    tweets = list(tw.get_tweets(username, pages))
    logger.info(f"Downloaded {len(tweets)} tweets...")

    now = datetime.datetime.now()
    dir_user_data = os.path.join(DIR_DATA, f"{username}_{now.strftime('%F_%H%M')}")
    mkdir(dir_user_data)
    file_user_data = os.path.join(dir_user_data, "data.json")

    profile_dict = profile.to_dict() if profile is not None else {}
    data = {
        "profile": profile_dict,
        "history": tweets,
    }
    logger.info(f"Saving data: {truncate_filepath(file_user_data)}")
    with open(file_user_data, 'w') as fp:
        dump_pretty_json(data, fp)

    return file_user_data


def daterange(start_date, end_date):
    """
    Yield datetime objects (delta = 1 day) between start and end date

    Args:
        :start_date: (obj) start date time object
        :end_date: (obj) end date time object

    Note:
        * https://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
    """

    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


def get_tweets_per_day(twitter_data, count_zero_days=True, include_retweet=True):
    """
    Return the number of tweets posted per day

    Args:
        :twitter_data: (dict) dictionary with twitter data
        :count_zero_days: (bool) if True, include days with zero tweets
        :include_retweet: (bool) if True, include retweets

    Returns:
        :tweets_per_day: (dict) dictionary with day (datetime object) and tweet count
    """

    tweets = get_tweets(twitter_data)
    logger.info(f"Counting tweets per day (including retweets: {include_retweet})...")

    tweets_per_day = Counter()
    for tweet in tweets:
        time = datetime.datetime.fromisoformat(tweet['time'])
        if tweet['isRetweet'] and not include_retweet:
            continue
        tweets_per_day[datetime.datetime(time.year, time.month, time.day)] += 1

    # Fill up the dictionary with zeros
    if count_zero_days:
        logger.info("Looking for days with zero tweets...")

        # Get start and end date
        all_dates = sorted(list(tweets_per_day.keys()))  # list of sorted dates
        start_date, end_date = all_dates[0], all_dates[-1]
        if end_date < start_date:
            start_date, end_date, = end_date, start_date

        logger.info(f"Date range is {start_date.strftime('%F')} to {end_date.strftime('%F')}")
        for day in daterange(start_date, end_date):
            tweets_per_day[datetime.datetime(day.year, day.month, day.day)] += 0

    tweets_per_day = _sort_date_dict(tweets_per_day)
    return tweets_per_day


def _sort_date_dict(date_dict):
    """
    Sort a dictionary with dates as keys in chronological order

    Args:
        :date_dict: (dict) dictionary (key must be dates in sortable format)

    Returns:
        :sorted_dict: (dict) dictionary sorted by keys
    """

    # Note: OrderedDict() should not be necessary in 3.8
    return OrderedDict({k: v for k, v in sorted(date_dict.items())})


def _sort_tweets_by_date(tweets):
    """
    Ensure that tweets objects are are sorted by date

    Args:
        :tweets: (list) Tweets from 'twitter_data'

    Returns:
        :tweets_sorted: (list) sorted list of Tweets
    """

    # Sanity check of date format. Date string in iso-format expected.
    # We assume that if first tweet looks okay, all will.
    time_first_tweet = tweets[0]['time']
    if not isinstance(time_first_tweet, str):
        logger.error(f"Date must be a string, not {type(time_first_tweet)}. Exit.")
        sys.exit(1)

    match_iso8601 = re.compile(
       r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-' +
       r'(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9])' +
       r':([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?' +
       r'(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'
    ).match

    if match_iso8601(time_first_tweet) is None:
        logger.error(f"Date does not look like valid iso-format ({time_first_tweet!r}). Exit.")
        sys.exit(1)

    len_orig = len(tweets)
    # Add unique ID as suffix to timestamps (as strings), since in some special
    # cases, there can be two different tweets which have the exact same timestamp.
    tweets_as_date_dict = _sort_date_dict(
        {
            tweet['time'] + str(get_unique_id()): tweet
            for tweet in tweets
        }
    )
    tweets_sorted = list(tweets_as_date_dict.values())
    if len(tweets_sorted) != len_orig:
        logger.error(f"Some tweets went missing while sorting... Exit.")
        sys.exit(1)
    return tweets_sorted


def get_tweets(twitter_data, sort=True):
    """
    Return tweets from twitter data or return error

    Args:
        :twitter_data: (dict) dictionary with twitter data
        :sort: (bool) if true tweets will be sorted by date

    Returns:
        :tweets: (list) Tweets
    """

    tweets = twitter_data.get('history', None)
    if tweets is None:
        logger.error("Failed to retrieve tweets... Exit.")
        sys.exit(1)

    if sort:
        tweets = _sort_tweets_by_date(tweets)

    return tweets


def filter_tweets(tweets, filter_kw):
    """
    Filter tweets by a #hashtag or keyword

    Args:
        :tweets: (list) Tweets from 'twitter_data'
        :filter_kw: (str) filter keyword

    Returns:
        :filtered_tweets: (list) Filtered tweets from 'twitter_data'

    Note:
        * If 'filter_kw' starts with '#' it is interpreted as a hashtag, and
          only hashtags will be checked. If 'filter_kw' is not a hashtag, both
          hashtags and the tweet text will be checked.
    """

    is_hashtag, parsed_kw = parse_filter_kw(filter_kw)
    filtered_tweets = []

    for tweet in tweets:
        hashtags = list(parse_filter_kw(ht)[1] for ht in tweet['entries']['hashtags'])
        if parsed_kw in hashtags:
            filtered_tweets.append(tweet)
            continue
        if not is_hashtag and parsed_kw in tweet['text'].lower():
            filtered_tweets.append(tweet)

    logger.info(f"Found {len(filtered_tweets)} tweets for filter {filter_kw!r}...")
    return filtered_tweets


def print_tweets_to_xl_sheet(sheet, tweets, username):
    """
    List all tweets in an Excel sheet

    Args:
        :sheet: (obj) Excel sheet reference
        :tweets: (list) Tweets from 'twitter_data'
    """

    headers = ["Time", "url", "isRetweet", "replies", "retweets", "likes", "hashtags", "text"]
    for i, header in enumerate(headers, start=1):
        cell = sheet.cell(row=1, column=i)
        cell.value = header
        cell.fill = XL_FILL_GREEN
        cell.font = XL_FONT_BOLD

    for i, tweet in enumerate(tweets, start=2):
        sheet.cell(row=i, column=1, value=tweet['time'])
        sheet.cell(row=i, column=2, value="link").hyperlink = get_tweet_url(username, tweet['tweetId'])
        cell = sheet.cell(row=i, column=3, value=str(tweet['isRetweet']))
        if tweet['isRetweet']:
                cell.fill = XL_FILL_RED
        sheet.cell(row=i, column=4, value=tweet['replies'])
        sheet.cell(row=i, column=5, value=tweet['retweets'])
        sheet.cell(row=i, column=6, value=tweet['likes'])
        sheet.cell(row=i, column=7, value=str(tweet['entries']['hashtags']))
        sheet.cell(row=i, column=8, value=tweet['text'])


def convert_to_excel(twitter_data, excel_file, filters):
    """
    Convert a twitter data dictionary to a excel file

    Args:
        :twitter_data: (dict) dictionary with twitter data
        :excel_file: (str) excel file name
        :filters: (list) list of filters
    """

    logger.info("Creating excel file...")
    tweets = get_tweets(twitter_data)
    username = twitter_data['profile'].get('username', None)

    # ----- Tweet data -----
    workbook = xl.Workbook()
    sheet1 = workbook.active
    sheet1.title = "Twitter raw data"
    print_tweets_to_xl_sheet(sheet1, tweets, username)

    # ----- Tweets per day -----
    sheet2 = workbook.create_sheet(title="Twitter activity")
    for i, header in enumerate(["Day", "totTweets", "ownTweets"], start=1):
        cell = sheet2.cell(row=1, column=i)
        cell.value = header
        cell.fill = XL_FILL_GREEN
        cell.font = XL_FONT_BOLD

    tweets_per_day = get_tweets_per_day(twitter_data)
    # Only count tweets made by the own account (exclude any retweets)
    tweets_per_day_own = get_tweets_per_day(twitter_data, include_retweet=False)
    for i, (day, num_tweets) in enumerate(tweets_per_day.items(), start=2):
        sheet2.cell(row=i, column=1, value=day.strftime('%F'))
        sheet2.cell(row=i, column=2, value=num_tweets)
        sheet2.cell(row=i, column=3, value=tweets_per_day_own.get(day, 0))

    # ----- User data -----
    sheet3 = workbook.create_sheet(title="Account")
    profile = twitter_data['profile']
    headers = ["name", "username", "likes_count", "tweets_count", "followers_count", "following_count"]
    for i, header in enumerate(headers, start=1):
        cell = sheet3.cell(row=i, column=1)
        cell.value = header
        cell.fill = XL_FILL_GREEN
        cell.font = XL_FONT_BOLD
        sheet3.cell(row=i, column=2, value=profile.get(header, 'NONE'))

    # ----- Filter tweet data by keywords or tweets -----
    if filters is not None:
        for filter_kw in filters:
            is_hashtag, parsed_kw = parse_filter_kw(filter_kw)
            logger.info(f"Applying filter {filter_kw!r} (hashtag: {is_hashtag})...")
            sheet = workbook.create_sheet(f"Filter {'HT' if is_hashtag else 'KW'} {parsed_kw}")
            filtered_tweets = filter_tweets(tweets, filter_kw)
            print_tweets_to_xl_sheet(sheet, filtered_tweets, username)

    # ----- Save data... -----
    logger.info(f"Saving data: {truncate_filepath(excel_file)}")
    workbook.save(excel_file)


def parse_filter_kw(filter_kw):
    filter_kw = filter_kw.strip()
    is_hashtag = filter_kw.startswith('#')
    parsed_kw = filter_kw.replace('#', '').repace("'", '').lower()
    return (is_hashtag, parsed_kw)


if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        logger.error(f"Exit...")
        sys.exit(1)
