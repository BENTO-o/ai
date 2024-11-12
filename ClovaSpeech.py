import requests
import json

class ClovaSpeechClient:
    # Clova Speech invoke URL (앱 등록 시 발급받은 Invoke URL)
    invoke_url = 'https://clovaspeech-gw.ncloud.com/external/v1/9450/557708102ce267f8581b8e3855a37bb72d9246a419c6cb90a1eebe6fe97a2a33'
    # Clova Speech secret key (앱 등록 시 발급받은 Secret Key)
    secret = 'fa6d851268854b6c84df056c72de52b4'

    # def req_url(self, url, completion, callback=None, userdata=None, forbiddens=None, boostings=None, wordAlignment=True, fullText=True, diarization=None, sed=None):
    #     request_body = {
    #         'url': url,
    #         'language': 'enko',
    #         'completion': completion,
    #         'callback': callback,
    #         'userdata': userdata,
    #         'wordAlignment': wordAlignment,
    #         'fullText': fullText,
    #         'forbiddens': forbiddens,
    #         'boostings': boostings,
    #         'diarization': diarization,
    #         'sed': sed,
    #     }
    #     headers = {
    #         'Accept': 'application/json;UTF-8',
    #         'Content-Type': 'application/json;UTF-8',
    #         'X-CLOVASPEECH-API-KEY': self.secret
    #     }
    #     return requests.post(headers=headers,
    #                          url=self.invoke_url + '/recognizer/url',
    #                          data=json.dumps(request_body).encode('UTF-8'))
    #
    # def req_object_storage(self, data_key, completion, callback=None, userdata=None, forbiddens=None, boostings=None,
    #                        wordAlignment=True, fullText=True, diarization=None, sed=None):
    #     request_body = {
    #         'dataKey': data_key,
    #         'language': 'enko',
    #         'completion': completion,
    #         'callback': callback,
    #         'userdata': userdata,
    #         'wordAlignment': wordAlignment,
    #         'fullText': fullText,
    #         'forbiddens': forbiddens,
    #         'boostings': boostings,
    #         'diarization': diarization,
    #         'sed': sed,
    #     }
    #     headers = {
    #         'Accept': 'application/json;UTF-8',
    #         'Content-Type': 'application/json;UTF-8',
    #         'X-CLOVASPEECH-API-KEY': self.secret
    #     }
    #     return requests.post(headers=headers,
    #                          url=self.invoke_url + '/recognizer/object-storage',
    #                          data=json.dumps(request_body).encode('UTF-8'))

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

# if __name__ == '__main__':
#     # res = ClovaSpeechClient().req_url(url='http://example.com/media.mp3', completion='sync')
#     # res = ClovaSpeechClient().req_object_storage(data_key='data/media.mp3', completion='sync')
#     res = ClovaSpeechClient().req_upload(file='../data/test_1.m4a', completion='sync')
#     # res = ClovaSpeechClient().req_upload(file='/')
#     print(res.text)

# if __name__ == '__main__':
#     res = ClovaSpeechClient().req_upload(file='../data/test_1.m4a', completion='sync')
#     result = res.json()
#
#     segments = result.get('segments', [])
#     timeline_segments = []
#
#     for segment in segments:
#         timeline_label = segment['start']
#         text = segment['text']
#         timeline_segments.append({'timeline': timeline_label, 'text': text})
#
#     for timeline_segment in timeline_segments:
#         timeline_label = round(timeline_segment['timeline'] * 0.001, 2)
#         text = timeline_segment['text']
#         print(f'{timeline_label}초: {text}')

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
