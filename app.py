from flask import (Flask, render_template, Response)
import cv2
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

# camera = cv2.VideoCapture('sample.mp4')
camera = cv2.VideoCapture("https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4")

def generate_frames():
    while True:
        time.sleep(0.03)
        success, frame = camera.read()
        if not success:
            camera.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = 5000,
        debug = True
    )



