import pandas
from googleapiclient.discovery import build
import time
import Database
import requests
import json
 
class youtubeAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_obj = build('youtube', 'v3', developerKey=self.api_key)
        self.comment = []
        self.like = 0
        self.pageToken = '' 

    def get_youtuber(self, channelId):
        url = f'https://www.googleapis.com/youtube/v3/channels?id={channelId}&part=snippet&part=statistics&key={self.api_key}'
        result = json.loads(requests.get(url).text)['items'][0]
        youtuber_ID = channelId
        channel_name = result['snippet']['title']
        profile_img = result['snippet']['thumbnails']['high']['url']
        ## 유튜버 테이블 만들기, 중복에러는 DB에서 처리// 유튜버id, 채널명, 프로필 이미지
        youtuber_info = Database.Youtuber(youtuber_ID, channel_name, profile_img)

        Database.insert_youtuber_info(youtuber_info)
        
    def get_contents(self):
        response = self.api_obj.channels().list(part='contentDetails', id='UCLAgUdDB5AacEGtPqyTBD0w').execute()
        uploads = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        # 결과값으로 나온 upload 값을 이용.
        response = self.api_obj.playlistItems().list(part='snippet', playlistId=uploads).execute()
        #response['items'] 안에 리스트가 플레이리스트고, 기본값으로 5개씩 리턴, maxResults 속성 최대값
        # 은 50 , 더 있을경우 ['nextPageToken'] 리턴
        # 제목 ['snippet']['title']
        # 썸네일 ['snippet']['thumbnails']['standard']['url']
        # url 은 
        # 조회수는
        # 댓글 수는

    def get_playlist(self):
        response = self.api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, maxResults=100).execute()
        # 유튜버 아이디, url, 동영상 title, 동영상 썸네일, 조회수, 댓글 수
        content = Database.Content(task['id'], task['video_url'], task['video_name'], task['thumbnail'], task['hits'], task['comment_num'])
        Database.insert_content(content)

    def get_comment_and_likes(self, video_id):
        def remove_a_tag(string):
            string = string.replace('<br>','')
            string = string.replace('&quot;','"')
            if 'a href' in string:
                string = string.replace('</a>','')
                string = string.replace(string[string.index('<a'):string.index('">')+2],'')
            return string

        comments = list()
        api_obj = self.api_obj
        response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, maxResults=100).execute()

        while response:
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append([remove_a_tag(comment['textDisplay']), comment['likeCount']])
        
                if item['snippet']['totalReplyCount'] > 0:
                    for reply_item in item['replies']['comments']:
                        reply = reply_item['snippet']
                        comments.append([remove_a_tag(reply['textDisplay']), reply['likeCount']])
        
            if 'nextPageToken' in response:
                try:
                    response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, pageToken=response['nextPageToken'], maxResults=100).execute()
                except:
                    return response['nextPageToken']
                    # self.pageToken = response['nextPageToken']
                    # response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, pageToken=response['nextPageToken'], maxResults=100).execute()
            else:
                return comments
 
if __name__=="__main__":
    # api_key = 'AIzaSyCEwR4BXNL_ZxJgy6JTBcu2_wYuwS3RnDo'    
    api_key = 'AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A'     ## 발급받은 api 키
    video_id = 'kLUAqWu3YzU'                                ## 동영상 id watch?v= 다음
    api = youtubeAPI(api_key)
    api.get_comment_and_likes()
    returnvalue = api.get_comment_and_likes(video_id)
