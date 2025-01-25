import streamlit as st
from pathlib import Path
from openai import OpenAI
import os
from datetime import datetime
import re

# OpenAI client initialization with error handling
if "openai_api_key" not in st.secrets:
    st.error("OpenAI API 키가 설정되지 않았습니다. 환경 변수를 확인해주세요.")
    st.stop()

try:
    client = OpenAI(api_key=st.secrets["openai_api_key"])
except Exception as e:
    st.error("OpenAI API 클라이언트를 초기화하는 중 문제가 발생했습니다.")
    st.stop()

@st.cache_data(ttl=3600)
def translate_and_transliterate(text, source_lang, target_audience):
    if not text.strip():
        return "", ""
    
    try:
        sentences = text.split("\n")
        translations = []
        pronunciations = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            if source_lang == "태국어":
                prompt = f"""Your task:
1. Translate the following Thai text into Korean accurately and contextually.
2. Ensure the translation is clear and suitable for understanding by native Korean speakers.
3. On the next line, write the Korean pronunciation guide for the given Thai text (how to read the Thai words in Korean).

Rules:
- Always output in two lines.
- The first line should ONLY contain the accurate Korean translation of the Thai text.
- The second line should ONLY contain the Korean pronunciation of the Thai text (transliteration).
- Do not add labels, numbers, or additional explanations.
- Maintain the context and meaning of the Thai text while translating.
- Write the pronunciation in a way that is easy to read for Korean speakers.

Text to translate: {sentence}"""
            else:
                if target_audience == "유치원생":
                    prompt = f"""Your task:
1. Translate the given text into Thai in a way that a kindergarten child can easily understand.
2. Make the translation simple, warm, and friendly, with short sentences.
3. On the next line, write the Korean pronunciation guide for the Thai translation.

Rules:
- Keep sentences short and clear.
- Use vocabulary appropriate for children aged 3-6 years old.
- The translation should feel kind and loving, suitable for a Christian missionary message.

Text to translate: {sentence}"""
                elif target_audience == "초등학생":
                    prompt = f"""Your task:
1. Translate the given text into Thai suitable for elementary school students.
2. Use clear language and appropriate vocabulary for ages 7-12.
3. On the next line, write the Korean pronunciation guide for the Thai translation.

Rules:
- Use age-appropriate vocabulary and expressions
- Maintain a friendly but educational tone
- Keep religious concepts understandable for this age group

Text to translate: {sentence}"""
                elif target_audience == "중고등학생":
                    prompt = f"""Your task:
1. Translate the given text into Thai suitable for middle/high school students.
2. Use more sophisticated language appropriate for teenagers.
3. On the next line, write the Korean pronunciation guide for the Thai translation.

Rules:
- Use varied vocabulary and natural expressions
- Include appropriate theological terminology when needed
- Maintain an engaging tone for teenagers

Text to translate: {sentence}"""
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a translation assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            output = ""
            if response.choices and len(response.choices) > 0:
                output = response.choices[0].message.content.strip()
            else:
                st.warning("OpenAI 응답이 예상과 다릅니다. 빈 응답을 수신했습니다.")
                translations.append("번역 오류")
                pronunciations.append("발음 오류")
                continue
            
            lines = [line.strip() for line in output.split("\n") if line.strip()]
            if len(lines) == 2:
                translations.append(lines[0])
                pronunciations.append(lines[1])
            else:
                st.warning(f"API 응답이 예상과 다릅니다. 원본 응답: {output}")
                translations.append("번역 오류")
                pronunciations.append("발음 오류")
        
        final_translation = "\n".join(translations)
        final_pronunciation = "\n".join(pronunciations)
        return final_translation, final_pronunciation
    
    except Exception as e:
        st.error(f"번역 중 오류가 발생했습니다: {str(e)}")
        return "", ""

def generate_tts(text, voice="shimmer", file_name="output.mp3"):
    if not text.strip():
        return None
    
    try:
        output_dir = "temp_audio"
        os.makedirs(output_dir, exist_ok=True)
        output_mp3_path = Path(output_dir) / file_name
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        with open(output_mp3_path, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
        
        return output_mp3_path
    
    except Exception as e:
        st.error(f"음성 생성 중 오류가 발생했습니다: {str(e)}")
        return None

def create_file_name(text, target_audience):
    today_date = datetime.now().strftime("%y%m%d")
    file_name_base = re.sub(r"[^\w]", "", text[:10].strip())
    return f"{file_name_base}({today_date})_{target_audience}.mp3"

def main():
    st.title("🌟 태국 선교를 위한 기독교 번역 도구 🌟")
    st.subheader("🇹🇭 유치원생, 초등학생, 중고등학생 대상 맞춤 번역")
    st.write("🎧 **대상에 맞는 번역과 음성을 생성합니다.** 🎧")

    col1, col2 = st.columns(2)
    with col1:
        input_language = st.radio("입력 언어:", ["한글", "태국어"])
    with col2:
        target_audience = st.radio("대상:", ["유치원생", "초등학생", "중고등학생"])

    input_method = st.radio("입력 방식:", ["텍스트 창 입력", "텍스트 파일 업로드"])

    if input_method == "텍스트 창 입력":
        user_text = st.text_area("📝 텍스트를 입력하세요:", height=150)
    else:
        uploaded_file = st.file_uploader("📂 텍스트 파일을 업로드하세요:", type=["txt"])
        user_text = uploaded_file.read().decode("utf-8") if uploaded_file else ""

    if st.button("번역 및 MP3 생성"):
        if not user_text.strip():
            st.error("❌ 텍스트를 입력해주세요!")
            return

        with st.spinner(f"🔄 {target_audience} 대상 번역 중..."):
            translation, pronunciation = translate_and_transliterate(user_text, input_language, target_audience)
            
            if translation and pronunciation:
                st.write("🌏 번역 결과:")
                st.info(f"**입력:**\n{user_text}")
                st.success(f"**번역 결과:**\n{translation}")
                st.info(f"**발음:**\n{pronunciation}")
                
                tts_text = user_text if input_language == "태국어" else translation
                file_name = create_file_name(user_text, target_audience)
                
                with st.spinner("🎧 MP3 생성 중..."):
                    mp3_path = generate_tts(tts_text, file_name=file_name)
                    
                    if mp3_path and mp3_path.exists():
                        with open(mp3_path, "rb") as mp3_file:
                            audio_data = mp3_file.read()
                            st.audio(audio_data, format="audio/mpeg")
                            st.download_button(
                                label="📥 MP3 파일 다운로드",
                                data=audio_data,
                                file_name=file_name,
                                mime="audio/mpeg"
                            )
                        st.success("✅ 번역 및 MP3 생성 완료! 🎉")

if __name__ == "__main__":
    main()
