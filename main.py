import streamlit as st
from pathlib import Path
import openai

# OpenAI API 키 설정
openai.api_key = st.secrets["openai_api_key"]

# Streamlit UI 구성
st.title("🌟 하늘씨앗교회 태국 선교 파이팅!! 🌟")
st.subheader("🇹🇭 한글 또는 태국어 텍스트를 입력하거나 파일로 업로드하세요!")

st.write("🎧 **한글 또는 태국어 텍스트를 번역하고 발음을 확인하며 음성을 생성합니다.** 🎧")

# 입력 방법 선택
input_method = st.radio(
    "입력 방법을 선택하세요:",
    ["한글 / 태국어 텍스트 입력", "한글 / 태국어 텍스트 파일 입력"]
)

# 텍스트 입력 또는 파일 업로드
if input_method == "한글 / 태국어 텍스트 입력":
    user_text = st.text_area("📝 텍스트를 입력하세요:")
elif input_method == "한글 / 태국어 텍스트 파일 입력":
    uploaded_file = st.file_uploader("📂 텍스트 파일을 업로드하세요:", type=["txt"])
    if uploaded_file is not None:
        user_text = uploaded_file.read().decode("utf-8")
    else:
        user_text = ""

# ChatGPT를 이용한 번역 및 발음 생성 함수
def translate_and_transliterate(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # 4o로 지정
        messages=[
            {"role": "system", "content": "You are a translation assistant."},
            {"role": "user", "content": f"Translate the following Korean text into Thai and provide its pronunciation in Korean script:\n{text}"}
        ],
        temperature=0.3,
    )
    output = response["choices"][0]["message"]["content"]
    lines = output.split("\n")
    thai_translation = lines[0].strip()
    thai_pronunciation = lines[1].strip() if len(lines) > 1 else "Pronunciation not available"
    return thai_translation, thai_pronunciation

# TTS 생성 함수
def generate_tts(text, voice="shimmer"):
    output_mp3_path = Path("output.mp3")
    response = openai.Audio.create(
        model="tts-1",
        voice=voice,
        input=text,
    )
    with open(output_mp3_path, "wb") as f:
        f.write(response.content)
    return output_mp3_path

# 변환 및 MP3 생성 처리
if st.button("번역 및 MP3 생성"):
    if not user_text.strip():
        st.error("❌ 텍스트를 입력해주세요!")
    else:
        # 번역 및 발음 생성
        st.write("🔄 번역 중...")
        thai_translation, thai_pronunciation = translate_and_transliterate(user_text)
        
        st.write("🌏 번역 결과:")
        st.markdown(f"**한글 또는 태국어 입력:** {user_text}")
        st.markdown(f"**태국어 번역:** {thai_translation}")
        st.markdown(f"**태국어 발음:** {thai_pronunciation}")
        
        # TTS 생성
        st.write("🎧 MP3 생성 중...")
        mp3_path = generate_tts(thai_translation)

        # MP3 파일 제공
        with open(mp3_path, "rb") as mp3_file:
            st.audio(mp3_file.read(), format="audio/mp3")
            st.download_button(
                label="📥 MP3 파일 다운로드",
                data=mp3_file,
                file_name="output.mp3",
                mime="audio/mp3",
            )

        st.success("✅ 번역 및 MP3 생성 완료! 🎉")
