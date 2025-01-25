import streamlit as st
from pathlib import Path
from openai import OpenAI

# OpenAI client initialization
client = OpenAI(api_key=st.secrets["openai_api_key"])

st.title("🌟 하늘씨앗교회 태국 선교 파이팅!! 🌟")
st.subheader("🇹🇭 한글 또는 태국어를 입력하거나 파일로 업로드하세요!")
st.write("🎧 **텍스트를 번역하고 발음을 확인하며 음성을 생성합니다.** 🎧")

input_language = st.radio(
    "입력 언어를 선택하세요:",
    ["한글", "태국어"],
    index=0
)

input_method = st.radio(
    "입력 방식을 선택하세요:",
    ["텍스트 창 입력", "텍스트 파일 업로드"],
    index=0
)

if input_method == "텍스트 창 입력":
    user_text = st.text_area("📝 텍스트를 입력하세요:")
elif input_method == "텍스트 파일 업로드":
    uploaded_file = st.file_uploader("📂 텍스트 파일을 업로드하세요:", type=["txt"])
    if uploaded_file is not None:
        user_text = uploaded_file.read().decode("utf-8")
    else:
        user_text = ""

def translate_and_transliterate(text, source_lang):
    if source_lang == "한글":
        prompt = f"Translate the following Korean text into Thai and provide its pronunciation in Korean script:\n{text}"
    else:
        prompt = f"Translate the following Thai text into Korean and provide its pronunciation in Thai script:\n{text}"
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a translation assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    output = response.choices[0].message.content
    lines = output.split("\n")
    translation = lines[0].strip()
    pronunciation = lines[1].strip() if len(lines) > 1 else "Pronunciation not available"
    return translation, pronunciation

def generate_tts(text, voice="shimmer"):
    output_mp3_path = Path("output.mp3")
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    
    response.stream_to_file(str(output_mp3_path))
    return output_mp3_path

if st.button("번역 및 MP3 생성"):
    if not user_text.strip():
        st.error("❌ 텍스트를 입력해주세요!")
    else:
        st.write("🔄 번역 중...")
        translation, pronunciation = translate_and_transliterate(user_text, input_language)
        
        st.write("🌏 번역 결과:")
        st.markdown(f"**입력 ({input_language}):** {user_text}")
        st.markdown(f"**번역 결과:** {translation}")
        st.markdown(f"**발음:** {pronunciation}")
        
        st.write("🎧 MP3 생성 중...")
        mp3_path = generate_tts(translation)
        
        with open(mp3_path, "rb") as mp3_file:
            audio_data = mp3_file.read()
            st.audio(audio_data, format="audio/mp3")
            st.download_button(
                label="📥 MP3 파일 다운로드",
                data=audio_data,
                file_name="output.mp3",
                mime="audio/mp3"
            )
        
        st.success("✅ 번역 및 MP3 생성 완료! 🎉")
