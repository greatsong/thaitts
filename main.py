import streamlit as st
from pathlib import Path
from openai import OpenAI
from googletrans import Translator
from io import BytesIO
from IPython.display import Audio

# OpenAI API 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])  # OpenAI API 키 입력

# Google Translator 초기화
translator = Translator()

# 음성 옵션 목록
voice_options = [
    "alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"
]

# Streamlit UI 구성
st.title("TTS with OpenAI: Text to Speech")
st.write("텍스트를 음성으로 변환하고, MP3 파일을 다운로드하세요.")
st.write("추가로 한글 텍스트를 태국어로 번역 후 음성으로 변환할 수도 있습니다.")

# 음성 선택
selected_voice = st.selectbox("음성을 선택하세요:", options=voice_options)

# 텍스트 입력 방식 선택
input_method = st.radio("텍스트 입력 방식을 선택하세요:", ["텍스트 입력", "파일 업로드"])

# 텍스트 입력 또는 파일 업로드 처리
if input_method == "텍스트 입력":
    user_text = st.text_area("텍스트를 입력하세요:")
elif input_method == "파일 업로드":
    uploaded_file = st.file_uploader("텍스트 파일을 업로드하세요:", type=["txt"])
    if uploaded_file is not None:
        user_text = uploaded_file.read().decode("utf-8")
    else:
        user_text = ""

# 번역 및 변환 옵션 선택
translate_to_thai = st.checkbox("한글 텍스트를 태국어로 번역하기")

# 변환 및 다운로드 처리
if st.button("MP3 생성"):
    if not user_text.strip():
        st.error("텍스트를 입력하거나 파일을 업로드하세요!")
    else:
        # 한글을 태국어로 번역
        if translate_to_thai:
            thai_text = translator.translate(user_text, src="ko", dest="th").text
            st.write("번역된 태국어:")
            st.write(thai_text)
        else:
            thai_text = user_text

        # TTS 변환 및 MP3 생성
        output_mp3_path = Path("output.mp3")
        response = client.audio.speech.create(
            model="tts-1",
            voice=selected_voice,
            input=thai_text,
        )
        response.stream_to_file(output_mp3_path)

        # MP3 파일 재생 및 다운로드 제공
        with open(output_mp3_path, "rb") as mp3_file:
            st.audio(mp3_file.read(), format="audio/mp3")
            st.download_button(
                label="MP3 파일 다운로드",
                data=mp3_file,
                file_name="output.mp3",
                mime="audio/mp3",
            )

        st.success("MP3 파일 생성 완료!")

