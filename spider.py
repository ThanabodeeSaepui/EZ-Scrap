import os
import re
import json
from urllib.parse import urlparse
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
    link = [
        'https://www.imdb.com/news/movie',
        'https://www.empireonline.com/movies/news/',
        'https://editorial.rottentomatoes.com/news/',
        'https://collider.com',
        'https://screenrant.com/movie-news/']
    non_scrap_domain = {
        't.co',
        'twitter.com',
        'pinterest.com',
        'www.reddit.com',
        'youtu.be',
        'www.youtube.com',
        'instagram.com',
        'www.instagram.com',
        'www.facebook.com',
        'www.tumblr.com',
        'plus.google.com',
        'www.fandango.com',
        'support.google.com',
        'www.vudu.com',
        'www.entershanementreviews.com',
        'twitch.tv'
    }
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88) Gecko/20100101 Firefox/88.0'}
    clean = re.compile('<.*?>')

    def __init__(self):
        self.start_link = WebCrawler.link

        self.found_link = set()
        self.scrap_data = {}
        self.metadata = {}

        self.setup_dir()
        self.load_metadata()

    def setup_dir(self):
        if not os.path.exists("./data/web-data"):
            os.mkdir("./data/web-data")
        if not os.path.exists('./data/metadata.json'):
            data = {'twitter-keyword' : {}, 'web-keyword' : [], 'web' : [], 'link ref': {}}
            with open('./data/metadata.json', 'w', encoding="UTF-8") as outfile:
                JSON = json.dumps(data, indent=4)
                outfile.write(JSON)

    def save_metadata(self):
        with open('./data/metadata.json', 'w' , encoding="UTF-8") as outfile:
            JSON = json.dumps(self.metadata, indent=4)
            outfile.write(JSON)

    def load_metadata(self):
        metadata_json = open('./data/metadata.json',encoding="UTF-8")
        self.metadata = json.load(metadata_json)

    def scrap(self):
        for domain in self.start_link:
            response = requests.get(domain, headers=WebCrawler.headers)
            if response.status_code >= 400:
                continue
            current_domain = urlparse(domain).netloc
            bs = BeautifulSoup(response.text, 'html.parser')

            # remove unuse tag
            unuse_tag = [bs.head, bs.footer, bs.script, bs.noscript, bs.iframe]
            for tag in unuse_tag:
                if tag != None:
                    tag.decompose()

            if current_domain not in self.scrap_data.keys():
                self.scrap_data[current_domain] = {}
            self.scrap_data[current_domain][domain] = self.clean_html(str(bs))

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
                
                link_domain = urlparse(link).netloc
                if link_domain not in WebCrawler.non_scrap_domain:
                    LINK.add(link)
                    self.found_link.add(link)

                # count link ref
                if link_domain != current_domain:       # not same domain
                    if link_domain not in self.metadata['link ref'].keys():
                        self.metadata['link ref'][link_domain] = 1
                    else:
                        self.metadata['link ref'][link_domain] += 1


            # use thread to go next link
            n = len(LINK)
            with ThreadPoolExecutor(max_workers=n) as executor:
                with requests.Session() as session:
                    executor.map(self.fetch, [domain]*n ,[session]*n, [*LINK])
                    executor.shutdown(wait=True)

        self.save_to_data()
        self.save_metadata()


    def fetch(self, domain, session, url):
        with session.get(url, headers=WebCrawler.headers) as response:
            if response.status_code >= 400:
                return
            current_domain = urlparse(url).netloc
            print(f'current url : {url}', end='\r')
            bs = BeautifulSoup(response.text, 'html.parser')

            # remove unuse tag
            unuse_tag = [bs.head, bs.footer, bs.script, bs.noscript, bs.iframe]
            for tag in unuse_tag:
                if tag != None:
                    tag.decompose()
            
            if current_domain not in self.scrap_data.keys():
                self.scrap_data[current_domain] = {}
            self.scrap_data[current_domain][url] = self.clean_html(str(bs))

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

                link_domain = urlparse(link).netloc
                if link_domain not in WebCrawler.non_scrap_domain:
                    LINK.add(link)
                    self.found_link.add(link)

                # count link ref
                if link_domain != current_domain:       # not same domain
                    if link_domain not in self.metadata['link ref'].keys():
                        self.metadata['link ref'][link_domain] = 1
                    else:
                        self.metadata['link ref'][link_domain] += 1

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
            current_domain = urlparse(url).netloc
            print(f'current url(sub) : {url}', end='\r')
            bs = BeautifulSoup(response.text, 'html.parser')
            # remove unuse tag
            unuse_tag = [bs.head, bs.footer, bs.script, bs.noscript, bs.iframe]
            for tag in unuse_tag:
                if tag != None:
                    tag.decompose()
            
            if current_domain not in self.scrap_data.keys():
                self.scrap_data[current_domain] = {}
            self.scrap_data[current_domain][url] = self.clean_html(str(bs))

            for a in bs.find_all('a'):              # find all tag a
                try:
                    link = a.attrs['href']
                except KeyError:
                    continue
                if link == None:                    # no href found
                    continue
                if link.find('https') == -1:        # is relative link
                    link = url + link
                if link in self.found_link:         # if already found link
                    continue
                
                link_domain = urlparse(link).netloc
                # count link ref
                if link_domain != current_domain:       # not same domain
                    if link_domain not in self.metadata['link ref'].keys():
                        self.metadata['link ref'][link_domain] = 1
                    else:
                        self.metadata['link ref'][link_domain] += 1

    def save_to_data(self):
        for domain in self.scrap_data:
            if not os.path.exists(f'./data/web-data/{domain}'):
                os.mkdir(f'./data/web-data/{domain}')
            with open(f"./data/web-data/{domain}/data.json", 'w', encoding="UTF-8") as outfile:
                JSON = json.dumps(self.scrap_data[domain], indent=4) 
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
        if not os.path.exists('./data/metadata.json'):
            data = {'twitter-keyword' : {}, 'web-keyword' : [], 'web' : [], 'link ref': {}}
            with open('./data/metadata.json', 'w', encoding="UTF-8") as outfile:
                JSON = json.dumps(data, indent=4)
                outfile.write(JSON)
        
    def load_metadata(self):
        metadata_json = open('./data/metadata.json',encoding="UTF-8")
        self.metadata = json.load(metadata_json)

    def save_metadata(self):
        with open('./data/metadata.json', 'w', encoding="UTF-8") as outfile:
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
        reg = re.compile(r'[a-zA-Z]')
        if reg.match(keyword.replace("#","")):
            use_lan = "en"
        else:
            use_lan = "th"
        if not os.path.exists(f"./data/tweets/{keyword}"):  # create dir for new keyword if not exist
            os.makedirs(f"./data/tweets/{keyword}")
        api = self.connect()
        for i in range(7):  # search 7 day
            until_day = datetime.strftime(datetime.now() - timedelta(i-1), '%Y-%m-%d')
            day = datetime.strftime(datetime.now() - timedelta(i), '%Y-%m-%d')
            start_day = (datetime.today() - timedelta(i+1)).date()
            if keyword not  in self.metadata['twitter-keyword'].keys():
                self.metadata['twitter-keyword'][keyword] = {'date' : []}
            if day in self.metadata['twitter-keyword'][keyword]['date']:
                continue
            print(f"searching [{keyword}]: {day}")
            tweets = tw.Cursor(api.search_tweets, 
                        q=f"{keyword} -filter:retweets",
                        lang=use_lan,
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
                sentiment(TextBlob(stem(cleanText(tweet.text)))) if use_lan == "en" else sentiment_th(cleanText_th(tweet.text)),
                f"https://twitter.com/twitter/statuses/{tweet.id}"] for tweet in tweets if tweet.created_at.replace(tzinfo=None).date() > start_day]
            
            if len(users_locs) == 0:
                continue

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

def cleanText_th(text):

    text = re.sub('http://\S+|https://\S+', '', text) # remove url


    url = "https://api.aiforthai.in.th/textcleansing" #api for remove emoji
    
    params = {f'text':{text}}
    
    
    headers = {
        'Apikey': "fIwWRjuLjs8KrK8BcA7kaj5das47eZpH",
        }
    
    response = requests.request("GET", url, headers=headers, params=params)
    
    return response.json()['cleansing_text']

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

def sentiment_th(clean_text):

    url = "https://api.aiforthai.in.th/ssense"
    params = {'text':clean_text}
    headers = {
        'Apikey': "fIwWRjuLjs8KrK8BcA7kaj5das47eZpH"
        }
    response = requests.get(url, headers=headers, params=params)

    if response.json()['sentiment']['polarity'] == '':
        polarity = "neutral"
    else:
        polarity = response.json()['sentiment']['polarity']
    
    return polarity


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