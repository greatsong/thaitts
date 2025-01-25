import streamlit as st
from pathlib import Path
from openai import OpenAI

# OpenAI API 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai_api_key"])  # OpenAI API 키 사용

# 음성 옵션 목록
voice_options = [
    "alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"
]

# Streamlit UI 구성
st.title("🌟 하늘씨앗교회 태국 선교 파이팅!! 🌟")
st.subheader("🇹🇭 문장 간 간격을 추가하여 선교 메시지를 음성으로 변환하세요!")

st.write("🙏 **문장 사이에 점(`.`)으로 간격을 추가하여 자연스러운 음성을 만들어보세요.** 🙏")

# 음성 선택
selected_voice = st.selectbox("🎤 음성을 선택하세요:", options=voice_options)

# 쉬는 시간 설정
pause_duration = st.slider(
    "⏳ 문장 사이 점(`.`) 갯수:",
    min_value=0,
    max_value=10,
    value=3,  # 기본값
    step=1
)

# 텍스트 입력 방식 선택
input_method = st.radio("✍️ 텍스트 입력 방식을 선택하세요:", ["텍스트 입력", "파일 업로드"])

# 텍스트 입력 또는 파일 업로드 처리
if input_method == "텍스트 입력":
    user_text = st.text_area("📝 텍스트를 입력하세요:")
elif input_method == "파일 업로드":
    uploaded_file = st.file_uploader("📂 텍스트 파일을 업로드하세요:", type=["txt"])
    if uploaded_file is not None:
        user_text = uploaded_file.read().decode("utf-8")
    else:
        user_text = ""

# 텍스트에 문장 사이 점(`.`) 추가
def add_pauses_to_text(text, pause):
    sentences = text.split(". ")  # 문장을 분리
    pause_text = "." * pause  # 점(`.`) 갯수로 간격 추가
    return pause_text.join(sentences) + "."  # 마지막에 마침표 추가

# 변환 및 다운로드 처리
if st.button("MP3 생성"):
    if not user_text.strip():
        st.error("❌ 텍스트를 입력하거나 파일을 업로드하세요!")
    else:
        # 문장 사이에 점(`.`) 추가
        modified_text = add_pauses_to_text(user_text, pause_duration)
        st.write("🚀 변환된 텍스트:")
        st.code(modified_text)

        # TTS 변환 및 MP3 생성
        output_mp3_path = Path("output.mp3")
        response = client.audio.speech.create(
            model="tts-1",
            voice=selected_voice,
            input=modified_text,
        )
        response.stream_to_file(output_mp3_path)

        # MP3 파일 제공
        with open(output_mp3_path, "rb") as mp3_file:
            st.audio(mp3_file.read(), format="audio/mp3")  # 오디오 재생
            st.download_button(
                label="📥 MP3 파일 다운로드",
                data=mp3_file,
                file_name="output.mp3",
                mime="audio/mp3",
            )

        st.success("✅ MP3 파일 생성 완료! 🎉")
        st.balloons()
