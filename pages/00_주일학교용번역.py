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

@st.cache_data()
@st.cache_data(ttl=3600)
def translate_and_transliterate(text, source_lang):
    if not text.strip():
        return "", ""
        
    try:
        if source_lang == "한글":
            prompt = f"""Task: Translate Korean to Thai for Christian missionary work

Input format: Korean text
Required output format:
Line 1: Thai translation using standard Thai script
Line 2: Korean phonetic guide using common Korean syllables

Translation rules:
- Maintain Christian theological terms accurately
- Keep sentence structures simple but natural
- Preserve honorific expressions appropriately

Pronunciation guide rules:
- Use Korean syllables that best match Thai sounds
- Write each syllable separated by spaces
- Follow standard Thai pronunciation patterns

Example 1:
Input: 하나님은 사랑이십니다
Output:
พระเจ้าคือความรัก
프라짜오 쿠 크왐락

Example 2:
Input: 예수님을 믿으세요
Output:
เชื่อในพระเยซู
츠아 나이 프라예수

Text to translate: {text}"""

        else:  # 태국어
            prompt = f"""Task: Translate Thai to Korean for Christian missionary work

Input format: Thai text
Required output format:
Line 1: Korean translation using proper Korean grammar
Line 2: Thai pronunciation guide in Korean syllables

Translation rules:
- Use natural Korean expressions
- Maintain appropriate honorific levels
- Preserve Christian theological terminology

Pronunciation guide rules:
- Break down Thai words into Korean syllables
- Separate each syllable with spaces
- Match Thai tones as closely as possible with Korean sounds

Example 1:
Input: พระเจ้าทรงรักเรา
Output:
하나님께서 우리를 사랑하십니다
프라짜오 송 락 라우

Example 2:
Input: พระเยซูเป็นพระผู้ช่วยให้รอด
Output:
예수님은 구세주이십니다
프라예수 펀 프라푸추아이 하이 롯

Text to translate: {text}"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Christian missionary translation assistant specializing in Thai-Korean translations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        output = response.choices[0].message.content.strip()
        lines = [line.strip() for line in output.split("\n") if line.strip()]
        if len(lines) != 2:
            raise ValueError("번역 결과가 예상 형식과 다릅니다.")
        
        return lines[0], lines[1]

def generate_tts_per_sentence(text, target_audience):
    if not text.strip():
        return []
        
    sentences = [s.strip() for s in text.split('\n') if s.strip()]
    audio_paths = []
    
    with st.progress(0) as progress_bar:
        for i, sentence in enumerate(sentences):
            try:
                file_name = f"sentence_{i+1}_{target_audience}.mp3"
                output_dir = "temp_audio"
                os.makedirs(output_dir, exist_ok=True)
                output_path = Path(output_dir) / file_name
                
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="shimmer",
                    input=sentence
                )
                
                with open(output_path, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
                        
                audio_paths.append(output_path)
                progress_bar.progress((i + 1) / len(sentences))
                
            except Exception as e:
                st.error(f"음성 생성 중 오류: {str(e)}")
                
    return audio_paths

def main():
    st.set_page_config(page_title="태국 선교 번역 도구", layout="wide")
    
    st.markdown("""
    <h1 style='text-align: center; color: #1E88E5;'>🌟 태국 선교를 위한 번역 도구 🌟</h1>
    <h3 style='text-align: center; color: #424242;'>맞춤형 번역과 음성 생성 서비스</h3>
    """, unsafe_allow_html=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📝 입력 설정")
            input_language = st.radio(
                "입력 언어를 선택하세요:",
                ["한글", "태국어"],
                format_func=lambda x: {"한글": "🇰🇷 한글", "태국어": "🇹🇭 태국어"}[x]
            )
            
        with col2:
            st.markdown("### 👥 대상 설정")
            target_audience = st.radio(
                "번역 대상을 선택하세요:",
                ["유치원생", "초등학생", "중고등학생"],
                format_func=lambda x: {
                    "유치원생": "🎈 유치원생 (3-6세)",
                    "초등학생": "✏️ 초등학생 (7-12세)",
                    "중고등학생": "📚 중고등학생 (13-18세)"
                }[x]
            )

    st.markdown("---")

    tab1, tab2 = st.tabs(["📝 텍스트 입력", "📂 파일 업로드"])
    
    with tab1:
        user_text = st.text_area(
            "텍스트를 입력하세요:",
            height=150,
            placeholder="여기에 번역할 텍스트를 입력하세요..."
        )
        
    with tab2:
        uploaded_file = st.file_uploader(
            "텍스트 파일을 업로드하세요:",
            type=["txt"],
            help="UTF-8 인코딩된 텍스트 파일만 지원합니다."
        )
        if uploaded_file:
            user_text = uploaded_file.read().decode("utf-8")

    if st.button("🚀 번역 시작", type="primary", use_container_width=True):
        if not user_text.strip():
            st.error("❌ 텍스트를 입력해주세요!")
            return

        with st.spinner("🔄 번역 중..."):
            translation, pronunciation = translate_and_transliterate(
                user_text, input_language, target_audience
            )
            
            if translation and pronunciation:
                st.markdown("---")
                st.markdown("### 📊 번역 결과")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("#### 원문")
                    st.info(user_text)
                    
                with col2:
                    st.markdown("#### 번역")
                    st.success(translation)
                    
                with col3:
                    st.markdown("#### 발음")
                    st.info(pronunciation)

                st.markdown("---")
                st.markdown("### 🎧 음성 생성")
                
                tts_text = user_text if input_language == "태국어" else translation
                audio_paths = generate_tts_per_sentence(tts_text, target_audience)

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
                                        file_name=f"sentence_{i}_{target_audience}.mp3",
                                        mime="audio/mpeg",
                                        use_container_width=True
                                    )
                                    
                    st.success("✅ 번역 및 음성 생성이 완료되었습니다!")

if __name__ == "__main__":
    main()
