import os
import re
import json
import requests
import tweepy as tw
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

class WebCrawler():
    link = ['https://www.imdb.com/news/top', 'https://www.metacritic.com', 'https://www.rottentomatoes.com']
    
    def __init__(self):
        self.main_link = 'https://www.imdb.com/news/top'
        self.found_link = set()
        self.allow_domain = 'www.imdb.com'
        self.scrap_data = {}
        self.metadata = {}

        self.load_metadata()

    def load_metadata(self):
        metadata_json = open("metadata.json")
        self.metadata = json.load(metadata_json)
    
    def search_twitter(self, query):
        if query not in self.metadata['twitter-keyword']:
            pass # search from twitter

    def scrap(self):
        html = requests.get(self.main_link)
        bs = BeautifulSoup(html.text, 'html.parser')

        # remove unuse tag
        unuse_tag = [bs.head, bs.footer, bs.script, bs.noscript, bs.iframe]
        for tag in unuse_tag:
            if tag != None:
                tag.decompose()
        self.scrap_data[self.main_link] = bs.prettify()

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
        with session.get(url) as response:
            print(f'current url : {url}', end='\r')
            bs = BeautifulSoup(response.text, 'html.parser')

            # remove unuse tag
            unuse_tag = [bs.head, bs.footer, bs.script, bs.noscript, bs.iframe]
            for tag in unuse_tag:
                if tag != None:
                    tag.decompose()

            self.scrap_data[url] = bs.prettify()

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
        with session.get(url) as response:
            print(f'current url(sub) : {url}', end='\r')
            bs = BeautifulSoup(response.text, 'html.parser')
            # remove unuse tag
            unuse_tag = [bs.head, bs.footer, bs.script, bs.noscript, bs.iframe]
            for tag in unuse_tag:
                if tag != None:
                    tag.decompose()

            self.scrap_data[url] = bs.prettify()

    def save_to_data(self):
        with open(".\data\web-data.json", 'w') as outfile:
            JSON = json.dumps(self.scrap_data, indent=4) 
            outfile.write(JSON)

class TwitterCrawler():

    def __init__(self):
        self.metadata = {}
        self.load_metadata()

    def load_metadata(self):
        metadata_json = open("metadata.json")
        self.metadata = json.load(metadata_json)

    def connect(self):
        # set API key in .env
        consumer_key = os.getenv('CONSUMER_KEY')
        consumer_secret = os.getenv('COMSUMER_SECRET')
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
        search_words += ' -filter:retweets'
        fetched_data = api.search_tweets(q=search_words, count=count)
        for tweet in fetched_data:
            txt = tweet.text
            print(txt)