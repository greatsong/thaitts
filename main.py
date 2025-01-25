import streamlit as st
from pathlib import Path
from openai import OpenAI
import os
import subprocess

# OpenAI client initialization with error handling
try:
    client = OpenAI(api_key=st.secrets["openai_api_key"])
except Exception as e:
    st.error("OpenAI API 키 설정에 문제가 있습니다.")
    st.stop()

# MP3 파일 변환 함수
def convert_to_standard_mp3(input_path, output_path):
    try:
        command = [
            "ffmpeg",
            "-i", input_path,
            "-ar", "44100",  # 표준 샘플링 레이트
            "-ac", "2",      # 스테레오
            "-b:a", "192k",  # 비트레이트
            output_path
        ]
        subprocess.run(command, check=True)
    except Exception as e:
        st.error(f"MP3 변환 중 오류가 발생했습니다: {str(e)}")

# 캐시 데코레이터 추가
@st.cache_data(ttl=3600)
def translate_and_transliterate(text, source_lang):
    if not text.strip():
        return "", ""
        
    try:
        prompt = f"""Your task:
1. Translate the given text into Thai.
2. On the next line, write the Korean pronunciation guide for the Thai translation (how to read the Thai words in Korean).

Rules:
- Always output in two lines.
- The first line should ONLY contain the Thai translation.
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

def generate_tts(text, voice="shimmer"):
    if not text.strip():
        return None
        
    try:
        output_dir = "temp_audio"
        os.makedirs(output_dir, exist_ok=True)
        raw_mp3_path = Path(output_dir) / "raw_output.mp3"
        final_mp3_path = Path(output_dir) / "output.mp3"
        
        # 스트림 방식으로 처리
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        with open(raw_mp3_path, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
        
        # MP3 변환
        convert_to_standard_mp3(raw_mp3_path, final_mp3_path)
        
        return final_mp3_path
        
    except Exception as e:
        st.error(f"음성 생성 중 오류가 발생했습니다: {str(e)}")
        return None

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
                
                with st.spinner("🎧 MP3 생성 중..."):
                    mp3_path = generate_tts(translation)
                    
                    if mp3_path and mp3_path.exists():
                        with open(mp3_path, "rb") as mp3_file:
                            audio_data = mp3_file.read()
                            st.audio(audio_data, format="audio/mpeg")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    label="📥 MP3 파일 다운로드",
                                    data=audio_data,
                                    file_name="output.mp3",
                                    mime="audio/mpeg"
                                )
                                
                        try:
                            os.remove(mp3_path)
                        except:
                            pass
                            
                        st.success("✅ 번역 및 MP3 생성 완료! 🎉")

if __name__ == "__main__":
    main()
