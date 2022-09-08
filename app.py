from flask import Flask, request
from flask_cors import CORS
import Database as db
from youtubeAPI import youtubeAPI
import requests
import json
import pika
from comment_analyze import *  

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

@app.route('/related',methods=['GET'])
def related():
    all_args = request.args.to_dict()
    video_id = all_args.get('videoId','')
    payload = {'videoId':video_id}
    is_cached = db.search_db_cache(json.dumps(payload))
    if is_cached:
        return json.loads(is_cached)
    else:
        result = {'recommend':yt.get_related_video(video_id)}
    db.insert_db_cache(json.dumps(payload), json.dumps(result))
    return result

@app.route('/analyze',methods=['GET'])
def analyze():
    all_args = request.args.to_dict()
    video_id = all_args.get('videoId','')
    payload = {'type':'analyze','videoId':video_id}
    # is_cached = db.search_db_cache(json.dumps(payload))
    # if is_cached:
    #     return json.loads(is_cached)
    # else:
    result = {
        'thumbnail':{
            'url':'https://i.ytimg.com/vi/ADRKCe5G5k4/hq720.jpg'
        },
        'recommend':[
            {
                'thumb':'https://i.ytimg.com/vi/riJJQOo9lV4/hqdefault.jpg',
                'url':'https://www.youtube.com/watch?v=riJJQOo9lV4'
            },
            {
                'thumb':'https://i.ytimg.com/vi/TCBB1U0mbhI/hqdefault.jpg',
                'url':'https://www.youtube.com/watch?v=TCBB1U0mbhI'
            }
        ],
        'sentimental':{
            'pos':88,
            'neg':12
        },
        'bigdata':{
            'image':'https://lh3.googleusercontent.com/fife/AAbDypD5uowlKKYO1FnE85SLeyZOc9j6RE1ymyhOUsd8mDyQ3spHFp9kuMyB8XDEBCtewhKC7aewDgaH4WG7hTCvN0wh3zqEppfjyujHVEF8vVk2GdMJt5qgSd9D3qAQz2THhIzL5umSxmz_JXGzm-V1vjDPGb8YZ4OnADTxaxY8d52XhUwDT5f5t9sDVmT0T81Kw2Bpz3hRgTtFBKbJgEtF14PtKd2r49S6UmcwR2gInqNUq0PnKlX7TycmjOqTAo8rGVj8R1aLR9J5V8iMlFLpWaVdd3XJdplcXAJiXTUc0JoQD8g2DVGlelYIl0qxExjnMGl9yMSg1sq1veeH5jqHlbwb5H-ni-_42tRZVaeaEimnOS41L4JxOeYE0xdt-uDvCu-eo4atoTe92w9DtuVQ0KEBZFEsMaimNit-MNUGyxOKMWFiiuCkUlH2dvXZt7LIcWSwYhrhMG1FHEUp_28RqRfqs6x-KhlX0Z0XC45rlmxHc1pL1MBScjJCSpIHn_P8sV6iHghQ1cwKU85eI-GLTb3lmBPG7eiLU04CJXEUGJGLt9OxwiHg51-17kquNelIoU8zo1N5XYCuHJ_UimgKQgFbN6RpT_HJhCDP1NttgSTC3bYTLcbLwDdq-2sIOuILikQCd0Vau998o_puLzlflgUT-MPs0dvbBCbesyrkhNG46VvjalctM2TNCwo7RpR53X73tW4ziGnNnSccc2JKcJC_e3Ye5XfV2aQQPduyywEFsQhzL0dcp_oNm-GnHO0Ljs1PYhDaH_w4e94CjHGth20sZbBzkyUcOj2_oABDeysMpiODVxbYV1Y7gZGZvIp_PKyMEyXmRRjZ_Hyr4YcdepKhqaoJAvETAG7qYi4MtbuRzpHlk0uLSZwoD3fbUIl77m-jjpLI2aNgZo94pjOzengyM4Cg4U3VvUXWRwYC438wIm_GTsINzRR9d-mjQp2zSZvrOYdWPgNcxlocMHS_tW9IadLWNG2HOnqNUdAbtmFJ4d9HhTBoYxaWtXDYV6Yge2U6Y8G1PusDlrvqz0ciUKcyWFpIl2WLdRA6JreG3K_4HzEgBq5ITaMGQolOWaBSqDPiIv-gFu4jGheZzphrTC3juLuCzJXjxkxKXhvM7Dtnz4x47po1DLAFTSnOT6Jehavh9GjfwWKhYs0uolFYSogx7_xBN4GKg9FpOji5zvK4JiNi5caEFJ8EuhtVEc1J37CMlWdjoSZ5Cwt8CBsNTJvcLyMt36xc5Fuz25lCy1D6ekgVwAikXUAwktXejaLdx9USSKuZr50nCxJAzxayMcH3VI7QmoFFi09TBjgIcuw=w1875-h895',
            'comments':{'진짜': 435, '영상': 384, '언니': 287, '오늘': 145, '사람': 145, '보고': 143, '정보': 134, '사랑': 131, '정말': 120, '생각': 112, '그냥': 101, '나영': 95, '추천': 93, '스타일': 91, '신발': 90, '얼굴': 89, '바지': 86, '실장': 84, '느낌': 83, '항상': 82, '패션': 79, '제품': 79, '한별': 79, '지금': 78, '어디': 72, 
'여자': 72, '댓글': 68, '브랜드': 67, '하나': 67, '머리': 63, '남자': 63, '요리': 61, '구매': 60, '요즘': 58, '가방': 57, '최고': 57, '가요': 53, '부츠': 52, '한번': 51, '코디': 50, '정도': 50, '모델': 49, '고민': 49, '처음': 48, '혹시': 48, '이번': 48, '명품': 48, '여기': 47, '운동': 47, '응원': 45, '사이즈': 45, '유행': 44, '역시': 44, '마지막': 44, '도움': 44, '겨울': 43, '때문': 43, '제일': 42, '몸매': 42, '엄마': 42, '뭔가': 42, '나이키': 42, '부분': 41, '형님': 41, '블랙': 40, '대박': 40, '아이유': 40, '설명': 39, '우리': 39, '완전': 39, '선생님': 39, '이준': 38, '컨텐츠': 38, '가격': 38, '구독': 37, '당신': 37, '다른': 37, '주우': 37, '시간': 36, '피부': 36, '이제': 35, '보기': 35, '니트': 35, '다리': 35, '여름': 34, '누나': 34, '원피스': 34, '사진': 34, '사고': 33, 
'아시': 33, '팬츠': 33, '유튜브': 33, '하루': 33, '기분': 32, '목소리': 32, '바로': 32, '계속': 32, '와이드': 32, '꿀팁': 32, '라인': 32
            }
        },
        'timestamp':[
            {
                '01:20':{
                    'freq':'123',
                    'comments':['1:20 댓글내용 1', '댓글내용 2 1:20', '댓글내용1:20 3']
                }
            },
            {
                '03:14':{
                    'freq':'109',
                    'comments':['3:14 댓글내용 1', '댓글내용 2 3:14', '댓글내용3:14 3']
                }
            }
        ]
    }
    # db.insert_db_cache(json.dumps(payload), json.dumps(result))
    return result

@app.route('/popular',methods=['GET'])
def popular():
    # DB에서 channelId와 videoId를 꺼내온다
    channel_id = ''
    video_id = '' 
    url = f'https://www.googleapis.com/youtube/v3/channels?id={channel_id}&part=snippet&part=statistics&key={yt.api_key}'
    # response = json.loads(requests.get(url).text)['items'][0]
    # channel_name = response['snippet']['title']
    # profile_img = response['snippet']['thumbnails']['high']['url']
    # subscribers = response['statistics'].get('subscriberCount','0')
    result = {
        'channel':{
            'channelId': 'UC3SyT4_WLHzN7JmHQwKQZww',
            'channelName': '이지금 [IU Official]',
            'thumbnail': 'https://yt3.ggpht.com/ytc/AMLnZu-UWvwHCKwBxSfbMOjy5D2z03jrZz4hnOWyksk1gw=s88-c-k-c0x00ffffff-no-rj-mo',
            'channelHits': '8050000' #혹시 채널 조회수도 얻을 수 있을까요?? 힘드시면 빼도 될 것 같아요
        }, #많이 분석한 채널 객체
        'video':{
            'cid': 'UC_gkwRB-p1JrOzzJk7PBKDQ',
            'comment_num': '2861',
            'hits': '6445799',
            'id': 'fmn7aswQUdQ',
            'thumbnail': 'https://i.ytimg.com/vi/fmn7aswQUdQ/hqdefault.jpg',
            'video_name' : '한국 여자 직장인 출근룩 국룰 #shorts #lookbook #룩북 #패션',
            'video_url': 'www.youtube.com/watch?=fmn7aswQUdQ'
        }
    }
    return result


if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)
