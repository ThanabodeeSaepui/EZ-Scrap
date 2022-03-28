from spider import *

if __name__ == '__main__':
    # webcrawler = WebCrawler()
    # webcrawler.scrap()

    tw_crawler = TwitterCrawler()
    tw_crawler.search_tweets("#IMDb")