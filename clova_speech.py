import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class ClovaSpeechClient:
    # Clova Speech invoke URL (앱 등록 시 발급받은 Invoke URL)
    invoke_url = 'https://clovaspeech-gw.ncloud.com/external/v1/9450/557708102ce267f8581b8e3855a37bb72d9246a419c6cb90a1eebe6fe97a2a33'
    # Clova Speech secret key (앱 등록 시 발급받은 Secret Key)
    secret = os.getenv("CLOVA_SECRET_KEY")

    def req_upload(self, file, completion, callback=None, userdata=None, forbiddens=None, boostings=None,
                   wordAlignment=True, fullText=True, diarization=None, sed=None):

        # 키워드 부스팅을 위한 형식
        if boostings is None:
            boostings = [{'words': '밝기값'}, {'words': '조영제'}, {'words': '비강체'}, {'words': '강체'}, {'words': '오차'},
                         {'words': '아티팩트'}, {'words': '보간'}, {'words': 'voxel'}, {'words': 'mm'}, {'words': '유클리디안'},
                         {'words': '정합'}, {'words': '듀얼'}, {'words': 'translation'}, {'words': '기저'}, {'words': '미분'}]

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
        print(json.dumps(request_body, ensure_ascii=False).encode('UTF-8'))
        files = {
            'media': open(file, 'rb'),
            'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
        }
        response = requests.post(headers=headers, url=self.invoke_url + '/recognizer/upload', files=files)
        return response

if __name__ == '__main__':
    res = ClovaSpeechClient().req_upload(file='./Data/test_1.m4a', completion='sync')
    result = res.json()

    segments = result.get('segments', [])
    timeline_segments = []

    for segment in segments:
        timeline_label = segment['start']
        text = segment['text']
        timeline_segments.append({'timeline': timeline_label, 'text': text})

    for timeline_segment in timeline_segments:
        # 초 단위를 시, 분, 초로 변환
        total_seconds = int(timeline_segment['timeline'] * 0.001)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        text = timeline_segment['text']

        # 시, 분, 초 형식으로 출력
        print(f'{hours:02}:{minutes:02}:{seconds:02} - {text}')

    # 음성 파일 총 시간 second 단위로 출력
    if segments:
        total_time_ms = segments[-1]['end'] # 마지막 세그먼트의 끝 시간
        total_time_sec = int(total_time_ms * 0.001)
        print(f"\nTotal Duration Time: {total_time_sec} second")
    else:
        print("No segments found. Unable to calculate total duration.")
