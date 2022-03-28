import os
import re
import json
from datetime import datetime, timedelta
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
    link = ['https://www.imdb.com/news/top', 'https://www.empireonline.com/movies/news/', 'https://editorial.rottentomatoes.com/news/']
    allow_domain = ['https://www.imdb.com', 'https://www.empireonline.com', 'rottentomatoes.com']
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88) Gecko/20100101 Firefox/88.0'}
    clean = re.compile('<.*?>')

    def __init__(self):
        self.start_link = WebCrawler.link

        self.found_link = set()
        self.allow_domain = WebCrawler.allow_domain
        self.scrap_data = {}
        self.metadata = {}

        self.setup_dir()
        self.load_metadata()

    def setup_dir(self):
        if not os.path.exists("./data/web-data"):
            os.mkdir("./data/web-data")

    def load_metadata(self):
        if os.path.exists('./data/metadata.json'):  # load metadata if file was found
            metadata_json = open('./data/metadata.json')
            self.metadata = json.load(metadata_json)
        else:  # make file if no file
            data = {'twitter-keyword' : [], 'web-keyword' : [], 'web' : []}
            with open('./data/metadata.json', 'w') as outfile:
                JSON = json.dumps(data, indent=4)
                outfile.write(JSON)
            self.metadata = data

    def scrap(self):
        for domain in self.start_link:
            response = requests.get(domain, headers=WebCrawler.headers)
            if response.status_code >= 400:
                continue
            bs = BeautifulSoup(response.text, 'html.parser')

            # remove unuse tag
            unuse_tag = [bs.head, bs.footer, bs.script, bs.noscript, bs.iframe]
            for tag in unuse_tag:
                if tag != None:
                    tag.decompose()
            self.scrap_data[domain] = self.clean_html(str(bs))

            # find next link
            LINK = set()
            for a in bs.find_all('a'):              # find all tag a
                try:
                    link = a.attrs['href']
                except KeyError:
                    continue
                if link == None:                    # no href found
                    continue
                if link.find('https') == -1:        # is relative link
                    link = domain + link
                if link in self.found_link:         # if already found link
                    continue
                for DOMAIN in self.allow_domain:
                    if link.find(DOMAIN) != -1:  # in allow domain
                        LINK.add(link)
                        self.found_link.add(link)
                        break

            # use thread to go next link
            n = len(LINK)
            with ThreadPoolExecutor(max_workers=n) as executor:
                with requests.Session() as session:
                    executor.map(self.fetch, [domain]*n ,[session]*n, [*LINK])
                    executor.shutdown(wait=True)

        self.save_to_data()


    def fetch(self, domain, session, url):
        with session.get(url, headers=WebCrawler.headers) as response:
            if response.status_code >= 400:
                return
            self.found_link.add(domain)
            print(f'current url : {url}', end='\r')
            bs = BeautifulSoup(response.text, 'html.parser')

            # remove unuse tag
            unuse_tag = [bs.head, bs.footer, bs.script, bs.noscript, bs.iframe]
            for tag in unuse_tag:
                if tag != None:
                    tag.decompose()
            self.scrap_data[url] = self.clean_html(str(bs))

            # find next link
            LINK = set()
            for a in bs.find_all('a'):
                link = a.attrs['href']
                try:
                    link = a.attrs['href']
                except KeyError:
                    continue
                if link == None:
                    continue
                if link.find('https') == -1:            # is relative link
                    link = domain + link
                if link in self.found_link:         # if already found link
                    continue
                for DOMAIN in self.allow_domain:
                    if link.find(DOMAIN) != -1:  # in allow domain
                        LINK.add(link)
                        self.found_link.add(link)
                        break

            # use thread to go next link
            n = len(LINK)
            with ThreadPoolExecutor(max_workers=n) as executor:
                with requests.Session() as session:
                    executor.map(self.fetch_sub,[session]*n, [*LINK])
                    executor.shutdown(wait=True)

    def fetch_sub(self, session, url):
        with session.get(url, headers=WebCrawler.headers) as response:
            if response.status_code >= 400:
                return
            print(f'current url(sub) : {url}', end='\r')
            bs = BeautifulSoup(response.text, 'html.parser')
            # remove unuse tag
            unuse_tag = [bs.head, bs.footer, bs.script, bs.noscript, bs.iframe]
            for tag in unuse_tag:
                if tag != None:
                    tag.decompose()
            self.scrap_data[url] = self.clean_html(str(bs))

    def save_to_data(self):
        with open("./data/web-data.json", 'w') as outfile:
            JSON = json.dumps(self.scrap_data, indent=4) 
            outfile.write(JSON)

    def clean_html(self, html):
        clean_text = re.sub(WebCrawler.clean, '', html)     # remove all html tag
        for char in ['\n', '\t', '\r']:                     # remove escape character
            clean_text = clean_text.replace(char, '')
        clean_text = re.sub(' +', ' ', clean_text)
        return clean_text

class TwitterCrawler():

    def __init__(self):
        self.metadata = {}

        self.setup_dir()    # setup data hierarchy
        self.load_metadata()

    def setup_dir(self):
        if not os.path.exists(f"./data/tweets/"): 
            os.mkdir(f"./data/tweets/")
        
    def load_metadata(self):
        if os.path.exists('./data/metadata.json'):  # load metadata if file was found
            metadata_json = open('./data/metadata.json')
            self.metadata = json.load(metadata_json)
        else:  # make file if no file
            data = {'twitter-keyword' : [], 'web-keyword' : [], 'web' : []}
            with open('./data/metadata.json', 'w') as outfile:
                JSON = json.dumps(data, indent=4)
                outfile.write(JSON)
            self.metadata = data

    def save_metadata(self):
        with open('./data/metadata.json', 'w') as outfile:
            JSON = json.dumps(self.metadata, indent=4)
            outfile.write(JSON)


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

    def search_tweets(self, keyword):
        if not os.path.exists(f"./data/tweets/{keyword}"):  # create dir for new keyword if not exist
            os.makedirs(f"./data/tweets/{keyword}")
        api = self.connect()
        for i in range(7):  # search 7 day
            until_day = datetime.strftime(datetime.now() - timedelta(i-1), '%Y-%m-%d')
            day = datetime.strftime(datetime.now() - timedelta(i), '%Y-%m-%d')
            if keyword not  in self.metadata['twitter-keyword'].keys():
                self.metadata['twitter-keyword'][keyword] = {'date' : []}
            if day in self.metadata['twitter-keyword'][keyword]['date']:
                continue
            print(f"searching : {day}")
            tweets = tw.Cursor(api.search_tweets, 
                        q=f"{keyword} -filter:retweets",
                        lang="en",
                        until=until_day).items(900)

            # use set to remove duplicate tweet
            tweets_set = set()
            for tweet in tweets:
                tweets_set.add(tweet)
            tweets = list(tweets_set)

            # convert to dataframe
            users_locs = [[
                keyword,
                tweet.user.screen_name,
                tweet.user.location if tweet.user.location != '' else 'unknown',
                tweet.created_at.replace(tzinfo=None),
                remove_url(tweet.text),
                tweet.favorite_count,
                tweet.retweet_count,
                sentiment(TextBlob(stem(cleanText(tweet.text)))),
                f"https://twitter.com/twitter/statuses/{tweet.id}"] for tweet in tweets]

            tweet_text = pd.DataFrame(data=users_locs, 
                columns=['keyword','user','location','post date','tweet', 'favorite count', 'retweet count','sentiment','tweet link'])
            tweet_text = tweet_text.sort_values('post date', ascending=True).reset_index(drop=True)     # sort by datetime

            # save to excel
            tweet_text.to_excel(f"./data/tweets/{keyword}/{day}.xlsx", engine="openpyxl", index=False)
            self.metadata['twitter-keyword'][keyword]['date'].append(day)
            self.save_metadata()
            print(f"save to file : {day}.xlsx")


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

if not os.path.exists('./data'):
    os.mkdir('./data')