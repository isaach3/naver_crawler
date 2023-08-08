import csv
import os
from requests_html import HTMLSession
import sys
import concurrent.futures
from math import ceil
from multiprocessing import cpu_count
from bs4 import BeautifulSoup as bs
from selenium.webdriver import Chrome

s = HTMLSession()
base_url = 'https://cafe.naver.com/jihosoccer123?iframe_url=/ArticleList.nhn%3Fsearch.clubid=23611966%26search.menuid=461%26search.boardtype=L%26search.totalCount=151%26search.cafeId=23611966%26search.page='

def get_response(base_url,page=0):
    url = base_url+str(page)
    print(url)
    r = s.get(url)
    r_error_handler(r,url)
    return r

def r_error_handler(r,url):
    if r.status_code != 200:
        print("URL:",url)
        print("URL Status Code:",r.status_code)

def parse(r):
    print('good')
    return 1

def nav_each_page(url):
    print('.',end='')
    sys.stdout.flush()
    r = get_response(url)
    info = parse(r)
    return info

def save_to_csv(info):
    keys = ['Title','Author','Date Posted','Views','Likes','Content','Comments','Comment-Replies']
    try:
        with open('text_media.csv','a',encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f,keys)
            dict_writer.writerows(info)
    except Exception as e:
        print('Unable to save as CSV')
        print(e)

def nav_big_page(page_start = 1,page_end = 101):
    # refresh_directory(idx)
    lst = []
    for page in range(page_start,page_end):
        r = get_response(base_url,page)
        print('r:',r)
        print(f'Page {page}...',end='')
        sys.stdout.flush()
        
        script = """
    () => {
        return {
            width: document.documentElement.clientWidth,
            height: document.documentElement.clientHeight,
            deviceScaleFactor: window.devicePixelRatio,
        }
    }
"""
        print_s = r.html.render(sleep=2,script=script)
        print(print_s)
#         with open('file.txt','w') as sys.stdout:
        print(r.html.html)
        print(r.html.find('div.article-board'))
        print(r.html.find('div.article-board'))
        print(r.status_code)
        articles = r.html.xpath('//*[@id="main-area"]/div[4]',first=True)
        print(articles)
        with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()-2) as executor:
            chunksize = ceil(len(articles)/(cpu_count() - 2))
            for res in executor.map(nav_each_page,[article.find('div.subject',first=True).find('a',first=True).attrs['href'] for article in articles], chunksize=chunksize):
                if res['Title'] != 'n/a':
                    lst.append(res)
        save_to_csv(lst)
        print()
    return

def refresh_directory():
    # for f in os.listdir(os.getcwd()):
    #     if f.endswith(f'{idx+1}.csv'):
    #         os.remove(os.path.join(os.getcwd(),f))

    keys = ['Title','DateTime','Author','Category','Text','Images','Comments','Comment Count','Views']
    with open('naver.csv','w',encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f,keys)
        dict_writer.writeheader()


def main():
    refresh_directory()
    nav_big_page(1,11)

if __name__ == '__main__':
    main()
