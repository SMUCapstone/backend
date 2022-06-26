from flask import Flask, request
from flask_cors import CORS
import Database as db
from youtubeAPI import youtubeAPI
import requests
import json

yt = youtubeAPI('AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A')
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def hello():
    return 'Hello, world!'

@app.route('/youtubers',methods=['GET', 'POST', 'DELETE'])
def youtuber():
    if(request.method =='GET'):
        data = db.getYoutuber()
        result = []
        for i in range(len(data.id)):
            result.append({'id':data.id[i], 'channel':data.channel[i], 'profile':data.profile[i]})
        return {'result': result}
    elif(request.method == 'POST'):
        channelId = request.get_json().get('id','')
        if channelId:
            yt.get_youtuber(channelId)
            return {"response":"save success!"}
        else:
            return {"response":"invalid input type"}
    elif(request.method == 'DELETE'):
        channelId = request.get_json().get('id','')
        print(channelId)
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
    'https://www.googleapis.com/youtube/v3/search?key=AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A&part=snippet&type=channel&q=백종원&maxResults=1'
    payload = {'q':query,'maxResults':maxResults if maxResults else '10', 'key':'AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A','part':'snippet', 'type':'channel' }
    result = json.loads(requests.get(url, params=payload).text)['items']
    result = [{'channelId':item['snippet']['channelId'], 'Channelname':item['snippet']['channelTitle'], 'thumbnail':item['snippet']['thumbnails']['high']['url']} for item in result]
    return {'items':result}


@app.route('/contents')
def contents():
    all_args = request.args.to_dict()
    channelId = all_args.get('channelId','')
    pageToken = all_args.get('pageToken','')
    if not channelId:
        return ''
    if pageToken:
        result = yt.get_contents(channelId, pageToken)
    else:
        result = yt.get_contents(channelId)
    
    return result

app.run(host='0.0.0.0', debug=True)
