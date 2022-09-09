from flask import Flask, request
from flask_cors import CORS
import Database as db
from youtubeAPI import youtubeAPI
import requests
import json
import pika
from comment_analyze import *  
import random

class Publisher:
    def __init__(self):
        self.__url = '34.64.56.32'
        self.__port = 5672
        self.__vhost = 'youthat'
        self.__cred = pika.PlainCredentials('admin', 'capstoneVPC')
        self.__queue = 'pre-collect'

    def publish(self, body):
        conn = pika.BlockingConnection(pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
        chan = conn.channel()
        chan.basic_publish(
            exchange = '',
            routing_key = self.__queue,
            body = body
        )
        conn.close()
        return

publisher = Publisher()
# yt = youtubeAPI('AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A')
yt = youtubeAPI('AIzaSyCEwR4BXNL_ZxJgy6JTBcu2_wYuwS3RnDo')
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def hello():
    return 'Hello, world!'

@app.route('/youtubers',methods=['GET', 'POST', 'DELETE'])
def youtuber():
    if request.method =='GET':
        data = db.getYoutuber()
        result = []
        for i in range(len(data.id)):
            result.append({'id':data.id[i], 'channel':data.channel[i], 'profile':data.profile[i]})
        return {'result': result}
    elif request.method == 'POST':
        channelId = request.get_json().get('id','')
        if channelId:
            yt.get_youtuber(channelId)
            return {"response":"save success!"}
        else:
            return {"response":"invalid input type"}
    elif request.method == 'DELETE':
        channelId = request.get_json().get('id','')
        if channelId:
            db.delYoutuber(channelId)
            return {"response":"delete success!"}
        else:
            return {"response":"invalid input type"}


@app.route('/channels')
def search():
    all_args = request.args.to_dict()
    query = all_args.get('q','')
    maxResults = all_args.get('maxResults','10')
    url = 'https://www.googleapis.com/youtube/v3/search'
    payload = {'q':query,'maxResults':maxResults if maxResults else '10', 'key':'AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A','part':'snippet', 'type':'channel' }
    is_cached = db.search_db_cache(json.dumps(payload).replace('\\','\\\\'))
    if is_cached:
        return json.loads(is_cached)
    payload = {'q':query,'maxResults':maxResults if maxResults else '10', 'key':yt.api_key,'part':'snippet', 'type':'channel' }
    result = json.loads(requests.get(url, params=payload).text)['items']
    result = [{'channelId':item['snippet']['channelId'], 'channelname':item['snippet']['channelTitle'], 'thumbnail':item['snippet']['thumbnails']['high']['url']} for item in result]
    payload['key']='AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A'
    db.insert_db_cache(json.dumps(payload),json.dumps({'items':result}))
    return {'items':result}


@app.route('/contents',methods=['GET', 'POST', 'DELETE'])
def contents():
    if request.method =='GET':
        all_args = request.args.to_dict()
        fromDB = all_args.get('fromDB','')
        channelId = all_args.get('channelId','')
        pageToken = all_args.get('pageToken','')
        if not channelId:
            return ''

        # if fromDB:
        #     data = db.getContent(channelId)
        #     result = []
        #     for i in range(len(data.id)):
        #         result.append({'id':data.id[i], 'url':data.url[i], 'recognize':data.recognize[i], 'video_name':data.video_name[i], 'thumbnail':data.thumbnail[i], 'hits':str(data.hits[i]), 'comment_num':str(data.comment_num[i]), 'state':str(data.state[i]), 'pageToken':data.last_page[i] })
        #     return {'data': result}

        # payload = {'channelId':channelId, 'pageToken':pageToken}
        # is_cached = db.search_db_cache(json.dumps(payload))
        # if is_cached:
        #     return json.loads(is_cached)
        if pageToken:
            result = yt.get_contents(channelId, pageToken)
        else:
            result = yt.get_contents(channelId)
            db.searched_channel(channelId)
        # db.insert_db_cache(json.dumps(payload), json.dumps(result))
        return result


    elif request.method == 'POST':
        contArr = request.get_json().get('contArr','')
        if contArr:
            yt.put_contents(contArr)
            return {"response":"save success!"}
        else:
            return {"response":"invalid input type"}

@app.route('/scrape',methods=['GET'])
def scrape():
    if request.method =='GET':
        all_args = request.args.to_dict()
        recognize = all_args.get('recognize','')
        if not recognize:
            return ''
        db.update_state_request(recognize)
        publisher.publish(recognize)
        return 'success'

@app.route('/analyze',methods=['GET'])
def analyze():
    all_args = request.args.to_dict()
    video_id = all_args.get('videoId','')
    comments = [x[1] for x in yt.get_comment_and_likes_3000(video_id)]
    # db에서 추천 비디오 랜덤 추출
    conn = db.get_connection()
    curs = conn.cursor(db.pymysql.cursors.DictCursor)
    sql  = "select recognize from searched_video"
    curs.execute(sql)
    all_video_ids = [x['recognize'] for x in curs.fetchall()]
    random.seed(video_id)
    random.shuffle(all_video_ids)
    recommend_id1 = all_video_ids[0]
    recommend_id2 = all_video_ids[1]
    if not comments:
        return 
    # payload = {'type':'analyze','videoId':video_id}
    # is_cached = db.search_db_cache(json.dumps(payload))
    # if is_cached:
    #     return json.loads(is_cached)
    # else:
    result = {
        'thumbnail':{
            'url':f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg'
        },
        'recommend':[
            {
                'thumb':f'https://i.ytimg.com/vi/{recommend_id1}/hqdefault.jpg',
                'url':f'https://www.youtube.com/watch?v={recommend_id1}'
            },
            {
                'thumb':f'https://i.ytimg.com/vi/{recommend_id2}/hqdefault.jpg',
                'url':f'https://www.youtube.com/watch?v={recommend_id2}'
            }
        ],
        'sentimental':{
            'pos':88,
            'neg':12
        },
        'bigdata':{
            'image':'https://lh3.googleusercontent.com/fife/AAbDypD5uowlKKYO1FnE85SLeyZOc9j6RE1ymyhOUsd8mDyQ3spHFp9kuMyB8XDEBCtewhKC7aewDgaH4WG7hTCvN0wh3zqEppfjyujHVEF8vVk2GdMJt5qgSd9D3qAQz2THhIzL5umSxmz_JXGzm-V1vjDPGb8YZ4OnADTxaxY8d52XhUwDT5f5t9sDVmT0T81Kw2Bpz3hRgTtFBKbJgEtF14PtKd2r49S6UmcwR2gInqNUq0PnKlX7TycmjOqTAo8rGVj8R1aLR9J5V8iMlFLpWaVdd3XJdplcXAJiXTUc0JoQD8g2DVGlelYIl0qxExjnMGl9yMSg1sq1veeH5jqHlbwb5H-ni-_42tRZVaeaEimnOS41L4JxOeYE0xdt-uDvCu-eo4atoTe92w9DtuVQ0KEBZFEsMaimNit-MNUGyxOKMWFiiuCkUlH2dvXZt7LIcWSwYhrhMG1FHEUp_28RqRfqs6x-KhlX0Z0XC45rlmxHc1pL1MBScjJCSpIHn_P8sV6iHghQ1cwKU85eI-GLTb3lmBPG7eiLU04CJXEUGJGLt9OxwiHg51-17kquNelIoU8zo1N5XYCuHJ_UimgKQgFbN6RpT_HJhCDP1NttgSTC3bYTLcbLwDdq-2sIOuILikQCd0Vau998o_puLzlflgUT-MPs0dvbBCbesyrkhNG46VvjalctM2TNCwo7RpR53X73tW4ziGnNnSccc2JKcJC_e3Ye5XfV2aQQPduyywEFsQhzL0dcp_oNm-GnHO0Ljs1PYhDaH_w4e94CjHGth20sZbBzkyUcOj2_oABDeysMpiODVxbYV1Y7gZGZvIp_PKyMEyXmRRjZ_Hyr4YcdepKhqaoJAvETAG7qYi4MtbuRzpHlk0uLSZwoD3fbUIl77m-jjpLI2aNgZo94pjOzengyM4Cg4U3VvUXWRwYC438wIm_GTsINzRR9d-mjQp2zSZvrOYdWPgNcxlocMHS_tW9IadLWNG2HOnqNUdAbtmFJ4d9HhTBoYxaWtXDYV6Yge2U6Y8G1PusDlrvqz0ciUKcyWFpIl2WLdRA6JreG3K_4HzEgBq5ITaMGQolOWaBSqDPiIv-gFu4jGheZzphrTC3juLuCzJXjxkxKXhvM7Dtnz4x47po1DLAFTSnOT6Jehavh9GjfwWKhYs0uolFYSogx7_xBN4GKg9FpOji5zvK4JiNi5caEFJ8EuhtVEc1J37CMlWdjoSZ5Cwt8CBsNTJvcLyMt36xc5Fuz25lCy1D6ekgVwAikXUAwktXejaLdx9USSKuZr50nCxJAzxayMcH3VI7QmoFFi09TBjgIcuw=w1875-h895',
            'comments':make_wordcloud(comments, video_id)
        },
        'timestamp':find_timestamp(comments)
    }
    # db.insert_db_cache(json.dumps(payload), json.dumps(result))
    db.searched_video(video_id)
    return result

@app.route('/popular',methods=['GET'])
def popular():
    # DB에서 channelId와 videoId를 꺼내온다
    channel_id = db.most_searched_channel()
    video_id = db.most_searched_video()
    url = f'https://www.googleapis.com/youtube/v3/channels?id={channel_id}&part=snippet&part=statistics&key={yt.api_key}'
    chn_response = json.loads(requests.get(url).text)['items'][0]
    channel_name = chn_response['snippet']['title']
    profile_img = chn_response['snippet']['thumbnails']['high']['url']
    subscribers = chn_response['statistics'].get('subscriberCount','0')

    vid_response = yt.api_obj.videos().list(part='statistics, snippet', id=video_id).execute()
    hits =  vid_response['items'][0]['statistics'].get('viewCount','0')
    comment_num =  vid_response['items'][0]['statistics'].get('commentCount','0')
    cid = vid_response['items'][0]['snippet'].get('channelId','0')
    video_name = vid_response['items'][0]['snippet'].get('title','0')
    result = {
        'channel':{
            'channelId': channel_id,
            'channelName': channel_name,
            'thumbnail': profile_img,
            'channelHits': subscribers #혹시 채널 조회수도 얻을 수 있을까요?? 힘드시면 빼도 될 것 같아요
        }, #많이 분석한 채널 객체
        'video':{
            'cid': cid,
            'comment_num': comment_num,
            'hits': hits,
            'id': video_id,
            'thumbnail': f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg',
            'video_name' : video_name,
            'video_url': f'www.youtube.com/watch?={video_id}'
        }
    }
    return result

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)
