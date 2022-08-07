from youtubeAPI import youtubeAPI
import Database as db
import time

yt = youtubeAPI('AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A')

while True:
    res = db.search_request_state()
    if res==-1:
        print("message received 0")
    else:
        recognize, url = res
        print("message received 1", url)
        video_id = url.split('watch?v=')[-1]
        yt.get_comment_and_likes(recognize, video_id)

    time.sleep(1)