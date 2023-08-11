from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import concurrent.futures
from multiprocessing import cpu_count,Process
from math import ceil
import random as r
from datetime import datetime
import csv
import sys
import time


base_url = "https://cafe.naver.com/jihosoccer123?iframe_url=/ArticleList.nhn%3Fsearch.clubid=23611966%26search.menuid=461%26userDisplay=50%26search.boardtype=L%26search.totalCount=501%26search.cafeId=23611966%26search.page="
opp = Options()
opp.add_argument('--no-sandbox')
opp.add_argument('--disabled-dev-shm-usage')
opp.add_argument('--blink-settings=imagesEnabled=false')
driver = webdriver.Chrome(options=opp)  # You can use other drivers as well (e.g., Firefox)


def login(user,pw):
    driver.get('https://nid.naver.com/nidlogin.login')
    driver.implicitly_wait(1 + (0.1 * r.randint(5,10)))
    driver.find_element('id','id').send_keys(user)
    driver.find_element('id','pw').send_keys(pw)
    driver.find_element('id','log.login').click()
    driver.implicitly_wait(1.5 + (0.1 * r.randrange(1,10)))
    print(driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div[1]/form/ul/li/div/div[3]/div[1]/p[1]/img').get_attribute('src'))
    WebDriverWait(driver,60).until_not(EC.presence_of_element_located((By.CSS_SELECTOR,'#container > div > div.login_wrap.global')))
    

def init_page(url):
    driver.get(url)
    driver.implicitly_wait(1 + (0.1 * r.randint(5,10)))
    iframe = driver.find_element('id','cafe_main')
    driver.switch_to.frame(iframe)
    driver.implicitly_wait(2 + (0.1 * r.randint(5,10)))

def gather_links():
    articles = driver.find_elements(By.CLASS_NAME,'article-board')[1].find_elements(By.TAG_NAME,'tr')
    links = []
    for article in articles[::2]:
        article_number = article.find_element(By.CLASS_NAME,'inner_number').text
        article_href = article.find_element(By.CLASS_NAME,'inner_list').find_element(By.TAG_NAME,'a').get_attribute('href')
        links.append((article_number,article_href))
    return links

def gather_comment_info(comment):
    # comment_lst = []
    # for comment in comments:
    try:
        author = comment.find_element(By.CLASS_NAME,'comment_nickname').text
        post_datetime = datetime.strptime(comment.find_element(By.CLASS_NAME,'comment_info_date').text,'%Y.%m.%d. %H:%M')
        text = comment.find_element(By.CLASS_NAME,'text_comment').text
        # img_objs = comment.find_elements(By.CLASS_NAME,'image')
        # if img_objs:
        #     imgs = [image.get_attribute('src') for image in img_objs]
        # else:
        #     imgs = []
        return {
            'Author':author,
            'Post Date':post_datetime,
            'Text':text,
            #'Images':imgs
        }
    except Exception as e:
        print('Failed to add comment')
        print(e)
        sys.stdout.flush()
    # return comment_lst


def nav_small_page(link):
    # s = time.time()
    init_page(link)
    title = driver.find_element(By.CLASS_NAME,'title_text').text
    author = driver.find_element(By.CLASS_NAME,'nick_box').text
    level = driver.find_element(By.CLASS_NAME,'nick_level').text
    post_datetime = datetime.strptime(driver.find_element(By.CLASS_NAME,'date').text, '%Y.%m.%d. %H:%M')
    text = '\n'.join([cont.text for cont in driver.find_elements(By.CLASS_NAME,'se-text-paragraph')])
    imgs = [img.get_attribute('src') for img in driver.find_elements(By.CLASS_NAME,'se-image-resource')]
    # comment_elems = gather_comment_info(driver.find_elements(By.CLASS_NAME,'CommentItem'))
    comment_elems = driver.find_elements(By.CLASS_NAME,'CommentItem')
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        results = executor.map(gather_comment_info, comment_elems)
    all_comments = [result for result in results if result is not None]
    likes = driver.find_element(By.CLASS_NAME,'u_cnt').text
    views = driver.find_element(By.CLASS_NAME,'count').text[3:]
    # print(time.time() - s)
    return title,author,level,post_datetime,text,imgs,all_comments,likes,views

def save_to_csv(lst):
    keys = ['Post ID','Post Link','Title','Author','Author Level','Post Date','Text','Images','Comments','Likes','Views']
    try:
        with open('naver.csv','a',encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f,keys)
            dict_writer.writerows(lst)
    except Exception as e:
        print('Unable to save CSV')
        print(e)
        sys.stdout.flush()

def nav_big_pages(start=1,end=101):
    page = start
    while page < end:
        try:
            print(f'Page {page}...',end='')
            count = 1
            sys.stdout.flush()
            init_page(base_url+str(page))
            num_links = gather_links()
        except Exception as e:
            print('Failed on page',page)
            print('URL:',link)
            print(e)
            sys.stdout.flush()
        else:
            lst = []
            for num,link in num_links[:]:
                try:
                    title,author,level,post_datetime,text,imgs,all_comments,likes,views = nav_small_page(link)
                    lst.append({
                            'Post ID':num,
                            'Post Link':link,
                            'Title':title,
                            'Author':author,
                            'Author Level':level,
                            'Post Date':post_datetime,
                            'Text':text,
                            'Images':imgs,
                            'Comments':all_comments,
                            'Likes':likes,
                            'Views':views
                        })
                    print('.',end='')
                    count += 1
                    sys.stdout.flush()
                except Exception as e:
                    print('Failed to complete post',count)
                    print(link)
                    print(e)
                    sys.stdout.flush()
                    continue
            save_to_csv(lst)
            
        
        print()
        page += 1
    


def init_directory():
    keys = ['Post ID','Post Link','Title','Author','Author Level','Post Date','Text','Images','Comments','Likes','Views']
    with open('naver.csv','w',encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f,keys)
        dict_writer.writeheader()

def main():
    # init_directory()
    login('ihong0806','Isaac7736.')
    nav_big_pages(175,401)
    driver.quit()

if __name__ == '__main__':
    main()
