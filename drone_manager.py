import time            # 프레임 간격 조절 및 시간 측정을 위한 모듈
import cv2             # pyright: ignore[reportMissingImports] # 이미지 처리 및 AI 사각형 그리기 등을 위한 OpenCV 모듈
import os              # 로그 파일을 보관할 폴더(디렉토리) 자동 생성을 위한 모듈
import json            # 로그 데이터를 JSON 형식으로 읽고 쓰기 위한 모듈
from datetime import datetime  # 로그에 기록할 현재 날짜와 시간을 생성하는 모듈
from ultralytics import YOLO   # # pyright: ignore[reportMissingImports]  실시간 객체 인식을 위한 YOLO AI 모델 모듈

class DroneManager:
    def __init__(self):
        # 💡 ESP32-CAM 드론 카메라의 실시간 비디오 스트리밍 주소 설정
        self.url = 'http://192.168.137.44:81/stream'
        
        # 💡 YOLOv8 나노버전(가볍고 빠른 모델) AI 가중치 파일 로드
        self.model = YOLO('yolov8n.pt')
        
        # 💡 드론 카메라가 잘 켜져 있는지 확인하는 상태 변수
        self.is_connected = True
        
        # 💡 감지된 사고 위험 로그를 누적 저장할 데이터베이스 파일 경로
        self.LOG_FILE_PATH = 'db/data.json'
        
        # 💡 웹 설정 페이지와 실시간으로 동기화될 내부 옵션 저장 공간
        self.system_settings = {
            "danger_detection": "ON",  # 위험구역 AI 감지 기능 켜짐(ON)/꺼짐(OFF)
            "alert_mode": "ALL"        # 알림 모드 종류 (ALL: 전체, DANGER: 위험만, MUTE: 무음)
        }
        
        self.is_danger = False       # 현재 화면에 위험 상황(침입자)이 있는지 여부
        self.was_danger = False      # 직전 프레임에서 위험 상황이었는지 여부 (중복 로그 방지용)
        self.last_frame_time = time.time()  # 카메라가 살아있는지 체크하기 위한 마지막 프레임 수신 시간
        self.frame_count = 0

    def write_danger_log(self):
        """위험 구역에 사람이 진입했을 때 db/data.json 파일에 기록을 남기는 함수"""
        # 💡 [설정 연동] 만약 사용자가 웹 페이지에서 알림 설정을 '무음(MUTE)'으로 했다면 로그를 남기지 않고 즉시 탈출
        if self.system_settings.get("alert_mode") == "MUTE":
            print("🔕 [DroneManager] 알림 모드가 '무음(MUTE)'이므로 로그 저장을 스킵합니다.")
            return

        try:
            # logs 폴더나 db 폴더가 없을 경우 자동으로 하위 폴더 생성
            os.makedirs(os.path.dirname(self.LOG_FILE_PATH), exist_ok=True)
            
            logs_data = []
            # 기존에 저장된 로그 파일이 있다면 읽어와서 리스트에 담음
            if os.path.exists(self.LOG_FILE_PATH):
                with open(self.LOG_FILE_PATH, 'r', encoding='utf-8') as f:
                    try:
                        logs_data = json.load(f)
                    except json.JSONDecodeError:
                        logs_data = [] # 파일이 깨져있거나 비어있으면 초기화

            # 새로 추가할 위험 진입 데이터 양식 정의
            new_log = {
                "id": int(time.time() * 1000),  # 고유 식별자용 타임스탬프 밀리초 값
                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # 현재 시간 포맷팅
                "type": "위험진입",
                "location": "제 1구역 (해수욕장 우측)",
                "status": "미조치"  # 기본 조치 상태값
            }
            
            logs_data.append(new_log)  # 기존 로그 목록에 새 로그 붙여넣기
            
            # 갱신된 로그 리스트를 다시 파일에 깔끔하게 쓰기(정렬 및 한글 안깨지게 처리)
            with open(self.LOG_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(logs_data, f, indent=4, ensure_ascii=False)
            print("🚨 [DroneManager] 위험 구역 침입 로그 파일 저장 완료!")
            
        except Exception as e:
            print(f"로그 저장 에러: {e}")

    def generate_frames(self):
        """ESP32-CAM 영상을 받아 YOLO 분석 후 Flask 웹으로 실시간 전송"""

        # OpenCV 카메라 객체 (처음에는 연결 안 된 상태)
        cap = None

        while True:
            try:
                # ============================================================
                # 1. 카메라 연결 확인
                # ============================================================
                # cap 객체가 없거나 연결이 끊어진 경우 다시 연결 시도
                if cap is None or not cap.isOpened():

                    print("📡 ESP32-CAM 연결 시도...")

                    # ESP32-CAM의 MJPEG 스트림을 OpenCV로 연결
                    cap = cv2.VideoCapture(self.url)

                    # 연결 실패
                    if not cap.isOpened():
                        print("❌ ESP32-CAM 연결 실패")

                        self.is_connected = False

                        # 1초 후 다시 연결 시도
                        time.sleep(1)
                        continue

                    print("✅ ESP32-CAM 연결 성공")

                # ============================================================
                # 2. 프레임 읽기
                # ============================================================
                ret, frame = cap.read()

                # 프레임을 못 읽었으면 연결이 끊어진 것으로 판단
                if not ret or frame is None:

                    print("⚠️ 프레임 읽기 실패")

                    self.is_connected = False

                    cap.release()
                    cap = None

                    time.sleep(0.5)
                    continue

                # ============================================================
                # 3. 연결 상태 갱신
                # ============================================================
                self.is_connected = True
                self.last_frame_time = time.time()
                self.frame_count += 1

                # 영상 크기
                h, w, _ = frame.shape

                line_start = (0, int(h * 0.55))
                line_end = (w, int(h * 0.65))

                current_danger_state = False

                if self.system_settings.get("danger_detection") == "ON":

                    # 5프레임마다 한 번만 YOLO 수행
                    if self.frame_count % 5 == 0:
                        results = self.model(frame, imgsz=320, verbose=False)

                        
                        for r in results:
                            for box in r.boxes:
                                cls = int(box.cls[0])

                                if cls != 0:
                                    continue

                                x1, y1, x2, y2 = map(int, box.xyxy[0])

                                conf = float(box.conf[0]) * 100

                                # 사람 발 위치 계산
                                foot_x = (x1 + x2) // 2
                                foot_y = y2

                                line_y_at_x = line_start[1] + (line_end[1] - line_start[1]) * (foot_x - line_start[0]) / (line_end[0] - line_start[0])
                                
                                if foot_y > line_y_at_x:
                                    current_danger_state = True
                                    color = (0, 0, 255)
                                    label = f"WARNING {conf:.1f}%"

                                else:
                                    color = (0, 255, 255)
                                    label = f"Person {conf:.1f}%"

                                # 사람 박스 그리기
                                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                                cv2.putText(
                                    frame, label, (x1, y1 - 8),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA
                                )

                    # ========================================================
                    # 위험 여부 저장
                    # ========================================================
                    self.is_danger = current_danger_state

                    # 위험이 새롭게 발생했을 때만 로그 저장
                    if self.is_danger and not self.was_danger:
                        self.write_danger_log()

                    self.was_danger = self.is_danger

                    # ========================================================
                    # 위험구역 표시
                    # ========================================================
                    line_color = (0, 0, 255) if self.is_danger else (180, 230, 40)
                    cv2.line(frame, line_start, line_end, line_color, 2, cv2.LINE_AA)

                    cv2.putText(
                        frame, "RESTRICTED LINE", (20, line_start[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, line_color, 1, cv2.LINE_AA
                    )

                else:
                    # 위험 감지 OFF
                    self.is_danger = False
                    self.was_danger = False

                # ============================================================
                # 6. Flask 웹으로 JPEG 전송
                # ============================================================
                ret, buffer = cv2.imencode(".jpg", frame)
                if not ret:
                    continue

                jpg = buffer.tobytes()
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n'
                    + jpg +
                    b'\r\n'
                )

            # ================================================================
            # 예외 처리
            # ================================================================
            except Exception as e:
                print("❌ 카메라 오류 :", e)
                self.is_connected = False
                # 카메라 객체 해제
                if cap is not None:
                    cap.release()
                cap = None
                # 1초 후 자동 재연결
                time.sleep(1)