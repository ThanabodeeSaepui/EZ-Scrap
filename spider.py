from importlib.metadata import metadata
import os
import re
import json
import time
from collections import Counter
from urllib.parse import urlparse
from datetime import datetime, timedelta
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor

from WebScrap import clean_html, remove_unuse_tag
from WebScrap import CBR, CinemaBlend, Collider, EmpireOnline, HollywoodReporter, IrishTimes,\
                     Joblo, Movie2News, MovieNewsNet, MovieWeb, NME, RottenTomatoes, Sanook, \
                     Screenrant, SlashFilm, TheWrap, Wegotthiscovered, FirstShowing, Entertainment, IGN

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
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88) Gecko/20100101 Firefox/88.0'}
    clean = re.compile('<.*?>')

    def __init__(self):
        self.start_link = [
            'https://www.imdb.com/news/movie',
            'https://www.bbc.com/news/topics/cg41ylwvgjyt/film',
            'https://www.nytimes.com/section/movies',
            ]
        self.start_link_domain = [urlparse(link).netloc for link in self.start_link]

        self.found_link = set()
        self.scrap_data = {}
        self.metadata = {}
        self.status = 'standby'

        self.setup_dir()
        self.load_metadata()

    def setup_dir(self):
        if not os.path.exists("./data/web-data"):
            os.mkdir("./data/web-data")
        if not os.path.exists('./data/metadata.json'):
            data = {'twitter-keyword' : {}, 'web-keyword' : [], 'webdriver path : '', link ref': {}}
            with open('./data/metadata.json', 'w', encoding="UTF-8") as outfile:
                JSON = json.dumps(data, indent=4, ensure_ascii=False)
                outfile.write(JSON)

    def save_metadata(self):
        with open('./data/metadata.json', 'w' , encoding="UTF-8") as outfile:
            JSON = json.dumps(self.metadata, indent=4, ensure_ascii=False)
            outfile.write(JSON)

    def load_metadata(self):
        metadata_json = open('./data/metadata.json',encoding="UTF-8")
        self.metadata = json.load(metadata_json)

    def reset_link_ref(self):
        self.metadata['link ref'] = {}
        for domain in self.start_link_domain:
            self.metadata['link ref'][domain] = 0

    def set_selenium_webdriver(self, PATH):
        self.metadata['webdriver path'] = PATH
        self.save_metadata()

    def scrap(self):
        self.reset_link_ref()
        for domain in self.start_link:
            response = requests.get(domain, headers=WebCrawler.headers)
            if response.status_code >= 400:
                continue
            current_domain = urlparse(domain).netloc
            bs = BeautifulSoup(response.text, 'html.parser')
            bs = remove_unuse_tag(bs)

            title = bs.find('title').text

            if current_domain not in self.scrap_data.keys():
                self.scrap_data[current_domain] = {}
            self.scrap_data[current_domain][domain] = {}
            self.scrap_data[current_domain][domain]['title'] = title.strip()
            self.scrap_data[current_domain][domain]['content'] = clean_html(str(bs))

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
                if link_domain in self.start_link_domain:
                    LINK.add(link)
                    self.found_link.add(link)

                # count link ref
                if link_domain != current_domain:       # not same domain
                    if link_domain in self.metadata['link ref'].keys():
                        self.metadata['link ref'][link_domain] += 1


            # use thread to go next link
            n = len(LINK)
            with ThreadPoolExecutor(max_workers=n) as executor:
                with requests.Session() as session:
                    executor.map(self.fetch, [domain]*n ,[session]*n, [*LINK])
                    executor.shutdown(wait=True)

            self.save_metadata()
            self.save_to_data(domain)


    def fetch(self, domain, session, url):
        with session.get(url, headers=WebCrawler.headers) as response:
            if response.status_code >= 400:
                return
            current_domain = urlparse(url).netloc
            print(f'current url : {url}', end='\r')
            bs = BeautifulSoup(response.text, 'html.parser')
            bs = remove_unuse_tag(bs)

            title = bs.find('title').text
            
            if current_domain not in self.scrap_data.keys():
                self.scrap_data[current_domain] = {}
            self.scrap_data[current_domain][url] = {}
            self.scrap_data[current_domain][url]['title'] = title.strip()
            self.scrap_data[current_domain][url]['content'] = clean_html(str(bs))


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
                if link_domain in self.start_link_domain:
                    LINK.add(link)
                    self.found_link.add(link)

                # count link ref
                if link_domain != current_domain:       # not same domain
                    if link_domain in self.metadata['link ref'].keys():
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
            bs = remove_unuse_tag(bs)

            title = bs.find('title').text

            if current_domain not in self.scrap_data.keys():
                self.scrap_data[current_domain] = {}
            self.scrap_data[current_domain][url] = {}
            self.scrap_data[current_domain][url]['title'] = title.strip()
            self.scrap_data[current_domain][url]['content'] = clean_html(str(bs))

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
                    if link_domain in self.metadata['link ref'].keys():
                        self.metadata['link ref'][link_domain] += 1

    def default_scrap(self):
        c = Counter()
        for site in [CBR, CinemaBlend, Collider, EmpireOnline, HollywoodReporter, IrishTimes,\
                     Joblo, Movie2News, MovieNewsNet, MovieWeb, NME, RottenTomatoes, \
                     SlashFilm, TheWrap, Wegotthiscovered, FirstShowing]:
            self.status = f'Scraping'
            data = site.ScrapSite()
            domain = data['metadata']['domain']
            c += data['metadata']['ref']
            self.metadata['link ref'] = c
            self.status = f'Saving {domain} data'
            self.save_default_scrap(data, domain)
            self.status = f'Saving metadata'
            self.save_metadata()

        PATH = self.metadata['webdriver path']
        for site in [Sanook, Screenrant, Entertainment, IGN]:
            self.status = f'Scraping By selenium'
            if PATH != "":
                data = site.ScrapSite(PATH)
            else:
                try:
                    data = site.ScrapSite()
                except:
                    return
            domain = data['metadata']['domain']
            c += data['metadata']['ref']
            self.metadata['link ref'] = c
            self.status = f'Saving {domain} data'
            self.save_default_scrap(data, domain)
            self.status = f'Saving metadata'
            self.save_metadata()
        self.status = f'standby'
    
    def save_default_scrap(self, data, domain):
        data['metadata']['web'] = list(data['metadata']['web'])
        print(f"Saving to data : {domain}")
        if not os.path.exists(f'./data/web-data/{domain}'):
            os.mkdir(f'./data/web-data/{domain}')
        with open(f"./data/web-data/{domain}/data.json", 'w', encoding="UTF-8") as outfile:
            JSON = json.dumps(data['data'], indent=4, ensure_ascii=False) 
            outfile.write(JSON)
        with open(f"./data/web-data/{domain}/metadata.json", 'w', encoding="UTF-8") as outfile:
            JSON = json.dumps(data['metadata'], indent=4, ensure_ascii=False) 
            outfile.write(JSON)

    def save_to_data(self, domain):
        print(f"Saving to data : {domain}")
        if not os.path.exists(f'./data/web-data/{domain}'):
            os.mkdir(f'./data/web-data/{domain}')
        with open(f"./data/web-data/{domain}/data.json", 'w', encoding="UTF-8") as outfile:
            JSON = json.dumps(self.scrap_data[domain], indent=4, ensure_ascii=False) 
            outfile.write(JSON)

    def search(self, keyword : str, domain : str) -> tuple[Counter, list, Counter]:
        links = []
        sentiment = Counter()
        metadata_json = open(f'./data/web-data/{domain}/metadata.json', encoding='UTF-8')
        metadata = json.load(metadata_json)
        cnt = Counter()
        with open(f'./data/web-data/{domain}/data.json', encoding='UTF-8') as DATA:
            data = json.load(DATA)
            for page in data.keys():
                try:
                    content = data[page]['content']
                except KeyError:
                    continue
                found = re.findall(keyword, content, re.IGNORECASE)
                if found:
                    clean_text = cleanText(content)
                    SENTIMENT = sentiment_en(clean_text)
                    links.append(page)
                    sentiment[SENTIMENT] += 1
                    sentiment['found'] += len(found)
                    cnt += self.count_word(clean_text)
        return (sentiment, links, cnt)

    def search_web(self, keyword : str) -> tuple[pd.DataFrame, Counter]:
        import timeit
        start = timeit.default_timer()
        self.status = f'searching keyword : {keyword}'
        domain = os.listdir('./data/web-data')
        REF = Counter(self.metadata['link ref'])
        with Pool(os.cpu_count()) as pool:
            results = pool.starmap(self.search, iterable=[(keyword, d) for d in domain])
        LOCS = [[keyword,domain, result[0]['found'], result[0]['positive'], result[0]['neutral'], result[0]['negative'], REF[domain], result[1]]
            for domain, result in zip(domain, results)]
        cnt = Counter()
        for result in results:
            cnt += Counter(result[2])
        df = pd.DataFrame(
            data=LOCS, 
            columns=['Keyword','Domain', 'Found', 'Positive', 'Neutral', 'Negative', 'Ref Count', 'url'])
        self.status = 'standby'
        stop = timeit.default_timer()
        print(f'Search {keyword}Time: {stop - start}')
        return (df, cnt)

    def count_word(self, text : str) -> Counter:
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub("\d+", "", text)
        cnt = Counter(text.split(' '))
        cnt[''] = 0
        return cnt

    def get_status(self):
        return self.status


class TwitterCrawler():

    def __init__(self):
        self.metadata = {}
        self.status = 'standby'

        self.setup_dir()    # setup data hierarchy
        self.load_metadata()

    def setup_dir(self):
        if not os.path.exists(f"./data/tweets/"): 
            os.mkdir(f"./data/tweets/")
        if not os.path.exists('./data/metadata.json'):
            data = {'twitter-keyword' : {}, 'web-keyword' : [], 'webdriver path' : '', 'link ref': {}}
            with open('./data/metadata.json', 'w', encoding="UTF-8") as outfile:
                JSON = json.dumps(data, indent=4, ensure_ascii=False)
                outfile.write(JSON)
        
    def load_metadata(self):
        metadata_json = open('./data/metadata.json',encoding="UTF-8")
        self.metadata = json.load(metadata_json)

    def save_metadata(self):
        with open('./data/metadata.json', 'w', encoding="UTF-8") as outfile:
            JSON = json.dumps(self.metadata, indent=4, ensure_ascii=False)
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
            api = tw.API(auth,wait_on_rate_limit=True)
            return api
        except:
            print("Error")
            exit(1)

    def search_tweets(self, keyword,start_day,end_day):
        reg = re.compile(r'[a-zA-Z]')
        if reg.match(keyword.replace("#","")):
            use_lan = "en"
            hashtag_pattern = re.compile(r"#[a-zA-Z']+")
        else:
            use_lan = "th"
            hashtag_pattern = re.compile(r"#[\u0E00-\u0E7Fa-zA-Z']+")
        if not os.path.exists(f"./data/tweets/{keyword}"):  # create dir for new keyword if not exist
            os.makedirs(f"./data/tweets/{keyword}")
        api = self.connect()
        while start_day >= end_day:
            until_day = datetime.strftime(start_day + timedelta(1), '%Y-%m-%d')
            day = datetime.strftime(start_day, '%Y-%m-%d')
            if keyword not in self.metadata['twitter-keyword'].keys():
                self.metadata['twitter-keyword'][keyword] = {'date' : []}
            if day in self.metadata['twitter-keyword'][keyword]['date']:
                continue
            self.status = f'Collecting Tweets day : {day}'
            c = tw.Cursor(api.search_tweets, 
                        q=f"{keyword} -filter:retweets",
                        lang=use_lan,
                        until=until_day, 
                        tweet_mode="extended",
                        include_entities=True).items()
            tweets = []
            while True:
                try:
                    tweet = c.next()
                    if tweet.created_at.replace(tzinfo=None).date() != start_day:
                        break
                    tweets.append(tweet)
                except tw.TweepError:
                    self.status = 'request limit exceed'
                    time.sleep(60 * 15)
                    continue
                except StopIteration:
                    break
            if len(tweets) == 0:
                self.status = 'standby'
                continue
            
            users_locs = []
            if use_lan == "en":
                for tweet in tweets:
                    hashtag = re.findall(hashtag_pattern, tweet.full_text)
                    self.status = f'Doing Sentiment (EN)'
                    clean_txt = cleanText(tweet.full_text)
                    tweet_sen = sentiment(TextBlob(stem(clean_txt)))
                    text = re.sub(hashtag_pattern,"", tweet.full_text)
                    print(f"https://twitter.com/twitter/statuses/{tweet.id}")
                    locs = [
                        keyword,
                        tweet.user.screen_name,
                        tweet.user.location if tweet.user.location != '' else 'unknown',
                        tweet.created_at.replace(tzinfo=None),
                        remove_url(text) if use_lan == "en" else remove_url_th(text),
                        tweet.favorite_count,
                        tweet.retweet_count,
                        hashtag,
                        tweet_sen,
                        f"https://twitter.com/twitter/statuses/{tweet.id}"]
                    users_locs.append(locs)
            else:
                tweet_text_list = []
                for tweet in tweets:
                    tweet_text_list.append(tweet.full_text)
                self.status = f'Cleaning text (TH)'
                clean_text = cleanText_th(tweet_text_list)
                self.status = f'Doing Sentiment (TH)'
                sentiment_list = sentiment_th(clean_text)
                for tweet, text, sent in zip(tweets, clean_text, sentiment_list):
                    hashtag = re.findall(hashtag_pattern, text)
                    text = re.sub(hashtag_pattern,"", tweet.full_text)
                    print(f"https://twitter.com/twitter/statuses/{tweet.id}")
                    locs = [
                        keyword,
                        tweet.user.screen_name,
                        tweet.user.location if tweet.user.location != '' else 'unknown',
                        tweet.created_at.replace(tzinfo=None),
                        text,
                        tweet.favorite_count,
                        tweet.retweet_count,
                        hashtag,
                        sent,
                        f"https://twitter.com/twitter/statuses/{tweet.id}"]
                    users_locs.append(locs)      

            if len(users_locs) == 0:
                continue
            tweet_text = pd.DataFrame(data=users_locs, 
                columns=['keyword','user','location','post date','tweet', 'favorite count', 'retweet count','hashtag','sentiment','tweet link'])
            tweet_text = tweet_text.sort_values('post date', ascending=True).reset_index(drop=True)     # sort by datetime

            # save to excel
            self.status = f'Saving to Excel'
            tweet_text.to_excel(f"./data/tweets/{keyword}/{day}.xlsx", engine="openpyxl", index=False)
            self.metadata['twitter-keyword'][keyword]['date'].append(day)
            self.save_metadata()
            print(f"save to file : {day}.xlsx")
            start_day -= timedelta(1)

    def get_status(self):
        return self.status


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
    text = [word for word in text_tokens 
        if (not word.lower() in stopwords.words("english")) and (len(word)>1)]

    text = ' '.join(text)
    return text

def word_tokenize_th(text):
    url ='https://api.aiforthai.in.th/lextoplus'

    headers = {'Apikey':"fIwWRjuLjs8KrK8BcA7kaj5das47eZpH"}
    
    params = {'text':text,'norm':'1'}
    
    response = requests.get(url, params=params, headers=headers)
    
    return response.json()['tokens']

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


def cleanText_th(tweet_text : list) -> list:
    def get_cleantext(text : str,index : int):

        text = re.sub('http://\S+|https://\S+', '', text) # remove url


        url = "https://api.aiforthai.in.th/textcleansing" #api for remove emoji
        
        params = {f'text':{text}}
        
        
        headers = {
            'Apikey': "fIwWRjuLjs8KrK8BcA7kaj5das47eZpH",
            }
        
        response = requests.request("GET", url, headers=headers, params=params)
        cleantext[index] = response.json()['cleansing_text']

    n = len(tweet_text)
    cleantext = [None] * n
    with ThreadPoolExecutor(max_workers=n) as executor:
        executor.map(get_cleantext, tweet_text, list(range(n)))
        executor.shutdown(wait=True)
    
    
    return cleantext

def sentiment_en(text : str) -> str:
    SENTIMENT = sentiment(TextBlob(stem(text)))
    return SENTIMENT
    
def sentiment_TH(text : str) -> str:
    url = "https://api.aiforthai.in.th/ssense"
    params = {'text':text}
    headers = {
        'Apikey': "fIwWRjuLjs8KrK8BcA7kaj5das47eZpH"
    }
    response = requests.get(url, headers=headers, params=params)

    try:
        if response.json()['sentiment']['polarity'] == '':
            polarity = "neutral"
        else:
            polarity = response.json()['sentiment']['polarity']
        return polarity
    except requests.exceptions.JSONDecodeError:
        return None

def sentiment_th(tweet_text : list) -> list:
    def get_sentiment(text : str, index : int):

        url = "https://api.aiforthai.in.th/ssense"
        params = {'text':text}
        headers = {
            'Apikey': "fIwWRjuLjs8KrK8BcA7kaj5das47eZpH"
        }
        response = requests.get(url, headers=headers, params=params)

        if response.json()['sentiment']['polarity'] == '':
            polarity = "neutral"
        else:
            polarity = response.json()['sentiment']['polarity']
        sentiment[index] = polarity

    n = len(tweet_text)
    sentiment = [None] * n
    with ThreadPoolExecutor(max_workers=n) as executor:
        executor.map(get_sentiment, tweet_text, list(range(n)))
        executor.shutdown(wait=True)

    return sentiment


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
    txt = re.sub('http://\S+|https://\S+', '', txt)
    return txt 

if not os.path.exists('./data'):
    os.mkdir('./data')

if __name__ == '__main__':
    import timeit
    _keyword = 'Batman'

    WB = WebCrawler()
    start = timeit.default_timer()
    f = WB.search_web(_keyword)
    print(f)
    stop = timeit.default_timer()
    print('Time: ', stop - start)