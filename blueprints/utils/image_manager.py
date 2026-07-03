import os                       #폴더 생성경로 조합용 모듈
from datetime import datetime   #현재 시간 가져오기 모듈

CAPTURE_DIR = "static/captures"     #이미지 저장 경로

def save_image(file, drone_id, location):       #이미지 저장함수(파일객체, 드론번호, 위치)

    drone_folder = os.path.join(CAPTURE_DIR, f"drone{drone_id}")    #드론별 하위폴더 경로
    os.makedirs(drone_folder, exist_ok=True)                        #폴더없으면 생성

    zone = "zone" + location.replace("구역", "")                #b구역 -> zoneb로 수정
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")     #현재시간 형태표시
    filename = f"drone{drone_id}_{zone}_{timestamp}.jpg"        #파일명 조합(드론번호,구역, 시간)
    filepath = os.path.join(drone_folder, filename)             #전체경로

    file.save(filepath)                     #실제파일 저장경로에 저장

    return filepath                     #저장된 전체경로 반환

# 테스트
if __name__ == "__main__":          #이 파일 직접실행시 코드동작
    class DummyFile:                #Flask없이 테스트하기 위한 가짜파일
        def save(self, path):       #실제 save() 매서드처럼 동작하도록 정의
            with open(path, "w") as f:      #지정 경로에 파일 열기(쓰기 모드)
                f.write("dummy image")      #내용 dummy image 문자열로 대체
    result = save_image(DummyFile(), drone_id=2, location="B구역")      #drone_id=드론번호, location="구역명"
    print(result)

    