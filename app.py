from flask import Flask, request
from flask_cors import CORS
import DB_Test as db
from youtubeAPI import youtubeAPI
import requests
import json

yt = youtubeAPI('AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A')
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def hello_pybo():
    return 'Hello, Pybo!'

@app.route('/youtubers',methods=['GET', 'POST'])
def youtuber():
    if(request.method =='GET'):
        data = db.testYoutuber()
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


@app.route('/channels')
def search():
    all_args = request.args.to_dict()
    query = all_args.get('q','')
    maxResults = all_args.get('maxResults','10')
    url = 'https://www.googleapis.com/youtube/v3/search'
    'https://www.googleapis.com/youtube/v3/search?key=AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A&part=snippet&type=channel&q=백종원&maxResults=1'
    payload = {'q':query,'maxResults':maxResults if maxResults else '10', 'key':'AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A','part':'snippet', 'type':'channel' }
    result = json.loads(requests.get(url, params=payload).text)['items']
    print(result)
    result = [{'channelId':item['snippet']['channelId'], 'Channelname':item['snippet']['channelTitle'], 'thumbnail':item['snippet']['thumbnails']['high']['url']} for item in result]
    return {'items':result}

app.run(host='0.0.0.0', debug=True)
