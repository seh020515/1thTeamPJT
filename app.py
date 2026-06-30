from flask import (Flask, render_template, Response, jsonify)
import json
import requests
import cv2
import time

app = Flask(__name__)

last_frame_time = time.time()
is_camera_connected = True

ESP32_CAM_URL = 'http://192.168.137.145:81/stream'

@app.route('/')
def index():
    return render_template('index.html')

camera = cv2.VideoCapture('http://192.168.137.145:81/stream?type=some.mjpeg', cv2.CAP_FFMPEG)
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

def generate_frames():
    global last_frame_time, is_camera_connected

    while True:
        try:
            res = requests.get(ESP32_CAM_URL, stream=True, timeout=5)

            if res.status_code == 200:
                bytes_data = b''

                for chunk in res.iter_content(chunk_size=1024):
                    bytes_data += chunk

                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')

                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]

                        last_frame_time = time.time()
                        is_camera_connected = True

                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n')
                        
            else:
                raise Exception("카메라 응답 없음")
            
        except Exception as e:
            time.sleep(0.1)
            if time.time() - last_frame_time >= 3.0:
                is_camera_connected = False
            continue

    
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera_status')
def camera_status():
    global is_camera_connected
    return jsonify({'connected': is_camera_connected})

@app.route('/get_logs')
def get_logs():
    with open('db/data.json', 'r', encoding='utf-8') as f:
        logs_data = json.load(f)
    return jsonify(logs_data)

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = 5000,
        debug = True
    )



