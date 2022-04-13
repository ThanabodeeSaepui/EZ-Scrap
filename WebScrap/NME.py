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

            data['web'][url] = {}
            data['web'][url]['title'] = bs.find('h1').text

            content = ''
            section = bs.find('div', {'data-td-block-uid' : 'tdi_95'})
            for p in section.find_all('p'):
                content += f'{clean_html(p.text)} '
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
            for h3 in bs.find_all('h3', {'class' : 'entry-title'}):
                a = h3.find('a')
                news_link.append(a.attrs['href'])
            data['ref'] += count_link_ref(bs, domain)

            n = len(news_link)
            with ThreadPoolExecutor(max_workers=n) as executor:
                with requests.Session() as session:
                    executor.map(sub_fetch, [session]*n, news_link)
                    executor.shutdown(wait=True)


    pages_list = [f'https://www.nme.com/news/film/page/{i}' for i in range(1, 11)]
    n = len(pages_list)
    with ThreadPoolExecutor(max_workers=n) as executor:
        with requests.Session() as session:
            executor.map(fetch, [session]*n, pages_list)
            executor.shutdown(wait=True)
    data['domain'] = 'www.nme.com'
    return data


if __name__ == '__main__':
    data = ScrapSite()
    with open(f'nme.json', 'w', encoding="UTF-8") as outfile:
        JSON = json.dumps(data, indent=4) 
        outfile.write(JSON)