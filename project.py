"""Reddit Stock Scraper & Sentiment Analyzer

This script, when initiated, uses Reddit's API to search the 100 top *Hot* submissions
in a number of the most popular and active stock market related subreddits for mentions
of stock tickers and when found, determines the sentiment of the accompanying comment.
The top ten most mentioned stocks and their sentiment is printed in an ASCII art table.

This script requires that a number of third-party packages are installed within the Python
environment you are running this script in.  These packages are:
`praw`, `dotenv`, `transformers`, `tabulate`, `os`, `re`, `yfinance` and `logging`.

"""

# Libraries to import
import praw  # Python Reddit API Wrapper
from dotenv import load_dotenv  # Python-dotenv to keep reddit credentials hidden
from transformers import pipeline  # Loads NLP model for text classification
from tabulate import tabulate  # Creates an ASCII art table to display final results
import os  # Enables operating system dependent functionality to keep reddit credentials hidden
import re  # Regular expressions
import yfinance as yf  # Yahoo Finance stock information
import logging  # Error(log) handline

logger = logging.getLogger("yfinance")  # Disable printing of yfinance logs
logger.disabled = True
logger.propagate = False

# Load dotenv functionality
load_dotenv()

# Ignore FutureWarning raised by Transformers Pipeline
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)


def main():

    print("\n\n Hang tight... This program can take a few minutes to finish.\n\n")
    # Calls `scrape_reddit` to initiate program
    reddit_data = scrape_reddit()

    # Makes list of top 10 most mentioned stocks
    top_10: list = reddit_data[0:10]
    final_results: list = get_sentiment(top_10)
    print(tabulate(final_results, headers="keys", tablefmt="mixed_grid"))


def scrape_reddit() -> list:
    """
    Scans Reddit submissions for stock tickers and gathers the related comment text.
    Returns a dict of stock tickers, the company name, the number of occurrences of each stock, and the comments.

    :param None
    :return: A list of stock tickers and their corresponding sentiment
    :rtype: dict, list
    """

    # Total number of reddit submissions to search
    search_number: int = 100

    # List of subreddits to search in
    sublist: str = "stocks" "+stockmarket" "+investing" "+wallstreetbets"

    # Regular Expression patter to find stock tickers
    pattern = re.compile(
        r"""
    \b                          #Matches the empty string at the beginning of a word.
    (?!                         #Excludes the following matches
    (?:AI|IMO|ETF|O|WSB|FED|USA|A|U.S.|NFL|SF|DCA|EPS|VOO|SEA|CNN|IPO|EFT|VGT|CPI|DTC|API|X|III|USPS|GPU|PM|
    NYC|DCF|RUS|GOLD|AH|ROTH|YOLO|DUE|TV|SPY|QQQ|DOW|GRAB|EV|EU|VXUS|S|U|M|HYSA|E|R|CNBC|USD|MSCI|THE|DD)\b)
    \$?[A-Z]{1,5}\b             #Matches a string of all CAPS from 1-5 characters in length
    """,
        re.VERBOSE,
    )

    # Obtains a Reddit instance
    reddit = praw.Reddit(
        client_id=os.getenv("client_id"),
        client_secret=os.getenv("client_secret"),
        user_agent=os.getenv("user_agent"),
    )

    # Search each reddit submission for stock tickers get store tickers and comments
    reddit_comments: dict = {}
    ticker_count_list: list = []
    for submission in reddit.subreddit(sublist).hot(limit=search_number):
        full_post: str = submission.title + submission.selftext
        if re.search(pattern, full_post):
            matches: set = set(re.findall(pattern, full_post))
            for match in matches:
                try:
                    # Validates ticker with yfinance
                    possible_stock = yf.Ticker(match).info
                    name: str = possible_stock["shortName"]
                    ticker: str = possible_stock["symbol"]

                    # Adds ticker to `ticker_count_list`
                    ticker_count_list.append([ticker])

                    # Adds ticker and comment to `reddit_comments`
                    if ticker not in reddit_comments.keys():
                        reddit_comments[ticker] = full_post
                    else:
                        reddit_comments[ticker] = reddit_comments[match] + full_post
                except (KeyError, NameError):
                    pass

    # Counts the occurrences of each stock ticker in `ticker_count_list`.
    tickers_counted: dict = {}
    for ticker in ticker_count_list:
        if ticker[0] not in tickers_counted:
            tickers_counted[ticker[0]] = 1
        else:
            tickers_counted[ticker[0]] += 1

    # Sort `tickers_counted` in descending order
    tickers_counted = dict(
        sorted(tickers_counted.items(), reverse=True, key=lambda ticker: ticker[1])
    )

    # Combine all info into list of dicts
    reddit_data: list = []
    for item in tickers_counted:
        name = yf.Ticker(item).info["shortName"]
        reddit_data.append(
            {
                "Ticker": item,
                "Name": name,
                "Occurrences": tickers_counted[item],
                "Comments": reddit_comments[item],
            }
        )

    # Function returns a list of stock tickers and their corresponding sentiment.
    return reddit_data


def get_sentiment(top_10: list) -> list:
    """
    Gets the sentiment for each stock in the top_10 list.

    :param top_10: A list of dictionaries that contain comments to analyze
    :type top_10: list
    :return: A list of dictionaries that contain tickers, company names, occurrences, and sentiments
    :rtype: list
    """

    top_10_with_sentiments: list = []
    for stock in top_10:
        top_10_with_sentiments.append(
            {
                "Ticker": stock["Ticker"],
                "Name": stock["Name"],
                "Occurrences": stock["Occurrences"],
                "Sentiment": analyze_sentiment(stock["Comments"]),
            }
        )

    return top_10_with_sentiments


def analyze_sentiment(text: str) -> str:
    """
    Analyzes sentiment of text.

    :param text: A string of text to analyze
    :type text: str
    :raise TypeError: If text is not a str
    :return: A string, "negative" or "positive"
    :rtype: str
    """

    # Loads pre-trained sentiment analysis model
    sentiment_analysis = pipeline(
        "text-classification",
        model="mwkby/distilbert-base-uncased-sentiment-reddit-crypto",
    )

    # Splits "text" string into a list of strings at line breaks
    chunks: list = text.splitlines()

    # Empty list to deposit chunk scores into
    aggregate_scores: list = []

    # Iterates over each chunk of text to build a list of sentiment values for each chunk.
    for chunk in chunks:
        result: list = sentiment_analysis(chunk, max_length=512, truncation=True)
        aggregate_scores.append(result[0]["label"])

    # Determines the aggregate sentiment of all chunks by finding the MODE of the sentiment labels (excluding Neutral)
    aggregate_scores = [x for x in aggregate_scores if x != "Neutral"]
    final_sentiment: list = max(set(aggregate_scores), key=aggregate_scores.count)
    return str(final_sentiment)


if __name__ == "__main__":
    main()
