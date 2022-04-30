import time
from .utils import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def ScrapSite(driver_path='./SeleniumDriver/chromedriver.exe'):
    data = {}
    data['data'] = get_data('entertainment.ie')
    data['metadata'] = get_metadata('entertainment.ie')
    data['metadata']['lang'] = 'en'

    def get_article_urls() -> list:
        driver = webdriver.Chrome(driver_path)
        driver.get('https://entertainment.ie/movies/movie-news/')

        SCROLL_PAUSE_TIME = 2.5
        article_count = [0, 0]
        articles = None
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            section = WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@class="row posts-block"]'))
            )
            articles = section.find_elements(By.XPATH, '//article')
            article_count[1] = len(articles)
            if (article_count[0] == article_count[1]) or (len(articles) >= 150):
                break
            else:
                article_count[0] = article_count[1]
        urls = []
        for article in articles:
            a = article.find_element(By.TAG_NAME, 'a')
            href = a.get_attribute('href')
            urls.append(href)
        return urls

    def fetch(session, url):
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
            data['data'][url]['title'] = bs.find('h1').text

            content = ''
            section = bs.find('div', {'class' : 'rest'})
            for p in section.find_all(['p','h3']):
                content += f'{clean_html(p.text)} '
            data['data'][url]['content'] = content
            data['metadata']['ref'] += count_link_ref(bs, domain)

    urls = get_article_urls()
    n = len(urls)
    with ThreadPoolExecutor(max_workers=n) as executor:
        with requests.Session() as session:
            executor.map(fetch, [session]*n, urls)
            executor.shutdown(wait=True)
    return data

if __name__ == '__main__':
    data = ScrapSite()
    with open(f'entertainment.json', 'w', encoding="UTF-8",) as outfile:
        JSON = json.dumps(data['data'], indent=4, ensure_ascii=False) 
        outfile.write(JSON)