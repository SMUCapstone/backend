import pandas
from googleapiclient.discovery import build
import time
 

def get_comment_and_likes(api_key, video_id):
    def remove_a_tag(string):
        string = string.replace('<br>','')
        string = string.replace('&quot;','"')
        if 'a href' in string:
            string = string.replace('</a>','')
            string = string.replace(string[string.index('<a'):string.index('">')+2],'')
        return string

    comments = list()
    api_obj = build('youtube', 'v3', developerKey=api_key)
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
                time.sleep(86400)
                now = time.localtime()
                print('할당량 초과로 쉬는 중 ', end=' ')
                print ("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
                response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, pageToken=response['nextPageToken'], maxResults=100).execute()
        else:
            return comments
 
if __name__=="__main__":
    api_key = 'AIzaSyCEwR4BXNL_ZxJgy6JTBcu2_wYuwS3RnDo'    ## 발급받은 api 키
    video_id = 'kLUAqWu3YzU'                                ## 동영상 id watch?v= 다음
    returnvalue = get_comment_and_likes(api_key, video_id)
