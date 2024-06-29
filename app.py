import os
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    access_token = data.get('accessToken')
    url = f"https://graph.facebook.com/v20.0/me?access_token={access_token}"
    response = requests.get(url)
    if response.status_code == 200:
        return jsonify(success=True)
    else:
        return jsonify(success=False), 400

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return jsonify({"error": "No video part"}), 400
    video = request.files['video']
    title = request.form['title']
    description = request.form['description']
    access_token = request.form['accessToken']
    page_id = request.form['pageId']
    if video.filename == '':
        return jsonify({"error": "No selected file"}), 400

    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    video.save(video_path)

    url = f"https://graph-video.facebook.com/v20.0/{page_id}/videos"
    files = {
        'file': open(video_path, 'rb')
    }
    params = {
        'access_token': access_token,
        'title': title,
        'description': description
    }
    response = requests.post(url, files=files, params=params)
    os.remove(video_path)  # Xóa video sau khi tải lên

    return response.json()

if __name__ == '__main__':
    app.run(debug=True)
