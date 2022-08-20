from flask import Flask
import Database as db

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/jobs')
def fifo():
    res = db.search_request_state()
    return {'result':res}

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True, threaded=False, port=5555)