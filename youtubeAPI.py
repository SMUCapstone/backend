from multiprocessing.dummy import Array
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
            url = f'www.youtube.com/watch?={videoid}'
            hits =  response['items'][0]['statistics'].get('viewCount','0')
            comment_num =  response['items'][0]['statistics'].get('commentCount','0')
            resultArr.append({'id':videoid, 'video_name':title, 'thumbnail':thumbnail, 'video_url': url, 'hits':hits, 'comment_num': comment_num, 'cid':CID})
        return {'nextPageToken':nextPageToken, 'prevPageToken':prevPageToken,  'data':resultArr}

    def put_contents(self, inputDict):
        #inputDict 는 딕셔너리의 어레이
        for video in inputDict:
            content = Database.Content(video['cid'], video['video_url'], video['video_name'], video['thumbnail'], video['hits'], video['comment_num'])
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
                comments.append([remove_a_tag(comment['textDisplay']), comment.get('likeCount','0')])
        
                if item['snippet']['totalReplyCount'] > 0:
                    for reply_item in item['replies']['comments']:
                        reply = reply_item['snippet']
                        comments.append([remove_a_tag(reply['textDisplay']), reply.get('likeCount','0')])
        
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
