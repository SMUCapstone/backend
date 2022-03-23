# 모듈 
import pandas as pd 
from bs4 import BeautifulSoup 
from selenium import webdriver 
from webdriver_manager.chrome import ChromeDriverManager 
from tqdm import tqdm 
import time 
import re 

def comment_scrap(url, driver):
    # 크롤링 목표 : 해당 영상에 대한 댓글 id, 댓글 내용, 댓글의 좋아요 개수 추출
    data_list = [] 
    driver.get(url) 
    # 스크롤 내리기 
    body = driver.find_element_by_tag_name('body') 
    last_page_height = driver.execute_script("return document.documentElement.scrollHeight") 
    while True: 
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);") 
        # driver.execute_script("window.scrollTo(0,1000)")
        time.sleep(2)
        new_page_height = driver.execute_script("return document.documentElement.scrollHeight") 
        # print(new_page_height, last_page_height)
        if new_page_height == last_page_height: 
            break
        last_page_height = new_page_height
    html0 = driver.page_source 
    html = BeautifulSoup(html0, 'html.parser') 
    comments_list = html.findAll('ytd-comment-thread-renderer', {'class': 'style-scope ytd-item-section-renderer'})


    for j in range(len(comments_list)): 
        ## 댓글 내용 
        comment = comments_list[j].find('yt-formatted-string', {'id': 'content-text'}).text 
        comment = comment.replace('\n', '')         # 줄 바뀜 없애기 
        comment = comment.replace('\t', '')         # 탭 줄이기 
        ## 유튜브 id 
        youtube_id = comments_list[j].find('a', {'id': 'author-text'}).span.text 
        youtube_id = youtube_id.replace('\n', '') # 줄 바뀜 없애기 
        youtube_id = youtube_id.replace('\t', '') # 탭 줄이기 
        youtube_id = youtube_id.strip() 
        ## 댓글 좋아요 개수 (0인 경우 예외 처리) 
        try: 
            like_num = comments_list[j].find('span', {'id': 'vote-count-middle', 'class': 'style-scope ytd-comment-action-buttons-renderer', 'aria-label': re.compile('좋아요')}).text 
            like_num = like_num.replace('\n', '') # 줄 바뀜 없애기 
            like_num = like_num.replace('\t', '') # 탭 줄이기 
            like_num = like_num.strip() 
        except: 
            like_num = 0 
        data = {'comment': comment, 'youtube_id': youtube_id, 'like_num': like_num} 
        data_list.append(data) 

    return data_list

def initial():
    # 셀레니움 옵션 설정 
    options = webdriver.ChromeOptions() 
    options.add_argument('headless')  # 크롬 띄우는 창 없애기 
    options.add_argument('window-size=1920x1080') # 크롬드라이버 창크기 
    options.add_argument("disable-gpu") # 그래픽 성능 낮춰서 크롤링 성능 쪼금 높이기 
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36") # 네트워크 설정 
    options.add_argument("lang=ko_KR") # 사이트 주언어 
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    return driver


def main():
    driver = initial()