import streamlit as st
from pathlib import Path
from openai import OpenAI
import os
from datetime import datetime

try:
    client = OpenAI(api_key=st.secrets["openai_api_key"])
except Exception as e:
    st.error("OpenAI API 키 설정에 문제가 있습니다.")
    st.stop()

@st.cache_data(ttl=3600)
def translate_and_transliterate(text, source_lang):
    try:
        if not text.strip():
            return "", ""
            
        if source_lang == "한글":
            prompt = f"""Task: Translate Korean to Thai

Rules:
- Return EXACTLY 2 lines
- Line 1: Thai translation
- Line 2: Korean pronunciation of Thai

Example Input: 하나님은 사랑이십니다
Example Output:
พระเจ้าคือความรัก
프라짜오 쿠 크왐락

Input: {text}"""

        else:  # 태국어
            prompt = f"""Task: Translate Thai to Korean

Rules:
- Return EXACTLY 2 lines
- Line 1: Korean translation
- Line 2: Thai pronunciation in Korean

Example Input: พระเจ้าทรงรักเรา
Example Output:
하나님께서 우리를 사랑하십니다
프라짜오 송락 라우

Input: {text}"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Thai-Korean translation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        output = response.choices[0].message.content.strip()
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        
        if len(lines) != 2:
            st.error(f"API 응답: {output}")
            raise ValueError("번역 결과가 예상 형식과 다릅니다.")
        
        return lines[0], lines[1]
        
    except Exception as e:
        st.error(f"번역 중 오류가 발생했습니다: {str(e)}")
        return "", ""

def generate_tts_per_sentence(text, voice="shimmer"):
    if not text.strip():
        return []
        
    sentences = [s.strip() for s in text.split('\n') if s.strip()]
    audio_paths = []
    
    try:
        with st.progress(0) as progress_bar:
            for i, sentence in enumerate(sentences):
                file_name = f"sentence_{i+1}.mp3"
                output_dir = "temp_audio"
                os.makedirs(output_dir, exist_ok=True)
                output_path = Path(output_dir) / file_name
                
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=sentence
                )
                
                with open(output_path, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
                        
                audio_paths.append(output_path)
                progress_bar.progress((i + 1) / len(sentences))
                
        return audio_paths
                
    except Exception as e:
        st.error(f"음성 생성 중 오류 발생: {str(e)}")
        return []

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
                st.markdown("### 📝 번역 결과")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.info(f"**원문:**\n{user_text}")
                with col2:
                    st.success(f"**번역:**\n{translation}")
                with col3:
                    st.info(f"**발음:**\n{pronunciation}")
                
                st.markdown("### 🔊 음성")
                tts_text = user_text if input_language == "태국어" else translation
                
                with st.spinner("음성 파일 생성 중..."):
                    audio_paths = generate_tts_per_sentence(tts_text)
                    
                    if audio_paths:
                        for i, path in enumerate(audio_paths, 1):
                            if path.exists():
                                with open(path, "rb") as audio_file:
                                    audio_data = audio_file.read()
                                    col1, col2 = st.columns([3, 1])
                                    with col1:
                                        st.audio(audio_data, format="audio/mpeg")
                                    with col2:
                                        st.download_button(
                                            f"💾 문장 {i} 다운로드",
                                            data=audio_data,
                                            file_name=f"sentence_{i}.mp3",
                                            mime="audio/mpeg"
                                        )
                                        
                                try:
                                    os.remove(path)
                                except:
                                    pass
                                    
                        st.success("✅ 번역 및 음성 생성 완료!")

if __name__ == "__main__":
    main()
