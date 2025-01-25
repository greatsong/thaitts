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
def translate_and_transliterate(text, source_lang):
    if not text.strip():
        return "", ""
        
    try:
        if source_lang == "한글":
            prompt = f"""Your task:
1. Translate the given text into Thai.
2. On the next line, write the Korean pronunciation guide for the Thai translation (how to read the Thai words in Korean).

Rules:
- Always output in two lines.
- The first line should ONLY contain the Thai translation.
- The second line should ONLY contain the Korean pronunciation.
- Do not add any labels, numbers, or additional explanations.

Text to translate: {text}"""
        else:  # 태국어 입력
            prompt = f"""Your task:
1. Translate the given Thai text into Korean.
2. On the next line, write the Korean pronunciation guide for the Thai text (how to read the Thai words in Korean).

Rules:
- Always output in two lines.
- The first line should ONLY contain the Korean translation.
- The second line should ONLY contain the Korean pronunciation.
- Do not add any labels, numbers, or additional explanations.

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

def create_file_name(text, source_lang):
    # 오늘 날짜 가져오기
    today_date = datetime.now().strftime("%y%m%d")
    
    if source_lang == "한글":
        file_name_base = text[:10]  # 한글 입력 시, 처음 10글자 사용
    else:
        file_name_base = translate_and_transliterate(text, "태국어")[0][:10]  # 태국어를 한글 번역
    
    file_name_base = file_name_base.replace(" ", "").strip()  # 공백 제거
    return f"{file_name_base}({today_date}).mp3"

def main():
    st.title("🌟 하늘씨앗교회 태국 선교 파이팅!! 🌟")
    st.subheader("🇹🇭 한글 또는 태국어를 입력하거나 파일로 업로드하세요!")
    st.write("🎧 **텍스트를 번역하고 발음을 확인하며 음성을 생성합니다.** 🎧")

    col1, col2 = st.columns(2)
    with col1:
        input_language = st.radio("입력 언어:", ["한글", "태국어"])
    with col2:
        input_method = st.radio("입력 방식:", ["텍스트 창 입력", "텍스트 파일 업로드"])

    if input_method == "텍스트 창 입력":
        user_text = st.text_area("📝 텍스트를 입력하세요:", height=150)
    else:
        uploaded_file = st.file_uploader("📂 텍스트 파일을 업로드하세요:", type=["txt"])
        user_text = uploaded_file.read().decode("utf-8") if uploaded_file else ""

    if st.button("번역 및 MP3 생성", type="primary"):
        if not user_text.strip():
            st.error("❌ 텍스트를 입력해주세요!")
            return

        with st.spinner("🔄 번역 중..."):
            translation, pronunciation = translate_and_transliterate(user_text, input_language)
            
            if translation and pronunciation:
                st.write("🌏 번역 결과:")
                st.info(f"**입력 ({input_language}):**\n{user_text}")
                st.success(f"**번역 결과:**\n{translation}")
                st.info(f"**발음:**\n{pronunciation}")
                
                # MP3 파일 이름 생성
                tts_text = user_text if input_language == "태국어" else translation
                file_name = create_file_name(user_text, input_language)
                
                with st.spinner("🎧 MP3 생성 중..."):
                    mp3_path = generate_tts(tts_text, file_name=file_name)
                    
                    if mp3_path and mp3_path.exists():
                        with open(mp3_path, "rb") as mp3_file:
                            audio_data = mp3_file.read()
                            st.audio(audio_data, format="audio/mpeg")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    label="📥 MP3 파일 다운로드",
                                    data=audio_data,
                                    file_name=file_name,
                                    mime="audio/mpeg"
                                )
                                
                        # 임시 파일 정리
                        try:
                            os.remove(mp3_path)
                        except:
                            pass
                            
                        st.success("✅ 번역 및 MP3 생성 완료! 🎉")

if __name__ == "__main__":
    main()
