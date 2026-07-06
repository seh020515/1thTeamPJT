import urllib.request
import time, cv2, os, json
import numpy as np
from datetime import datetime
from ultralytics import YOLO

class DroneManager:
    def __init__(self):
        self.url = 'http://192.168.137.63:81/stream'
        self.model = YOLO('yolov8n.pt')
        self.is_connected = True
        self.LOG_FILE_PATH = 'db/detection_logs.json'
        
        self.system_settings = {
            "danger_detection": "ON",
            "alert_mode": "ALL"
        }
        self.is_danger = False
        self.was_danger = False
        self.last_frame_time = time.time()

    def write_danger_log(self):
        if self.system_settings.get("alert_mode") == "MUTE":
            print(" [DroneManager] 알림 모드가 '무음(MUTE)'이므로 로그를 기록하지 않습니다.")
            return

        try:
            os.makedirs(os.path.dirname(self.LOG_FILE_PATH), exist_ok=True)
            logs_data = []
            if os.path.exists(self.LOG_FILE_PATH):
                with open(self.LOG_FILE_PATH, 'r', encoding='utf-8') as f:
                    try:
                        logs_data = json.load(f)
                    except json.JSONDecodeError:
                        logs_data = []

            new_log = {
                "id": int(time.time() * 1000),
                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "type": "intrusion",
                "type_name": "위험구역 침입",
                "location": "제 1구역 (해수욕장 우측)",
                "status": "미조치"
            }
            logs_data.insert(0, new_log)


            with open(self.LOG_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(logs_data, f, indent=4, ensure_ascii=False)
            print("🚨 위험 구역 침입 로그 저장 완료!")
        except Exception as e:
            print(f"로그 저장 에러: {e}")

    def generate_frames(self):
        while True:
            try:
                time.sleep(0.04)
                req = urllib.request.Request(self.url, headers={'User-Agent': 'Mozilla/5.0'})
                
                with urllib.request.urlopen(req, timeout=4) as stream:
                    bytes_data = b''
                    while True:
                        chunk = stream.read(4096)
                        if not chunk:
                            break
                        bytes_data += chunk

                        a = bytes_data.find(b'\xff\xd8')
                        b = bytes_data.find(b'\xff\xd9')

                        if a != -1 and b != -1 and a < b:
                            jpg_bytes = bytes_data[a:b+2]
                            bytes_data = bytes_data[b+2:]

                            np_arr = np.frombuffer(jpg_bytes, dtype=np.uint8)
                            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                            if frame is not None:
                                h, w, _ = frame.shape
                                zone_x1, zone_y1 = int(w * 0.2), int(h * 0.2)
                                zone_x2, zone_y2 = int(w * 0.8), int(h * 0.8)

                                current_danger_state = False

                                if self.system_settings.get('danger_detection', 'ON') == 'ON':
                                    results = self.model(frame, stream=True, verbose=False)
                                    for r in results:
                                        boxes = r.boxes
                                        for box in boxes:
                                            cls = int(box.cls[0])
                                            if cls == 0:
                                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                                conf = float(box.conf[0]) * 100
                                                
                                                person_foot_x = int((x1 + x2) / 2)
                                                person_foot_y = y2

                                                if (zone_x1 <= person_foot_x <= zone_x2) and (zone_y1 <= person_foot_y <= zone_y2):
                                                    current_danger_state = True
                                                    box_color = (0, 0, 255)
                                                    label = f"WARNING: {conf:.1f}%"
                                                else:
                                                    box_color = (0, 255, 255)
                                                    label = f"Swimmer: {conf:.1f}%"

                                                cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
                                                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)

                                    self.is_danger = current_danger_state
                                    if self.is_danger and not self.was_danger:
                                        self.write_danger_log()
                                    self.was_danger = self.is_danger

                                    zone_color = (0, 0, 255) if self.is_danger else (0, 255, 0)
                                    zone_title = "RESTRICTED ENTRY" if self.is_danger else "SAFETY LINE (CLEAR)"
                                    cv2.rectangle(frame, (zone_x1, zone_y1), (zone_x2, zone_y2), zone_color, 3 if self.is_danger else 2)
                                    cv2.putText(frame, zone_title, (zone_x1, zone_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, zone_color, 2)
                                else:
                                    self.is_danger = False
                                    self.was_danger = False

                                ret, encoded_buffer = cv2.imencode('.jpg', frame)
                                if ret:
                                    jpg = encoded_buffer.tobytes()
                                    self.last_frame_time = time.time()
                                    self.is_connected = True

                                    yield (b'--frame\r\n'
                                           b'Content-Type: image/jpeg\r\n'
                                           b'Content-Length: ' + str(len(jpg)).encode() + b'\r\n\r\n' + jpg + b'\r\n')
                            else:
                                continue
            except Exception as e:
                print(f'카메라 통신 에러 로그: {e}')
                time.sleep(0.5)
                if time.time() - self.last_frame_time >= 3.0:
                    self.is_connected = False
                continue