from flask import Flask, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)


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

    def req_upload(self, file_path, completion):
        headers = {
            'Accept': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }

        request_body = {
            'language': 'enko',
            'completion': completion
        }

        with open(file_path, 'rb') as file:
            files = {
                'media': file,
                'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
            }
            response = requests.post(headers=headers, url=self.invoke_url + '/recognizer/upload', files=files)

        return response


def change_to_custom_json(segments, total_duration_ms):
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    note_manager = NoteManager()
    note_id = note_manager.get_next_note_id()

    script = []
    speakers = {}

    for segment in segments:
        start_time = format_time(segment['start'])
        text = segment['text']

        speaker_info = segment.get('speaker', None)
        if isinstance(speaker_info, dict):
            speaker_name = speaker_info.get('name', "Unknown")
        elif isinstance(speaker_info, str):
            speaker_name = speaker_info
        else:
            speaker_name = "Unknown"

        if speaker_name not in speakers:
            speakers[speaker_name] = f"Speaker {len(speakers) + 1}"

        script.append({
            "text": text,
            "speaker": speakers[speaker_name],
            "timestamp": start_time
        })

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

    return data


def format_time(milliseconds):
    total_seconds = int(milliseconds * 0.001)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


@app.route('/scripts', methods=['POST'])
def process_audio():
    # JSON 파일 경로 설정
    file_dir = os.getenv("VOLUME_PATH")
    json_file_path = file_dir + '/example.json'

    try:
        # 파일을 열고 JSON 데이터 읽기
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)  # 파일에서 JSON 데이터를 로드

        # JSON 데이터를 응답으로 반환
        return jsonify(data)

    except FileNotFoundError:
        # 파일을 찾을 수 없는 경우 오류 메시지 반환
        return jsonify({"error": "File not found"}), 404

    except json.JSONDecodeError:
        # 파일이 잘못된 JSON 형식일 경우 오류 메시지 반환
        return jsonify({"error": "Invalid JSON format"}), 400

    #
    # data = request.get_json()
    # file_path = data.get('file_path')
    # completion = data.get('completion', 'sync')
    #
    # if not file_path:
    #     return jsonify({'error': 'file_path is required'}), 400
    #
    # client = ClovaSpeechClient()
    # response = client.req_upload(file_path, completion)
    #
    # if response.status_code != 200:
    #     return jsonify({'error': 'Failed to get response from Clova API'}), 500
    #
    # result = response.json()
    # segments = result.get('segments', [])
    #
    # if not segments:
    #     return jsonify({'error': 'No segments found in the response'}), 400
    #
    # total_duration_ms = segments[-1]['end']
    # custom_json = change_to_custom_json(segments, total_duration_ms)
    #
    # return jsonify(custom_json)

# 엔드포인트 정의: /get-json
@app.route('/get-json', methods=['GET'])
def get_json():
    # JSON 파일 경로 설정
    file_dir = os.getenv("VOLUME_PATH")
    json_file_path = file_dir + '/example.json'

    try:
        # 파일을 열고 JSON 데이터 읽기
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)  # 파일에서 JSON 데이터를 로드

        # JSON 데이터를 응답으로 반환
        return jsonify(data)

    except FileNotFoundError:
        # 파일을 찾을 수 없는 경우 오류 메시지 반환
        return jsonify({"error": "File not found"}), 404

    except json.JSONDecodeError:
        # 파일이 잘못된 JSON 형식일 경우 오류 메시지 반환
        return jsonify({"error": "Invalid JSON format"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
