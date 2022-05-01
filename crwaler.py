from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from webdriver_manager.chrome import ChromeDriverManager 
import time 
import re 
import Database
import urllib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from youtubeAPI import get_comment_and_likes


def toInteger(string):
    mul = 0
    string = string.replace('회', '')
    if '천' in string:
        string = string.replace('천', '')
        mul = 1000
    elif '만' in string:
        string = string.replace('만', '')
        mul = 10000
    elif '억' in string:
        string = string.replace('억', '')
        mul = 10**8
    else:
        mul = 1
    
    return float(string)*mul

def url_validation(url):
    x = url.split("/")
    i = 0
    print(x)
    try:
        # 프로토콜이 적혀있는가? 
        if x[i] != 'https:':
            url = 'https://' + url
            i+=1
        else:
            i+=2
        # 유튜브 url이 맞는가?
        if x[i] == 'www.youtube.com':
            i+=1
        else:
            return -1
        # 유튜브 채널 페이지가 맞는가?
        if x[i]=='c' or x[i]=='channel':
            c = x[i]
            chn = x[i+1]
            i+=2
        else:
            return -1
    except:
        return -1
    # 채널 비디오 페이지가 맞는가?

    url = f'https://www.youtube.com/{c}/{chn}/videos' 
    return url


        
def get_comment_num(url, driver):
    # 크롤링 목표 : 해당 영상에 대한 댓글 id, 댓글 내용, 댓글의 좋아요 개수 추출
    driver.get(url) 
    # 스크롤 내리기 
    comment_num = WebDriverWait(driver, 10).until(lambda x: x.find_element(By.CSS_SELECTOR, '#title #count span:nth-child(2)')).text

    return comment_num


def initial():
    # 셀레니움 옵션 설정 
    options = webdriver.ChromeOptions() 
    # options.add_argument('headless')  # 크롬 띄우는 창 없애기 
    # options.add_argument('window-size=1920x1080') # 크롬드라이버 창크기 
    # options.add_argument("disable-gpu") # 그래픽 성능 낮춰서 크롤링 성능 쪼금 높이기 
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36") # 네트워크 설정 
    options.add_argument("lang=ko_KR") # 사이트 주언어 
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    return driver

def channel_collector(tasklist, url, driver):
    # 크롤링 목표 : 해당 채널에 속한 영상의 url, 썸네일, 제목, 조회수, 댓글 수
    driver.get(url) 
    driver.implicitly_wait(5)
    # youtuber_ID, channel_name, profile_img
    container = driver.find_element(By.CSS_SELECTOR, "#channel-header-container")
    profile_img = container.find_element(By.CSS_SELECTOR, "#img").get_attribute("src")
    channel_name = container.find_element(By.CSS_SELECTOR, "#text").text
    if '/c/' in url:
        youtuber_ID = url.split('/c/')[-1].split('/')[0]
    elif '/channel/' in url:
        youtuber_ID = url.split('/channel/')[-1].split('/')[0]
    else:
        pass
    print("여기까진 돌았다.")
    ## 유튜버 테이블 만들기, 중복에러는 DB에서 처리
    youtuber_info = Database.Youtuber(youtuber_ID, channel_name, profile_img)

    Database.insert_youtuber_info(youtuber_info)
    

    # 스크롤 내리기 
    last_page_height = driver.execute_script("return document.documentElement.scrollHeight") 
    elements = []
    while True: 
        new_elements = driver.find_elements_by_css_selector("#dismissible")
        for source in new_elements:
            if source in elements:
                pass
            else:
                elements.append(source)

        # url, 썸네일, 제목, 조회수, 댓글 수
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);") 
        # driver.execute_script("window.scrollTo(0,1000)")
        time.sleep(1)
        new_page_height = driver.execute_script("return document.documentElement.scrollHeight") 
        # print(new_page_height, last_page_height)
        if new_page_height == last_page_height: 
            break
        last_page_height = new_page_height

    html0 = driver.page_source 
    html = BeautifulSoup(html0, 'html.parser') 
    video_list = html.findAll('ytd-grid-video-renderer', {'class': 'style-scope ytd-grid-renderer'})

    

    for j in range(len(video_list)): 
        ##  url,
        video_url = video_list[j].find('a', {'id': 'video-title'}).get('href') #find_element_by_css_selector('#thumbnail').get_attribute('href') #a 태그
        video_url = "https://www.youtube.com"+video_url

        ##  썸네일, 
        
        if 'watch?v=' in video_url:
            vid = video_url.split('watch?v=')[-1]
            thumb_img = f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg' 
        else:
            vid = video_url.split('/')[-1]
            thumb_img = f'https://i.ytimg.com/vi/{vid}/hq2.jpg' 

        ##  제목
        title = video_list[j].find('a', {'id': 'video-title'}).text 

        #  조회수, 
        view_num = video_list[j].find('div', {'id': 'metadata-line'}).findAll('span')[0].text 
        view_num = view_num.split("\n")[0].replace("조회수 ","")
        hits = toInteger(view_num)

        # print({'video_url': video_url, 'thumb_img': thumb_img, 'title': title, 'view_num': view_num} )
        tasklist.append({'id':youtuber_ID, 'video_url': video_url, 'video_name': title, 'thumbnail': thumb_img, 'hits': hits} ) 

    ###return 하지 않아도a tasklist 에 값이 저장되어있음
    return None


def main(channel_url):
    channel_url= urllib.parse.unquote(channel_url)
    tasklist = []
    youtube_api_key = 'AIzaSyCEwR4BXNL_ZxJgy6JTBcu2_wYuwS3RnDo'
    driver = initial()
    channel_collector(tasklist, channel_url, driver)
    max_num = 0
    for task in tasklist:
        max_num +=1
        if max_num > 100:
            print("끝")
            break
        url = task['video_url']
        print(url)
        comment_num = get_comment_num(url, driver)
        video_id = url.split('watch?v=')[-1]
        datalist = get_comment_and_likes(youtube_api_key, video_id)        #여기에 댓글 원문과 댓글 좋아요 수가 리스트로 저장됨.
        task['comment_num'] = int(comment_num.replace(',',''))
        content = Database.Content(task['id'], task['video_url'], task['video_name'], task['thumbnail'], task['hits'], task['comment_num'])
        Database.insert_content(content)
        # recognize Content객채의 recognize 값을 받아온 다음 recognize테이블 생성
        recognize = content.recognize
        Database.create_raw_comment_table(recognize)
        # Rawcomment 객체 생성해서 DB에 저장.
        # data = {'comment': comment, 'like_num': like_num, 'youtube_id': youtube_id}
        for data in datalist:
            r = Database.Rcomment(data[0], data[1])
            Database.insert_raw_comment(recognize, r)
    print('끝')

if __name__=="__main__":
    channel_url = input()
    main(channel_url)