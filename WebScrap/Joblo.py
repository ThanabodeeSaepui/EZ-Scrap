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
            section = bs.find('div', {'class' : 'post-content'})
            for p in section.find_all('p'):
                content += f'{clean_html(p.text)} '
            data[url]['content'] = content

    def fetch(session, url):
        with session.get(url, headers=headers) as response:
            if not response.ok:
                return
            bs = BeautifulSoup(response.text, 'html.parser')
            bs = remove_unuse_tag(bs)

            news_link = []
            news = bs.find('div', {'class' : 'content'})
            for article in news.find_all('article'):
                a = article.find('h3').find('a').attrs['href']
                print(f'{a}')
                news_link.append(f'{a}')
            n = len(news_link)

            with ThreadPoolExecutor(max_workers=n) as executor:
                with requests.Session() as session:
                    executor.map(sub_fetch, [session]*n, [*news_link])
                    executor.shutdown(wait=True)


    pages_list = [f'https://www.joblo.com/movie-news/page/{i}/' for i in range(1, 11)]
    n = len(pages_list)
    with ThreadPoolExecutor(max_workers=n) as executor:
        with requests.Session() as session:
            executor.map(fetch, [session]*n, pages_list)
            executor.shutdown(wait=True)

    return data


if __name__ == '__main__':
    data = ScrapSite()
    with open(f'joblo.json', 'w', encoding="UTF-8") as outfile:
        JSON = json.dumps(data, indent=4) 
        outfile.write(JSON)