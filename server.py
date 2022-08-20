from youtubeAPI import youtubeAPI
import Database as db
import time
import requests
import json

yt = youtubeAPI('AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A')
url = 'http://34.64.56.32:5555/jobs'

while True:
    res = json.loads(requests.get(url).text).get('result')
    if res==-1:
        pass
        # print("message received 0")
    else:
        recognize, yt_url = res
        print("message received 1", yt_url)
        video_id = yt_url.split('watch?v=')[-1]
        yt.get_comment_and_likes(recognize, video_id)
        print('finished')

    time.sleep(1)