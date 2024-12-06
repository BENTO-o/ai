import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# 환경변수에서 clova speech key load
load_dotenv()


class NoteManager:
    def __init__(self):
        self.current_note_id = 0

    def get_next_note_id(self):
        self.current_note_id += 1
        return self.current_note_id


class ClovaSpeechClient:
    def __init__(self):
        self.invoke_url = os.getenv("CLOVA_INVOKE_URL")
        self.secret = os.getenv("CLOVA_SECRET_KEY")
        if not self.secret:
            raise ValueError("CLOVA_SECRET_KEY is not set in environment variables.")

    def req_upload(self, file_path, completion, callback=None, userdata=None, forbiddens=None, boostings=None,
                   wordAlignment=True, fullText=True, diarization=None, sed=None):
        """
        Clova Speech API 업로드 방식 요청
        """
        if boostings is None:
            boostings = [
                {'words': '밝기값'}, {'words': '조영제'}, {'words': '비강체'}, {'words': '강체'},
                {'words': '오차'}, {'words': '아티팩트'}, {'words': '보간'}, {'words': 'voxel'},
                {'words': 'mm'}, {'words': '유클리디안'}, {'words': '정합'}, {'words': '듀얼'},
                {'words': 'translation'}, {'words': '기저'}, {'words': '미분'}
            ]

        request_body = {
            'language': 'enko',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': diarization,
            'sed': sed,
        }

        headers = {
            'Accept': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }

        # 파일 업로드 및 파라미터 전달
        with open(file_path, 'rb') as file:
            files = {
                'media': file,
                'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
            }
            response = requests.post(headers=headers, url=self.invoke_url + '/recognizer/upload', files=files)

        return response


def change_to_custom_json(segments, total_duration_ms, output_json_path):
    """
    Clova Speech API 응답 데이터를 지정된 JSON 포맷으로 저장
    """

    # # note_id
    # global cur_note_id;
    # cur_note_id += 1;   # 노트 아이디 자동

    # createdAt: 노트 생성 시간 받아오기
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    note_manager = NoteManager()
    note_id = note_manager.get_next_note_id()

    script = []
    speakers = {}

    # 스크립트와 화자 정보 생성
    for segment in segments:
        start_time = format_time(segment['start'])
        text = segment['text']

        # speaker 필드 처리
        speaker_info = segment.get('speaker', None)
        if isinstance(speaker_info, dict):  # speaker가 dict일 경우
            speaker_name = speaker_info.get('name', "Unknown")  # name 필드 추출
        elif isinstance(speaker_info, str):  # speaker가 문자열일 경우
            speaker_name = speaker_info
        else:
            speaker_name = "Unknown"  # 예상치 못한 경우 기본값

        # 화자 정보 매핑
        if speaker_name not in speakers:
            speakers[speaker_name] = f"Speaker {len(speakers) + 1}"

        # JSON 포맷에 맞게 스크립트 추가
        script.append({
            "text": text,
            "speaker": speakers[speaker_name],
            "timestamp": start_time
        })

    # 전체 JSON 구조 생성
    data = {
        "noteId": note_id,
        "title": "title",
        "folder": "folder",
        "createdAt": created_at,
        "duration": format_time(total_duration_ms),
        "content": {
            "script": script,
            "speaker": list(speakers.values())
        }
    }

    # JSON 파일로 저장
    with open(output_json_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print(f"Custom JSON file saved at: {output_json_path}")


def format_time(milliseconds):
    """
    밀리초(ms)를 hh:mm:ss 형식으로 변환
    """
    total_seconds = int(milliseconds * 0.001)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


if __name__ == '__main__':
    # ClovaSpeechClient 초기화
    client = ClovaSpeechClient()

    # 테스트 오디오 파일 경로
    file_path = 'Data/example.m4a'
    output_json_path = 'Data/example.json'

    # Clova Speech API 호출
    response = client.req_upload(file_path=file_path, completion='sync')
    result = response.json()

    # API 응답에서 세그먼트 추출
    segments = result.get('segments', [])

    if segments:
        # 총 길이 계산
        total_duration_ms = segments[-1]['end']  # 마지막 세그먼트의 끝 시간

        # 커스텀 JSON으로 저장
        change_to_custom_json(segments, total_duration_ms, output_json_path)

        print(f"\nTotal Duration: {format_time(total_duration_ms)}")
    else:
        print("No segments found in the response.")


