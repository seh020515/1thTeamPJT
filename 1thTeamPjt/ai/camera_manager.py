import cv2
import sys
import os
import threading
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.json_manager import (
    load_intrusion_logs,
    save_intrusion_logs,
    load_danger_zone,
    save_danger_zone
)



from datetime import datetime, timedelta
from ultralytics import YOLO
from utils.json_manager import (
    load_intrusion_logs,
    save_intrusion_logs
)

# 위험구역 마우스 드래그 설정
drawing = False
drag_start = None
drag_end = None

def mouse_callback(event, x, y, flags, param):
    global drawing, drag_start, drag_end, DANGER_X1, DANGER_Y1, DANGER_X2, DANGER_Y2

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        drag_start = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            drag_end = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        drag_end = (x, y)
        DANGER_X1 = min(drag_start[0], drag_end[0])
        DANGER_Y1 = min(drag_start[1], drag_end[1])
        DANGER_X2 = max(drag_start[0], drag_end[0])
        DANGER_Y2 = max(drag_start[1], drag_end[1])
        save_danger_zone({"x1": DANGER_X1, "y1": DANGER_Y1, "x2": DANGER_X2, "y2": DANGER_Y2})
        print(f"위험구역 저장: {DANGER_X1}, {DANGER_Y1}, {DANGER_X2}, {DANGER_Y2}")

camera = cv2.VideoCapture(r'C:\seh\firstPjt\1thTeamPJT\1thTeamPjt\video\video.mp4')
camera_lock = threading.Lock()

ESP32_STREAM_URL = "http://192.168.137.72:81/stream"

model = YOLO("yolov8n.pt")
shark_model = YOLO(r'C:\seh\firstPjt\1thTeamPJT\1thTeamPjt\runs\detect\train-2\weights\best.pt')

last_intrusion_time = None
last_shark_time = None
last_crowd_time = None

zone = load_danger_zone()
DANGER_X1 = zone["x1"]
DANGER_Y1 = zone["y1"]
DANGER_X2 = zone["x2"]
DANGER_Y2 = zone["y2"]

CROWD_LIMIT = 20


def init_camera():
    global camera
    if camera is None:
        print("camera connecting...")
        camera = cv2.VideoCapture(ESP32_STREAM_URL)
        print("camera connected")


def reconnect_camera():
    global camera
    print("camera reconnecting...")
    try:
        if camera is not None:
            camera.release()
    except:
        pass
    camera = cv2.VideoCapture(ESP32_STREAM_URL)
    print("camera reconnected")


def save_intrusion_log():
    logs = load_intrusion_logs()
    logs.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": "Person Intrusion in Danger Zone"
    })
    save_intrusion_logs(logs)
    print("person intrusion log saved")


def save_shark_log():
    logs = load_intrusion_logs()
    logs.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": "Shark Detected"
    })
    save_intrusion_logs(logs)
    print("shark log saved")


def save_crowd_log(count):
    logs = load_intrusion_logs()
    logs.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": f"Crowd Warning: {count} people in Danger Zone"
    })
    save_intrusion_logs(logs)
    print("crowd log saved")


def get_frame():
    global camera, last_intrusion_time, last_shark_time, last_crowd_time

    if camera is None:
        return None

    try:
        if not camera.isOpened():
            reconnect_camera()
            return None

        with camera_lock:
            success, frame = camera.read()

        if not success:
            reconnect_camera()
            return None

        is_intrusion = False
        danger_count = 0

        # 사람 탐지
        results = model(frame, verbose=False)
        result = results[0]

        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            if class_id != 0:
                continue
            if confidence < 0.8:
                continue

            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"person {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.circle(frame, (center_x, center_y), 5, (255, 0, 0), -1)

            if (DANGER_X1 <= center_x <= DANGER_X2 and
                    DANGER_Y1 <= center_y <= DANGER_Y2):
                is_intrusion = True
                danger_count += 1

        # 위험구역 표시
        danger_color = (0, 255, 255) if is_intrusion else (0, 0, 255)
        cv2.rectangle(frame, (DANGER_X1, DANGER_Y1), (DANGER_X2, DANGER_Y2), danger_color, 3)
        cv2.putText(frame, "DANGER ZONE", (DANGER_X1, DANGER_Y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, danger_color, 2)

        if is_intrusion:
            cv2.putText(frame, "PERSON INTRUSION", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            now = datetime.now()
            if (last_intrusion_time is None or
                    now - last_intrusion_time > timedelta(seconds=5)):
                save_intrusion_log()
                last_intrusion_time = now

        # 인파 과밀집 경고
        if danger_count >= CROWD_LIMIT:
            cv2.putText(frame, f"CROWD WARNING: {danger_count} people",
                        (30, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
            now = datetime.now()
            if (last_crowd_time is None or
                    now - last_crowd_time > timedelta(seconds=5)):
                save_crowd_log(danger_count)
                last_crowd_time = now

        # 상어 탐지
        shark_results = shark_model(frame, verbose=False)
        shark_result = shark_results[0]

        for box in shark_result.boxes:
            confidence = float(box.conf[0])
            if confidence < 0.8:
                continue

            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, f"SHARK {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "SHARK DETECTED", (30, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            now = datetime.now()
            if (last_shark_time is None or
                    now - last_shark_time > timedelta(seconds=5)):
                save_shark_log()
                last_shark_time = now

        return frame

    except Exception as e:
        print("camera exception:", e)
        reconnect_camera()
        return None


if __name__ == '__main__':
    init_camera()
    cv2.namedWindow('Detection')
    cv2.setMouseCallback('Detection', mouse_callback)
    while True:
        frame = get_frame()
        if frame is not None:
            # 드래그 중일 때 임시 박스 표시
            if drawing and drag_start and drag_end:
                cv2.rectangle(frame, drag_start, drag_end, (255, 255, 0), 2)
            cv2.imshow('Detection', frame)
        if cv2.waitKey(1) == ord('q'):
            break
    cv2.destroyAllWindows()