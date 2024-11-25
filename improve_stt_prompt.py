import os
from openai import OpenAI
from dotenv import load_dotenv


# OpenAI API 키 로드
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# STT 텍스트 파일 개선을 위한 프롬프트 생성
def generate_contextual_fix_prompt(text):
    return (
        "The following text is a transcription that includes terminology from various technical fields, such as computer vision, IT, medical imaging, "
        "engineering, and other specialized domains. Please refine this text by making the following improvements:\n\n"
        "1. Identify any foreign words or technical terms that are phonetically transcribed in Korean, and replace them with their original English terms.\n"
        "2. For all other content originally in Korean, keep it in Korean without any translations to English.\n"
        "3. Correctly identify and standardize any technical terms, acronyms, or field-specific jargon to maintain consistency and clarity.\n"
        "4. Ensure accuracy by fixing any transcription errors or ambiguities that might confuse the meaning.\n"
        "5. Please fix the word like 5차, this word actually means 오차.\n"
        "Here is the transcription text:\n\n"
        f"{text}"
    )


# OpenAI API를 사용하여 텍스트 개선하기
def improve_transcription(text):
    prompt = generate_contextual_fix_prompt(text)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an expert in transcription refinement across various technical domains, including IT, computer vision, medical imaging, and engineering."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=2000
    )

    # 응답에서 텍스트를 추출하여 반환
    message_content = response.choices[0].message.content
    return message_content.strip()


# 디렉토리 내 텍스트 파일 읽기 및 처리
def process_text_files_in_directory(directory_path, output_directory):
    # 디렉토리 내 텍스트 파일 반복
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                original_text = file.read()

            # 텍스트 개선
            improved_text = improve_transcription(original_text)

            # 결과를 새 파일로 저장
            output_path = os.path.join(output_directory, f"improved_{filename}")
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(improved_text)

            print(f"Processed and saved: {output_path}")


# 테스트
if __name__ == "__main__":
    # 처리할 텍스트 파일이 있는 디렉토리 경로
    input_dir = "./Data/input_txt"  # 텍스트 파일 저장된 dir
    output_dir = "./Data/output_txt" # 텍스트 파일 저장할 dir

    # output_dir 확인 및 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    process_text_files_in_directory(input_dir, output_dir)
