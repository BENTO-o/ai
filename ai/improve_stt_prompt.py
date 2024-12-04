import os
import json
import asyncio
import aiohttp
from dotenv import load_dotenv

def load_client():
    # Load the OpenAI API key from the environment
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")

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

async def call_openai_api(api_key, chunk):
    """Send a chunk of text to OpenAI API and return the corrected chunk."""
    async with aiohttp.ClientSession() as session:
        texts = [{"text": item["text"]} for item in chunk]
        prompt = create_stt_improve_prompt(texts)
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant skilled in text correction."},
                {"role": "user", "content": prompt},
            ],
        }

        async with session.post(url, headers=headers, json=payload) as response:
            response_data = await response.json()
            content = response_data["choices"][0]["message"]["content"]

            # Remove markdown formatting if present
            if content.startswith("```json"):
                content = content.strip("```json").strip("```").strip()

            return json.loads(content)

async def improve_transcription(input_file, output_file):
    # Load OpenAI API key
    api_key = load_client()

    # Load original JSON file
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract script data
    script = data["content"]["script"]

    # Split the script into chunks
    chunk_size = 20
    chunks = [script[i:i + chunk_size] for i in range(0, len(script), chunk_size)]

    # Asynchronous API calls
    tasks = [call_openai_api(api_key, chunk) for chunk in chunks]
    results = await asyncio.gather(*tasks)

    # Combine results
    corrected_scripts = []
    for corrected_chunk in results:
        corrected_scripts.extend(corrected_chunk)

    # Replace the script content in the original JSON with corrected content
    for i, corrected in enumerate(corrected_scripts):
        script[i]["text"] = corrected["text"]

    # Save the modified data to a new JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Updated JSON saved to {output_file}")

    return data

# Example usage
if __name__ == "__main__":
    asyncio.run(improve_transcription("Data/STT_output/example.json", "Data/improve_output/corrected_example.json"))