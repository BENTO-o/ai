import json
import time
import os
from openai import OpenAI
from dotenv import load_dotenv


def load_client():
    # Load the OpenAI API key from the environment
    load_dotenv()
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_script(data, output_file):
    # Load OpenAI client
    client = load_client()

    MAX_TOKENS = 8192
    MODEL_MAX_TOKENS = 4000  # 프롬프트와 응답의 최대 합

    # 시작 시간 기록
    start = time.time()

    # 스크립트 데이터
    script = data["content"]["script"]

    # 텍스트 길이를 제한
    def truncate_text(text, max_length=500):
        return text[:max_length]  # 최대 500자까지만 사용

    # 토큰 계산
    def count_tokens(text):
        return len(text.split())  # 간단한 토큰 계산 (공백 기준)

    # AI 요약 프롬프트 생성 함수
    def ai_summary_prompt(script_chunk, previous_summary=None):
        context = f"이전 청크 요약: {previous_summary}\n\n" if previous_summary else ""
        return (
                context
                + "You are the clerk to summarize the minutes."
                  "1. write the minutes summary in the following format:\n"
                  "1) 개요:\n"
                  " 1-1) 주제: {summarize the key agenda briefly based on the script content. if no information is available, write 'none'.}\n"
                  " 2) 목차:\n"
                  " - {first key discussion point}\n"
                  "   ✓ {give me some main point or "
                  "details or the meaning of the new technical word of this discussion} (add more items as necessary)"
                  " - {second key discussion point}\n"
                  "   ✓ {give me some main point or details or the meaning of the new technical word of this discussion} (add more items as necessary)"
                  " - {third key discussion point} "
                  "   ✓ {give me some main point or details or the meaning of the new technical word of this discussion} (add more items as necessary)"
                  " - {list all major discussion points provided in the script. if no information is available, write 'none'.}\n"
                  "3) 특이사항:\n"
                  " - {first unusual or noteworthy point}\n"
                  " - {second unusual or noteworthy point} (add more items as necessary)\n"
                  " - {list all unusual points provided in the script. if no information is available, write 'none'.}"
                  "2. if any section is not present in the script, write 'none'."
                  "3. ensure the summary is written in KOREAN."
                  "4. do not add any sentences or words other than the format presented above."
                  f"\n\n{json.dumps(script_chunk, ensure_ascii=False)}"
        )

    # 스크립트를 동적으로 분할
    def split_script_into_chunks(script, max_chunk_tokens):
        chunks = []
        current_chunk = []
        current_tokens = 0

        for item in script:
            item_tokens = count_tokens(item["text"])
            if current_tokens + item_tokens > max_chunk_tokens:
                chunks.append(current_chunk)
                current_chunk = []
                current_tokens = 0

            current_chunk.append(item)
            current_tokens += item_tokens

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    # 동적 청크 크기 설정
    chunk_size_tokens = MODEL_MAX_TOKENS // 2
    chunks = split_script_into_chunks(script, chunk_size_tokens)

    # 청크 요약 결과
    chunk_summaries = []
    previous_summary = ""  # 이전 요약 저장

    for chunk in chunks:
        texts = [{"text": truncate_text(item["text"])} for item in chunk]
        prompt = ai_summary_prompt(texts, previous_summary)

        # 프롬프트 길이 확인
        if count_tokens(prompt) > MODEL_MAX_TOKENS:
            print("Skipping chunk due to excessive token size.")
            continue

        try:
            # OpenAI API 호출
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant skilled in summarization."},
                    {"role": "user", "content": prompt}
                ]
            )

            summary = response.choices[0].message.content.strip()
            chunk_summaries.append(summary)
            previous_summary = summary

        except Exception as e:
            print(f"Error with chunk: {e}")
            continue

    # 모든 청크들 모아서 최종 요약 생성
    final_prompt = (
            "below is a summary of several chunks. please create a full summary based on that."
            "1. write the minutes summary in the following format:\n"
            "1) 개요:\n"
            " 1-1) 주제: {summarize the key agenda briefly based on the script content. if no information is available, write 'none'.}\n"
            " 2) 목차:\n"
            " - {first key discussion point}\n"
            "   ✓ {give me some main point or details or the meaning of the new technical word of this discussion} (add more items as necessary)"
            " - {second key discussion point}\n"
            "   ✓ {give me some main point or details or the meaning of the new technical word of this discussion} (add more items as necessary)"
            " - {third key discussion point} "
            "   ✓ {give me some main point or details or the meaning of the new technical word of this discussion} (add more items as necessary)"
            " - {list all major discussion points provided in the script. if no information is available, write 'none'.}\n"
            "3) 특이사항:\n"
            " - {first unusual or noteworthy point}\n"
            " - {second unusual or noteworthy point} (add more items as necessary)\n"
            " - {list all unusual points provided in the script. if no information is available, write 'none'.}"
            "2. if any section is not present in the script, write 'none'."
            "3. ensure the summary is written in KOREAN."
            "4. do not add any sentences or words other than the format presented above."
            + "\n\n".join(chunk_summaries)
    )

    if count_tokens(final_prompt) > MODEL_MAX_TOKENS:
        print("Final prompt too long, truncating.")
        final_prompt = final_prompt[:MODEL_MAX_TOKENS - 500]  # 여유 공간 확보

    try:
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant skilled in summarization."},
                {"role": "user", "content": final_prompt}
            ]
        )

        final_summary = final_response.choices[0].message.content.strip()

        # 출력 JSON 생성
        output_data = {
            "summary": final_summary
        }

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(output_data, file, ensure_ascii=False, indent=4)

        print(f"Updated JSON saved to {output_file}")

    except Exception as e:
        print(f"Error during final summary generation: {e}")

    # 처리 시간 출력
    print(f"{time.time() - start: .4f} sec")
    print("회의록이 다음과 같이 요약되었습니다. \n", final_summary)

    return output_data
