import streamlit as st
from pathlib import Path
from openai import OpenAI
import os
from datetime import datetime

# OpenAI client initialization with error handling
try:
    client = OpenAI(api_key=st.secrets["openai_api_key"])
except Exception as e:
    st.error("OpenAI API 키 설정에 문제가 있습니다.")
    st.stop()

@st.cache_data(ttl=3600)
def translate_and_transliterate(text, source_lang, target_audience):
    if not text.strip():
        return "", ""
        
    try:
        if target_audience == "유치원생":
            prompt = f"""Your task:
1. Translate the given text into Thai in a way that a kindergarten child can easily understand.
2. Make the translation simple, warm, and friendly, with short sentences.
3. On the next line, write the Korean pronunciation guide for the Thai translation (how to read the Thai words in Korean).

Rules:
- Keep sentences short and clear.
- Use vocabulary that is appropriate for children aged 3–6 years old.
- Do not add labels, numbers, or extra explanations.
- The translation should feel kind and loving, suitable for a Christian missionary message to young children.

Text to translate: {text}"""
        elif target_audience == "초등학생":
            prompt = f"""Your task:
1. Translate the given text into Thai in a way that a primary school child (aged 7–12) can easily understand.
2. Use simple and engaging language that makes the text interesting and relatable for children.
3. On the next line, write the Korean pronunciation guide for the Thai translation (how to read the Thai words in Korean).

Rules:
- Keep sentences clear and moderately short.
- Use age-appropriate vocabulary that encourages curiosity and learning.
- Make the tone friendly and hopeful, reflecting a Christian missionary perspective.
- Avoid labels, numbers, or unnecessary explanations.

Text to translate: {text}"""
        else:  # 중고등학생
            prompt = f"""Your task:
1. Translate the given text into Thai in a way that middle and high school students (aged 13–18) can understand and reflect upon.
2. Use thoughtful and respectful language that conveys a deeper meaning while being relatable to teenagers.
3. On the next line, write the Korean pronunciation guide for the Thai translation (how to read the Thai words in Korean).

Rules:
- Use language that encourages understanding and self-reflection.
- The tone should be inspiring, respectful, and in line with Christian missionary values.
- Do not add labels, numbers, or additional explanations.

Text to translate: {text}"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a translation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        output = response.choices[0].message.content.strip()
        lines = [line.strip() for line in output.split("\n") if line.strip()]
        if len(lines) != 2:
            raise ValueError("Unexpected output format from OpenAI API")
        
        return lines[0], lines[1]
        
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
    file_name_base = text[:10].replace(" ", "").strip()  # 텍스트 첫 10글자 (공백 제거)
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

    user_text = st.text_area("📝 텍스트를 입력하세요:", height=150)

    if st.button("번역 및 MP3 생성", type="primary"):
        if not user_text.strip():
            st.error("❌ 텍스트를 입력해주세요!")
            return

        with st.spinner(f"🔄 {target_audience} 대상 번역 중..."):
            translation, pronunciation = translate_and_transliterate(user_text, input_language, target_audience)
            
            if translation and pronunciation:
                st.write("🌏 번역 결과:")
                st.info(f"**입력 ({input_language}):**\n{user_text}")
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
