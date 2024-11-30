# import os
# import json
# from openai import OpenAI
# from dotenv import load_dotenv
#
#
# # OpenAI API 키 로드
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#
# input_file = "./Data/example2.json"
# output_file = "./Data/corrected_example2.json"
#
#
# # 프롬프트 생성 함수
# def create_stt_improve_prompt(script):
#     return (
#         "The following text is a transcription that includes terminology from various technical fields, such as computer vision, IT, medical imaging, "
#         "engineering, and other specialized domains. Please refine this text by making the following improvements:\n\n"
#         "1. Identify any foreign words or technical terms that are phonetically transcribed in Korean, and replace them with their original English terms.\n"
#         "2. For all other content originally in Korean, keep it in Korean without any translations to English.\n"
#         "3. Correctly identify and standardize any technical terms, acronyms, or field-specific jargon to maintain consistency and clarity.\n"
#         "4. Ensure accuracy by fixing any transcription errors or ambiguities that might confuse the meaning.\n"
#         "5. Please fix the word like 5차, this word actually means 오차.\n"
#         "6. Just give the file modified to json. No additional explanation or Notes needed"
#         "Here is the transcription text:\n\n"
#         f"\n\n{json.dumps(script, ensure_ascii=False)}"
#     )
#
#
# # json 파일 로드
# with open(input_file, "r", encoding="utf-8") as f:
#     data = json.load(f)
#
#
# # 스크립트의 텍스트 데이터만 추출
# script = data["content"]["script"]
# texts = [{"text": item["text"]} for item in script]
#
# # 텍스트 출력 확인
# # for text in texts:
# #     print(text)
#
# # JSON 파일 로드
# with open(input_file, "r", encoding="utf-8") as f:
#     data = json.load(f)
#
# # 스크립트 데이터 추출
# script = data["content"]["script"]
#
# # 스크립트 분할
# chunk_size = 20
# chunks = [script[i:i + chunk_size] for i in range(0, len(script), chunk_size)]
#
# # 교정된 텍스트를 저장할 리스트
# corrected_scripts = []
#
# for chunk in chunks:
#     # 텍스트만 추출
#     texts = [{"text": item["text"]} for item in chunk]
#
#     # OpenAI API 호출
#     response = client.chat.completions.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant skilled in text correction."},
#             {"role": "user", "content": create_stt_improve_prompt(texts)}
#         ]
#     )
#
#     # 변환된 텍스트 저장
#     print(response.choices[0].message.content)

    # corrected_chunk = json.loads(response.choices[0].message.content)
    # print(corrected_chunk)
#     corrected_scripts.extend(corrected_chunk)
#
# # 원본 데이터를 교정된 텍스트로 업데이트
# for original, corrected in zip(script, corrected_scripts):
#     original["text"] = corrected["text"]
#
# # 교정된 데이터를 새 JSON 파일로 저장
# with open(output_file, "w", encoding="utf-8") as f:
#     json.dump(data, f, ensure_ascii=False, indent=4)
#
# print(f"교정된 파일이 '{output_file}'에 저장되었습니다.")

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# OpenAI API 키 로드
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 파일 경로 설정
input_file = "./Data/example2.json"
output_file = "./Data/corrected_example2.json"

# 프롬프트 생성 함수
def create_stt_improve_prompt(script):
    return (
        "The following text is a transcription that includes terminology from various technical fields, such as computer vision, IT, medical imaging, "
        "engineering, and other specialized domains. Please refine this text by making the following improvements:\n\n"
        "1. Identify any foreign words or technical terms that are phonetically transcribed in Korean, and replace them with their original English terms.\n"
        "2. For all other content originally in Korean, keep it in Korean without any translations to English.\n"
        "3. Correctly identify and standardize any technical terms, acronyms, or field-specific jargon to maintain consistency and clarity.\n"
        "4. Ensure accuracy by fixing any transcription errors or ambiguities that might confuse the meaning.\n"
        "5. Please fix the word like 5차, this word actually means 오차.\n"
        "6. Just give the file modified to json. No additional explanation or Notes needed"
        "Here is the transcription text:\n\n"
        f"\n\n{json.dumps(script, ensure_ascii=False)}"
    )

# 원본 JSON 파일 로드
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# 스크립트 데이터 추출
script = data["content"]["script"]

# 스크립트 분할 (한 번에 너무 많은 텍스트를 보낼 수 없으므로 분할)
chunk_size = 20
chunks = [script[i:i + chunk_size] for i in range(0, len(script), chunk_size)]

# 교정된 텍스트를 저장할 리스트
corrected_scripts = []

for chunk in chunks:
    # 텍스트만 추출
    texts = [{"text": item["text"]} for item in chunk]

    # OpenAI API 호출
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant skilled in text correction."},
            {"role": "user", "content": create_stt_improve_prompt(texts)}
        ]
    )

    # 변환된 텍스트 JSON 문자열을 파싱
    corrected_chunk = json.loads(response.choices[0].message.content)
    corrected_scripts.extend(corrected_chunk)

# 원본 JSON의 script 내용 교체
for i, corrected in enumerate(corrected_scripts):
    script[i]["text"] = corrected["text"]

# 수정된 데이터를 새로운 JSON 파일로 저장
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Updated JSON saved to {output_file}")