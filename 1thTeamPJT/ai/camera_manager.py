import cv2
import threading

from datetime import datetime, timedelta

from ultralytics import YOLO

model = YOLO('yolov8n.pt')

model.train(
    data='data.yaml 경로',  # 예: 'C:/shark/data.yaml'
    epochs=50,
    imgsz=640,
    batch=8
)

from utils.json_manager import (
    load_intrusion_logs,
    save_intrusion_logs
)


camera = None
camera_lock = threading.Lock()

ESP32_STREAM_URL = "http://192.168.137.72:81/stream"

# YOLO 모델 로드
model = YOLO("yolov8n.pt")

last_intrusion_time = None


# 고정 위험구역 좌표
DANGER_X1 = 250
DANGER_Y1 = 100
DANGER_X2 = 550
DANGER_Y2 = 350


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

        "time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "message": "Person Intrusion in Danger Zone"

    })

    save_intrusion_logs(logs)

    print("person intrusion log saved")


def get_frame():

    global camera
    global last_intrusion_time

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

        # YOLO 객체 감지
        results = model(
            frame,
            verbose=False
        )

        result = results[0]

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            # COCO 기준 person 클래스 번호는 0
            if class_id != 0:
                continue

            # 신뢰도 낮은 결과 제거
            if confidence < 0.8:
                continue

            x1, y1, x2, y2 = box.xyxy[0]

            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            # 사람 박스 표시
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"person {confidence:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            # 중심점 표시
            cv2.circle(
                frame,
                (center_x, center_y),
                5,
                (255, 0, 0),
                -1
            )

            # 사람 중심점이 위험구역 안에 있는지 확인
            if (
                DANGER_X1 <= center_x <= DANGER_X2
                and
                DANGER_Y1 <= center_y <= DANGER_Y2
            ):
                is_intrusion = True

        danger_color = (0, 0, 255)

        if is_intrusion:
            danger_color = (0, 255, 255)

        # 위험구역 표시
        cv2.rectangle(
            frame,
            (DANGER_X1, DANGER_Y1),
            (DANGER_X2, DANGER_Y2),
            danger_color,
            3
        )

        cv2.putText(
            frame,
            "DANGER ZONE",
            (DANGER_X1, DANGER_Y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            danger_color,
            2
        )

        # 사람 침입 발생
        if is_intrusion:

            cv2.putText(
                frame,
                "PERSON INTRUSION",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                3
            )

            now = datetime.now()

            # 5초마다 한 번만 로그 저장
            if (
                last_intrusion_time is None
                or
                now - last_intrusion_time >
                timedelta(seconds=5)
            ):

                save_intrusion_log()

                last_intrusion_time = now

        return frame

    except Exception as e:

        print("camera exception:", e)

        reconnect_camera()

        return None