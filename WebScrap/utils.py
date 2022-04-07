import re
import json
from collections import Counter
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def clean_html(html : str) -> str:
    clean = re.compile('<.*?>')
    clean_text = re.sub(clean, '', html)     # remove all html tag
    for char in ['\n', '\t', '\r']:          # remove escape character
        clean_text = clean_text.replace(char, '')
    clean_text = re.sub(' +', ' ', clean_text)
    return clean_text

def remove_unuse_tag(bs : BeautifulSoup) -> BeautifulSoup:
    unuse_tag = ['script', 'style ', 'noscript', 'head', 'footer', 'iframe']
    for tag in unuse_tag:
        for s in bs.select(tag):
            if s != None:
                s.extract()
    return bs

def count_link_ref(bs : BeautifulSoup) -> Counter:
    c = Counter()
    for a in bs.find_all('a'):
        domain = urlparse(a.attrs['href']).netloc
        c[domain] += 1
    return c

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88) Gecko/20100101 Firefox/88.0'}

default_domain = [
    'collider.com',
    'editorial.rottentomatoes.com',
    'movieweb.com',
    'screenrant.com',
    'wegotthiscovered.com',
    'www.bbc.com',
    'www.cbr.com',
    'www.cinemablend.com',
    'www.empireonline.com',
    'www.euronews.com',
    'www.hollywoodreporter.com',
    'www.imdb.com',
    'www.irishtimes.com',
    'www.joblo.com',
    'www.movienewsnet.com',
    'www.nme.com',
    'www.nytimes.com',
    'www.rollingstone.com',
    'www.slashfilm.com',
    'www.thewrap.com'
]