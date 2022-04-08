from utils import *

def ScrapSite() -> dict:
    data = {}
    def sub_fetch(session, url):
        with session.get(url, headers=headers) as response:
            if not response.ok:
                return
            print(url)
            bs = BeautifulSoup(response.text, 'html.parser')
            bs = remove_unuse_tag(bs)

            data[url] = {}
            data[url]['title'] = bs.find('h1').text

            content = ''
            for p in bs.find_all('p'):
                content += f'{clean_html(p.text)} '
            data[url]['content'] = content

    def fetch(session, url):
        with session.get(url, headers=headers) as response:
            if not response.ok:
                return
            bs = BeautifulSoup(response.text, 'html.parser')
            bs = remove_unuse_tag(bs)

            news_link = []
            news = bs.find('div', {'class' : 'panel-body'})
            for a in news.find_all('a'):
                href = a.attrs['href']
                news_link.append(href)

            n = len(news_link)
            with ThreadPoolExecutor(max_workers=n) as executor:
                with requests.Session() as session:
                    executor.map(sub_fetch, [session]*n, news_link)
                    executor.shutdown(wait=True)


    pages_list = [f'https://editorial.rottentomatoes.com/news/?wpv_paged={i}' for i in range(1, 11)]
    n = len(pages_list)
    with ThreadPoolExecutor(max_workers=n) as executor:
        with requests.Session() as session:
            executor.map(fetch, [session]*n, pages_list)
            executor.shutdown(wait=True)

    return data

if __name__ == '__main__':
    data = ScrapSite()
    with open(f'rottentomatoes.json', 'w', encoding="UTF-8") as outfile:
        JSON = json.dumps(data, indent=4) 
        outfile.write(JSON)