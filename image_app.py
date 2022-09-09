from flask import Flask, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

# HTTP POST방식으로 전송된 이미지를 저장
@app.route('/image', methods=['POST'])
def save_image():
    f = request.files['file']
    f.save('./saved/'+secure_filename(f.filename))
    return 'done!'

if __name__=='__main__':
    app.run(port=3333, debug=True)