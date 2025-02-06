# Reddit Stock Scraper & Sentiment Analyzer
## Video Demo:  <https://youtu.be/gRL9q0WFo2A>
## Description:
This script, when initiated, uses Reddit's API to search the 100 top *Hot* submissions
in a number of the most popular and active stock market related subreddits for mentions
of stock tickers, and when found, determines the sentiment of the accompanying text.  This
data is then sorted to determine the top ten most mentioned stocks and their sentiment and
printed in an ASCII art table.

## Required Third-Party Packages
This script requires that a number of third-party packages are installed within the Python
environment you are running this script in.  These packages are:
`praw`, `dotenv`, `transformers`, `tabulate`, and `yfinance`.

You can find the pip installers [here.](requirements.txt)

## Details and How to Modify
There are a number of ways to customize this script to modify or fine tune the final results.  These details will be explained below in the descriptions for each function.

### main()
The main function simply calls the required functions and prints the final results in an ASCII art table using `tabulate`.  No input is required and nothing should be modified.

### scrape_reddit()
This function is called by `main()` and scans Reddit submissions for stock tickers.  The function will return a list of dictionaries that contains all the discovered stock tickers, the company names, the number of occurrences in various submissions and the comments relating to the mentioned stocks.  This function uses the `praw` library to access Reddit's API, then uses regular expressions to search for possible tickers and finally, it uses the `yfinance` library to validate the tickers and get the corresponding company names.  The pip installers can be found [here.](requirements.txt)

#### Variables to Modify

`search_number =`
This is the first variable that can be customized.  The default is **100**, which means the `scrape_reddit()` function will search through 100 posts to look for stock tickers, but this can be changed to any number that is a positive integer.  Beware that as this number increases, the script requires significantly more time to run.

`sublist =`
This variable contains the names of all the subreddits that will be searched through.  The default subreddits are Stocks, StockMarket, Investing, and WallStreetBets.  These are among the most popular stock related subreddits but the list can be modified as desired.  A new subreddit can be added to the code by using quotes and a + sign at the beginning ("+**NewSubredditHere**").

`pattern =`
The `scrape_reddit()` function uses Regular Expressions to match words between one and five characters containing only letters (A-Z).   `yfinace` then validates all the found stock tickers, but sometimes commonly capitalized words and acronyms are included if there is a ticker that matches an actual company.  If the final results of this script contain any stock tickers that the user knows to be incorrect or simply wants to exclude, they may be added to the RegEx pattern list.

### get_sentiment(top_10)
This function takes the `top_10` list returned by the `scrape_reddit()` function and replaces the "Comments" key and corresponding values with "Sentiment" and a corresponding value of `positive` or `negative`.  It does this by running each comment through the `analyze_sentiment()` function.  The list of dictionaries that this function returns is the final list of results for the **Reddit Stock Scraper & Sentiment Analyzer** script.  It's a list of dictionaries that contains, for each stock, it's *Ticker*, *Company Name*, *Number of Occurrences*, and *Sentiment*.

### analyze_sentiment(text)

This function is automatically called by the `get_sentiment()` function and takes a string of text as input.  It's purpose is to analyze the sentiment of a reddit submission (title and body) and return a value of `positive` or `negative`.

This function implements machine learning and natural language processing (NLP) by using the Hugging Face Transformers Library to analyze inputted text.  The pip installer can be found [here.](requirements.txt)

The default model used to analyze the text is [mwkby/distilbert-base-uncased-sentiment-reddit-crypto](https://huggingface.co/mwkby/distilbert-base-uncased-sentiment-reddit-crypto#distilbert-base-uncased-sentiment-reddit-crypto) which is pre-trained to determine the sentiment of Reddit comments (specifically related to cryptocurrency but it has worked well for financial and stock sentiment.) Additional models can be found [here](https://huggingface.co/models?pipeline_tag=text-classification&sort=trending) and can be implemented by swapping out the code in the `sentiment_analysis` variable.

    sentiment_analysis = pipeline("text-classification", model="mwkby/distilbert-base-uncased-sentiment-reddit-crypto")


