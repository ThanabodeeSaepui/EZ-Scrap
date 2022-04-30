import re
import os
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

def count_link_ref(bs : BeautifulSoup, current_domain : str) -> Counter:
    c = Counter()
    s = set()
    for a in bs.find_all('a'):
        try:
            domain = urlparse(a.attrs['href']).netloc
            if (domain in default_domain) and (domain != current_domain):
                if domain not in s:
                    s.add(domain)
                    c[domain] += 1
                else:
                    continue
        except KeyError:    # no href found
            continue
    if current_domain in ['collider.com', 'www.cbr.com']:
        c['screenrant.com'] = 0
    if current_domain in ['screenrant.com']:
        c['www.cbr.com'] = 0
    return c

def get_data(domain : str) -> dict:
    if os.path.exists(f'./data/web-data/{domain}/data.json'):
        data = open(f'./data/web-data/{domain}/data.json', encoding="UTF-8")
        data = json.load(data)
        return data
    else:
        return {}
        
def get_metadata(domain : str) -> dict:
    if os.path.exists(f'./data/web-data/{domain}/metadata.json'):
        metadata = open(f'./data/web-data/{domain}/metadata.json', encoding="UTF-8")
        metadata = json.load(metadata)
        metadata['ref'] = Counter(metadata['ref'])
        metadata['web'] = set(metadata['web'])
        return metadata
    else:
        metadata = {
            'domain' : domain,
            'ref' : Counter(),
            'web' : set()
        }
        return metadata

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88) Gecko/20100101 Firefox/88.0'}

default_domain = [
    'collider.com',
    'editorial.rottentomatoes.com',
    'entertainment.ie',
    'movie2news.com',
    'movieweb.com',
    'screenrant.com',
    'wegotthiscovered.com',
    'www.cbr.com',
    'www.cinemablend.com',
    'www.empireonline.com',
    'www.hollywoodreporter.com',
    'www.irishtimes.com',
    'www.ign.com',
    'www.joblo.com',
    'www.movienewsnet.com',
    'www.nme.com',
    'www.sanook.com',
    'www.slashfilm.com',
    'www.thewrap.com',
    'www.firstshowing.net'
]