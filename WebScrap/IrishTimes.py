from .utils import *

def ScrapSite() -> dict:
    data = {}
    data['web'] = {}
    data['ref'] = Counter()

    def sub_fetch(session, url):
        with session.get(url, headers=headers) as response:
            if not response.ok:
                return
            print(url)
            domain = urlparse(url).netloc
            bs = BeautifulSoup(response.text, 'html.parser')
            bs = remove_unuse_tag(bs)

            content = ''
            section = bs.find('div', {'class' : 'article_bodycopy'})
            for p in section.find_all('p'):
                content += f'{clean_html(p.text)} '
            if content == 'If you are reading this on the Irish Times app, click here to play. ':
                return
            data['web'][url] = {}
            data['web'][url]['title'] = bs.find('h1').text
            data['web'][url]['content'] = content
            data['ref'] += count_link_ref(bs, domain)

    def fetch(session, url):
        with session.get(url, headers=headers) as response:
            if not response.ok:
                return
            domain = urlparse(url).netloc
            bs = BeautifulSoup(response.text, 'html.parser')
            bs = remove_unuse_tag(bs)

            news_link = []
            news = bs.find('div', {'class' : 'sectionteaser'})
            for article in news.find_all('div', {'class': 'story'}):
                a = article.find('a').attrs['href']
                print(f'https://{domain}/{a}')
                news_link.append(f'https://{domain}/{a}')
            data['ref'] += count_link_ref(bs, domain)
            n = len(news_link)

            with ThreadPoolExecutor(max_workers=n) as executor:
                with requests.Session() as session:
                    executor.map(sub_fetch, [session]*n, [*news_link])
                    executor.shutdown(wait=True)


    pages_list = [f'https://www.irishtimes.com/culture/film?sectionTeaserPage-7.4113653={i}' for i in range(1, 6)]
    n = len(pages_list)
    with ThreadPoolExecutor(max_workers=n) as executor:
        with requests.Session() as session:
            executor.map(fetch, [session]*n, pages_list)
            executor.shutdown(wait=True)
    data['domain'] = 'www.irishtimes.com'
    return data


if __name__ == '__main__':
    data = ScrapSite()
    with open(f'irishtimes.json', 'w', encoding="UTF-8") as outfile:
        JSON = json.dumps(data, indent=4) 
        outfile.write(JSON)