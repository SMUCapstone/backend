from youtubeAPI import youtubeAPI
import Database as db
import time
import requests
import json

yt = youtubeAPI('AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A')
url = 'http://34.64.56.32:5000/jobs'

while True:
    res = json.loads(requests.get(url).text).get('result')
    if res==-1:
        pass
        # print("message received 0")
    else:
        recognize, url = res
        print("message received 1", url)
        video_id = url.split('watch?v=')[-1]
        yt.get_comment_and_likes(recognize, video_id)

    time.sleep(1)