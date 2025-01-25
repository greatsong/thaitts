import streamlit as st
from pathlib import Path
from openai import OpenAI
import os

# OpenAI client initialization with error handling
try:
    client = OpenAI(api_key=st.secrets["openai_api_key"])
except Exception as e:
    st.error("OpenAI API 키 설정에 문제가 있습니다.")
    st.stop()

# 캐시 데코레이터 추가
@st.cache_data(ttl=3600)
def translate_and_transliterate(text, source_lang):
    if not text.strip():
        return "", ""
        
    try:
        if source_lang == "한글":
            prompt = f"Translate the following Korean text into Thai. Then provide the Thai text's pronunciation in Korean script:\n{text}"
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
        lines = [line.replace('Thai Translation:', '').replace('Korean Pronunciation:', '').strip() 
                for line in output.split("\n")]
        translation = lines[0].strip()
        pronunciation = lines[1].strip() if len(lines) > 1 else "발음을 생성할 수 없습니다."
        return translation, pronunciation
        
    except Exception as e:
        st.error(f"번역 중 오류가 발생했습니다: {str(e)}")
        return "", ""

def generate_tts(text, voice="shimmer"):
    if not text.strip():
        return None
        
    try:
        output_dir = "temp_audio"
        os.makedirs(output_dir, exist_ok=True)
        output_mp3_path = Path(output_dir) / "output.mp3"
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        response.stream_to_file(str(output_mp3_path))
        return output_mp3_path
        
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
                            st.audio(audio_data, format="audio/mp3")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    label="📥 MP3 파일 다운로드",
                                    data=audio_data,
                                    file_name="output.mp3",
                                    mime="audio/mp3"
                                )
                                
                        # 임시 파일 정리
                        try:
                            os.remove(mp3_path)
                        except:
                            pass
                            
                        st.success("✅ 번역 및 MP3 생성 완료! 🎉")

if __name__ == "__main__":
    main()
