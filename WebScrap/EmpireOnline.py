from .utils import *

def ScrapSite() -> dict:
    data = {}
    data['data'] = get_data('www.empireonline.com')
    data['metadata'] = get_metadata('www.empireonline.com')
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
            data['data'][url]['title'] = bs.find('h1', {'class' : 'title'}).text

            content = ''
            section = bs.find('div', {'class' : 'article-content'})
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

            news_link = set()
            main_content = bs.find('div', {'class': 'content'})
            for content in main_content.find_all('div', {'class': ['cards-hero', 'cards-inline']}):
                for a in content.find_all('a'):
                    a = a.attrs['href']
                    news_link.add(f'https://{domain}/{a}')
            data['metadata']['ref'] += count_link_ref(bs, domain)
            
            n = len(news_link)
            with ThreadPoolExecutor(max_workers=n) as executor:
                with requests.Session() as session:
                    executor.map(sub_fetch, [session]*n, news_link)
                    executor.shutdown(wait=True)


    pages_list = [f'https://www.empireonline.com/movies/news/{i}/' for i in range(1, 11)]
    n = len(pages_list)
    with ThreadPoolExecutor(max_workers=n) as executor:
        with requests.Session() as session:
            executor.map(fetch, [session]*n, [*pages_list])
            executor.shutdown(wait=True)
    return data


if __name__ == '__main__':
    data = ScrapSite()
    with open(f'empireonline.json', 'w', encoding="UTF-8") as outfile:
        JSON = json.dumps(data, indent=4) 
        outfile.write(JSON)