import os
import re
import json
from concurrent.futures import ThreadPoolExecutor

import requests
import pandas as pd
import tweepy as tw
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from textblob import TextBlob

class WebCrawler():
    link = ['https://www.imdb.com/news/top', 'https://www.metacritic.com', 'https://www.rottentomatoes.com']
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88) Gecko/20100101 Firefox/88.0'}

    def __init__(self):
        self.main_link = 'https://www.imdb.com/news/top'
        self.found_link = set()
        self.allow_domain = 'www.imdb.com'
        self.scrap_data = {}
        self.metadata = {}

        try:
            os.mkdir('./data')
        except FileExistsError:
            pass
        self.load_metadata()

    def load_metadata(self):
        try:
            metadata_json = open('./data/metadata.json')
            self.metadata = json.load(metadata_json)
        except FileNotFoundError:   # make file if no file
            data = {'twitter-keyword' : [], 'web-keyword' : [], 'web' : []}
            with open('./data/metadata.json', 'w') as outfile:
                JSON = json.dumps(data, indent=4)
                outfile.write(JSON)
            self.metadata = data

    def scrap(self):
        html = requests.get(self.main_link, headers=WebCrawler.headers)
        bs = BeautifulSoup(html.text, 'html.parser')

        # remove unuse tag
        unuse_tag = [bs.head, bs.footer, bs.script, bs.noscript, bs.iframe]
        for tag in unuse_tag:
            if tag != None:
                tag.decompose()

        self.scrap_data[self.main_link] = str(bs)

        # find next link
        LINK = set()
        for a in bs.find_all('a'):              # find all tag a
            link = a.attrs['href']
            if link == None:                    # no href found
                continue
            if link.find('https') == -1:        # is relative link
                link = self.main_link + link
            if link.find(self.allow_domain) != -1:  # in allow domain
                LINK.add(link)

        # use thread to go next link
        n = len(LINK)
        with ThreadPoolExecutor(max_workers=n) as executor:
            with requests.Session() as session:
                executor.map(self.fetch, [self.main_link]*n ,[session]*n, [*LINK])
                executor.shutdown(wait=True)

        self.save_to_data()


    def fetch(self, domain, session, url):
        with session.get(url, headers=WebCrawler.headers) as response:
            print(f'current url : {url}', end='\r')
            bs = BeautifulSoup(response.text, 'html.parser')

            # remove unuse tag
            unuse_tag = [bs.head, bs.footer, bs.script, bs.noscript, bs.iframe]
            for tag in unuse_tag:
                if tag != None:
                    tag.decompose()

            self.scrap_data[self.main_link] = str(bs)

            # find next link
            LINK = set()
            for a in bs.find_all('a'):
                link = a.attrs['href']
                if link == None:
                    continue
                if link.find('https') == -1:            # is relative link
                    link = domain + link
                if link.find(self.allow_domain) != -1:  # in allow domain
                    LINK.add(link)

            # use thread to go next link
            n = len(LINK)
            with ThreadPoolExecutor(max_workers=n) as executor:
                with requests.Session() as session:
                    executor.map(self.fetch_sub,[session]*n, [*LINK])
                    executor.shutdown(wait=True)

    def fetch_sub(self, session, url):
        with session.get(url, headers=WebCrawler.headers) as response:
            print(f'current url(sub) : {url}', end='\r')
            bs = BeautifulSoup(response.text, 'html.parser')
            # remove unuse tag
            unuse_tag = [bs.head, bs.footer, bs.script, bs.noscript, bs.iframe]
            for tag in unuse_tag:
                if tag != None:
                    tag.decompose()

            self.scrap_data[self.main_link] = str(bs)

    def save_to_data(self):
        with open("./data/web-data.json", 'w') as outfile:
            JSON = json.dumps(self.scrap_data, indent=4) 
            outfile.write(JSON)

class TwitterCrawler():

    def __init__(self):
        self.metadata = {}

        try:
            os.mkdir('./data')
        except FileExistsError:
            pass
        self.load_metadata()

    def load_metadata(self):
        try:
            metadata_json = open('./data/metadata.json')
            self.metadata = json.load(metadata_json)
        except FileNotFoundError:   # make file if no file
            data = {'twitter-keyword' : [], 'web-keyword' : [], 'web' : []}
            with open('./data/metadata.json', 'w') as outfile:
                JSON = json.dumps(data, indent=4)
                outfile.write(JSON)
            self.metadata = data

    def connect(self):
        # set API key in .env
        load_dotenv()
        consumer_key = os.getenv('CONSUMER_KEY')
        consumer_secret = os.getenv('CONSUMER_SECRET')
        access_token = os.getenv('ACCESS_TOKEN')
        access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
        
        try:
            auth = tw.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tw.API(auth)
            return api
        except:
            print("Error")
            exit(1)

    def search_tweets(self, search_words, count=50):
        api = self.connect()
        tweets = api.search_tweets(
            q=f"{search_words} -filter:retweets", 
            lang="en",
            count=count)

        tweets_set = set()
        for tweet in tweets:
            tweets_set.add(tweet)
        tweets = list(tweets_set)

        users_locs = [[
            search_words,
            tweet.user.screen_name,
            tweet.user.location if tweet.user.location != '' else 'unknown',
            tweet.created_at.replace(tzinfo=None),
            remove_url(tweet.text),
            sentiment(TextBlob(stem(cleanText(tweet.text)))),
            f"https://twitter.com/twitter/statuses/{tweet.id}"] for tweet in tweets]
                    
        tweet_text = pd.DataFrame(data=users_locs, 
            columns=['keyword','user','location','post date','tweet','sentiment','tweet link'])
        self.save_to_excel(tweet_text)

    def save_to_excel(self, tweets):
        tweets.to_excel("./data/tweets.xlsx", engine="openpyxl", index=False)


def cleanText(text):
    text = text.lower()
    # Removes all mentions (@username) from the tweet since it is of no use to us
    text = re.sub(r'(@[A-Za-z0-9_]+)', '', text)
        
    # Removes any link in the text
    text = re.sub('http://\S+|https://\S+', '', text)

    # Only considers the part of the string with char between a to z or digits and whitespace characters
    # Basically removes punctuation
    text = re.sub(r'[^\w\s]', '', text)

    # Removes stop words that have no use in sentiment analysis 
    text_tokens = word_tokenize(text)
    text = [word for word in text_tokens if not word in stopwords.words()]

    text = ' '.join(text)
    return text

def stem(text):
    # This function is used to stem the given sentence
    porter = PorterStemmer()
    token_words = word_tokenize(text)
    stem_sentence = []
    for word in token_words:
        stem_sentence.append(porter.stem(word))
    return " ".join(stem_sentence)

def sentiment(cleaned_text):
    # Returns the sentiment based on the polarity of the input TextBlob object
    if cleaned_text.sentiment.polarity > 0:
        return 'positive'
    elif cleaned_text.sentiment.polarity < 0:
        return 'negative'
    else:
        return 'neutral'

def remove_url(txt):
    """Replace URLs found in a text string with nothing 
    (i.e. it will remove the URL from the string).

    Parameters
    ----------
    txt : string
        A text string that you want to parse and remove urls.

    Returns
    -------
    The same txt string with url's removed.
    """

    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())

def remove_url_th(txt):
    """Replace URLs found in a text string with nothing 
    (i.e. it will remove the URL from the string).

    Parameters
    ----------
    txt : string
        A text string that you want to parse and remove urls.

    Returns
    -------
    The same txt string with url's removed.
    """

    return " ".join(re.sub("([^\u0E00-\u0E7Fa-zA-Z' ]|^'|'$|''|(\w+:\/\/\S+))", "", txt).split())