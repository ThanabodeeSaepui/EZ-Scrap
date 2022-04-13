from .utils import *

def ScrapSite() -> dict:
    data = {}
    data['web'] = {}
    data['ref'] = Counter()

    def fetch(session, url):
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
            section = bs.find('div', {'class' : 'columns-holder'})
            for p in section.find_all('p'):
                content += f'{clean_html(p.text)} '
            data['web'][url]['content'] = content
            data['ref'] += count_link_ref(bs, domain)


    pages_list = []
    start = 1
    for _ in range(10):
        url = f'https://www.slashfilm.com/category/movies/?ajax=1&offset={start}&action=more-stories'
        response = requests.get(url , headers=headers)
        if response.ok:
            bs = BeautifulSoup(response.text, 'html.parser')
            for h3 in bs.find_all('h3'):
                a = h3.find('a').attrs['href']
                pages_list.append(f'https://www.slashfilm.com/{a}')
            domain = urlparse(url).netloc
            data['ref'] += count_link_ref(bs, domain)
            start = len(pages_list) + 1
        n = len(pages_list)

    with ThreadPoolExecutor(max_workers=n) as executor:
        with requests.Session() as session:
            executor.map(fetch, [session]*n, pages_list)
            executor.shutdown(wait=True)
    data['domain'] = 'www.slashfilm.com'
    return data


if __name__ == '__main__':
    data = ScrapSite()
    with open(f'slashfilm.json', 'w', encoding="UTF-8") as outfile:
        JSON = json.dumps(data, indent=4) 
        outfile.write(JSON)