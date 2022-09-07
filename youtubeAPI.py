from multiprocessing.dummy import Array
import pandas
from googleapiclient.discovery import build
import time

from pymysql import NULL
import Database
import requests
import json
import re

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
        
    def get_contents(self, CID, pageToken = ''):
        resultArr = []
        # response = self.api_obj.channels().list(part='contentDetails', id='UCLAgUdDB5AacEGtPqyTBD0w').execute()
        # uploads = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        # # 결과값으로 나온 uploads 값을 이용.
        # if pageToken:
        #     response = self.api_obj.playlistItems().list(part='snippet', playlistId=uploads, pageToken = pageToken, maxResults = 30).execute()
        # else:
        #     response = self.api_obj.playlistItems().list(part='snippet', playlistId=uploads, maxResults = 30).execute()
        if pageToken:
            response = self.api_obj.search().list(part='snippet', channelId=CID, pageToken = pageToken, order='viewCount', type='video', maxResults = 30).execute()
        else:
            response = self.api_obj.search().list(part='snippet', channelId=CID, order='viewCount', type='video', maxResults = 30).execute()
        nextPageToken = response.get('nextPageToken', '')
        prevPageToken = response.get('prevPageToken', '')
        for item in response['items']:
            videoid = item['id']['videoId']
            print(videoid)
            title =  item['snippet']['title']
            thumbnail = item['snippet']['thumbnails']['high']['url']
            response = self.api_obj.videos().list(part='snippet, statistics', id=videoid).execute()
            url = f'www.youtube.com/watch?v={videoid}'
            hits =  response['items'][0]['statistics'].get('viewCount','0')
            comment_num =  response['items'][0]['statistics'].get('commentCount','0')
            resultArr.append({'id':videoid, 'video_name':title, 'thumbnail':thumbnail, 'video_url': url, 'hits':hits, 'comment_num': comment_num, 'cid':CID})
        return {'nextPageToken':nextPageToken, 'prevPageToken':prevPageToken,  'data':resultArr}

    def put_contents(self, inputDict):
        #inputDict 는 딕셔너리의 어레이
        for video in inputDict:
            content = Database.Content(video['cid'], video['video_url'], video['video_name'], video['thumbnail'], video['hits'], video['comment_num'])
            Database.insert_content(content)
            Database.create_raw_comment_table(content.recognize)
            

    def get_comment_and_likes(self, recognize, video_id):
        def remove_a_tag(string):
            string = re.sub(r'<[^>]*>', '', string) 
            string = string.replace('&quot;','"')
            string = string.replace('&amp;','&')
            string = string.replace('&#39;','\'')
            if 'a href' in string:
                string = string.replace('</a>','')
                string = string.replace(string[string.index('<a'):string.index('">')+2],'')
            return string

        res = Database.get_last_page(recognize)
        cont = res[0].get('last_page')
        api_obj = self.api_obj
        data = []
        if cont:
            response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, pageToken=cont, maxResults=100).execute()
            Database.update_last_page_null(recognize)
        else:
            response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, maxResults=100).execute()
        try:
            while response:
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    etag = item['snippet']['topLevelComment']['etag']
                    if etag:
                        data.append([etag, remove_a_tag(comment['textDisplay']), comment.get('likeCount','0')])
                    else:
                        print(item)
            
                    if item['snippet']['totalReplyCount'] > 0:
                        try:
                            for reply_item in item['replies']['comments']:
                                reply = reply_item['snippet']
                                etag = reply_item.get('etag')
                                data.append([etag, remove_a_tag(reply['textDisplay']), reply.get('likeCount','0')])
                        except:
                            pass

                    if len(data)>18000:
                        Database.insert_raw_comment(recognize, data)
                        data = []
            
                if 'nextPageToken' in response:
                    pageToken =  response['nextPageToken']
                    response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, pageToken=response['nextPageToken'], maxResults=100).execute()
                else:
                    response = ''
            if data:
                Database.insert_raw_comment(recognize, data)

            Database.update_state_done(recognize)

        except:
            Database.update_last_page(recognize, pageToken)
            if data:
                Database.insert_raw_comment(recognize, data)
            Database.update_state_request(recognize)

 
if __name__=="__main__":
    # api_key = 'AIzaSyCEwR4BXNL_ZxJgy6JTBcu2_wYuwS3RnDo'    
    api_key = 'AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A'     ## 발급받은 api 키
    video_id = 'kLUAqWu3YzU'                                ## 동영상 id watch?v= 다음
    api = youtubeAPI(api_key)
    api.get_comment_and_likes()
    returnvalue = api.get_comment_and_likes(video_id)
