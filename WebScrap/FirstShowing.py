from .utils import *

def ScrapSite() -> dict:
    data = {}
    data['data'] = get_data('www.firstshowing.net')
    data['metadata'] = get_metadata('www.firstshowing.net')
    data['metadata']['lang'] = 'en'

    def sub_fetch(session, url):
        if url in data['metadata']['web']:
            return
        with session.get(url, headers=headers) as response:
            if not response.ok:
                return
            data['metadata']['web'].add(url)
            print(url)
            domain = urlparse(url).netloc
            bs = BeautifulSoup(response.text, 'html.parser')
            bs = remove_unuse_tag(bs)

            data['data'][url] = {}
            data['data'][url]['title'] = bs.find('h2').text

            content = ''
            section = bs.find('div', {'class' : 'review'})
            for p in section.find_all('p'):
                content += f'{clean_html(p.text)} '
            data['data'][url]['content'] = content
            data['metadata']['ref'] += count_link_ref(bs, domain)

    def fetch(session, url):
        with session.get(url, headers=headers) as response:
            if not response.ok:
                return
            domain = urlparse(url).netloc
            bs = BeautifulSoup(response.text, 'html.parser')
            bs = remove_unuse_tag(bs)

            news_link = []
            news = bs.find('div', {'id' : 'content'})
            for article in news.find_all('div', {'class' : 'article'}):
                a = article.find('a')
                news_link.append(a.attrs['href'])
            data['metadata']['ref'] += count_link_ref(bs, domain)
            n = len(news_link)
            with ThreadPoolExecutor(max_workers=n) as executor:
                with requests.Session() as session:
                    executor.map(sub_fetch, [session]*n, news_link)
                    executor.shutdown(wait=True)


    pages_list = [f'https://www.firstshowing.net/category/movie-news/page/{i}/' for i in range(1, 11)]
    n = len(pages_list)
    with ThreadPoolExecutor(max_workers=n) as executor:
        with requests.Session() as session:
            executor.map(fetch, [session]*n, pages_list)
            executor.shutdown(wait=True)
    return data


if __name__ == '__main__':
    data = ScrapSite()
    with open(f'firstshowing.json', 'w', encoding="UTF-8") as outfile:
        JSON = json.dumps(data['data'], indent=4) 
        outfile.write(JSON)