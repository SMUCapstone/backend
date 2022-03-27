from bs4 import BeautifulSoup 
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from webdriver_manager.chrome import ChromeDriverManager 
import time 
import re 
import Database

def comment_scrap(url, driver):
    # 크롤링 목표 : 해당 영상에 대한 댓글 id, 댓글 내용, 댓글의 좋아요 개수 추출
    data_list = [] 
    driver.get(url) 
    # 스크롤 내리기 
    comment_num = driver.find_element(By.CSS_SELECTOR, '#title #count span:nth-child(2)')
    last_page_height = driver.execute_script("return document.documentElement.scrollHeight") 
    while True: 
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);") 
        time.sleep(2)
        new_page_height = driver.execute_script("return document.documentElement.scrollHeight") 
        if new_page_height == last_page_height: 
            break
        last_page_height = new_page_height
    html0 = driver.page_source 
    html = BeautifulSoup(html0, 'html.parser') 
    comments_list = html.findAll('ytd-comment-thread-renderer', {'class': 'style-scope ytd-item-section-renderer'})


    for j in range(len(comments_list)): 
        ## 댓글 내용 
        comment = comments_list[j].find('yt-formatted-string', {'id': 'content-text'}).text 
        comment = comment.replace('\n', '')          
        comment = comment.replace('\t', '')        
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
        data = {'comment': comment, 'like_num': like_num, 'youtube_id': youtube_id} 
        data_list.append(data) 

    #### 혜원님이 DB 만들어주시면 DB에 올리는 함수 호출
    
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
    youtuber_ID = url.split('/c/')[-1].split('/')[0]
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

        # print({'video_url': video_url, 'thumb_img': thumb_img, 'title': title, 'view_num': view_num} )
        tasklist.append({'id':youtuber_ID, 'video_url': video_url, 'video_name': title, 'thumb_img': thumb_img, 'hits': view_num} ) 

    ###return 하지 않아도a tasklist 에 값이 저장되어있음
    return None


def main(channel_url):
    tasklist = []
    driver = initial()
    channel_collector(tasklist, channel_url, driver)
    for task in tasklist:
        print(task)
        url = task['video_url']
        comment_num = comment_scrap(url, driver)
        task['comment_num'] = comment_num
        content = Database.Content(task['id'], task['url'], task['video_name'], task['thunbnail'], task['hits'], task['comment_num'])
        Database.insert_content(content)

if __name__=="__main__":
    channel_url = input()
    main(channel_url)