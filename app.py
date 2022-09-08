from flask import Flask, request
from flask_cors import CORS
import Database as db
from youtubeAPI import youtubeAPI
import requests
import json
import pika

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

        if fromDB:
            data = db.getContent(channelId)
            result = []
            for i in range(len(data.id)):
                result.append({'id':data.id[i], 'url':data.url[i], 'recognize':data.recognize[i], 'video_name':data.video_name[i], 'thumbnail':data.thumbnail[i], 'hits':str(data.hits[i]), 'comment_num':str(data.comment_num[i]), 'state':str(data.state[i]), 'pageToken':data.last_page[i] })
            return {'data': result}

        payload = {'channelId':channelId, 'pageToken':pageToken}
        is_cached = db.search_db_cache(json.dumps(payload))
        if is_cached:
            return json.loads(is_cached)
        if pageToken:
            result = yt.get_contents(channelId, pageToken)
        else:
            result = yt.get_contents(channelId)
        db.insert_db_cache(json.dumps(payload), json.dumps(result))
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

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)
