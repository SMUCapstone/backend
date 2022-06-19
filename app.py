from flask import Flask, request
from flask_cors import CORS
import DB_Test as db
import requests
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

@app.route('/')
def hello_pybo():
    return 'Hello, Pybo!'

@app.route('/youtubers')
def test_youtuber():
    data = db.testYoutuber()
    print(data)
    print(type(data.id[0]))
    return {'id':data.id[0], 'channel':data.channel[0], 'profile':data.profile[0] }

@app.route('/channels')
def test_search():
    all_args = request.args.to_dict()
    query = all_args.get('q','')
    maxResults = all_args.get('maxResults','10')
    url = 'https://www.googleapis.com/youtube/v3/search'
    
    payload = {'q':query,'maxResults':maxResults if maxResults else '10', 'key':'AIzaSyBug-zl91U0prwpaI2LgBIg_UHQrv5DP8A','part':'snippet', 'type':'channel' }
    result = json.loads(requests.get(url, params=payload).text)['items']
    print(result)
    result = [{'channelId':item['snippet']['channelId'], 'Channelname':item['snippet']['channelTitle'], 'thumbnail':item['snippet']['thumbnails']['high']['url']} for item in result]
    print(result)
    return {'items':result}

app.run(host='0.0.0.0', debug=True)
