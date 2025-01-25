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
def translate_and_transliterate(text, source_lang, target_audience):
    if not text.strip():
        return "", ""
        
    try:
        sentences = text.split("\n")
        translations = []
        pronunciations = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            if source_lang == "태국어":
                prompt = f"""Your task:
1. Translate the following Thai text into Korean accurately and contextually.
2. Ensure the translation is clear and suitable for understanding by native Korean speakers.
3. On the next line, write the Korean pronunciation guide for the given Thai text.

Rules:
- Always output in two lines.
- The first line should ONLY contain the accurate Korean translation.
- The second line should ONLY contain the Korean pronunciation.
- Do not add labels or additional explanations.

Text to translate: {sentence}"""
            else:
                if target_audience == "유치원생":
                    prompt = f"""Your task:
1. Translate into Thai for kindergarten children.
2. Make it simple, warm, and friendly.
3. Write Korean pronunciation guide on next line.

Rules:
- Keep sentences very short and clear
- Use vocabulary for ages 3-6
- Make it loving and suitable for Christian message

Text to translate: {sentence}"""
                elif target_audience == "초등학생":
                    prompt = f"""Your task:
1. Translate into Thai for elementary students.
2. Use clear language for ages 7-12.
3. Write Korean pronunciation guide on next line.

Rules:
- Use age-appropriate vocabulary
- Keep a friendly but educational tone
- Make Christian concepts understandable

Text to translate: {sentence}"""
                else:  # 중고등학생
                    prompt = f"""Your task:
1. Translate into Thai for teenage students.
2. Use more sophisticated language.
3. Write Korean pronunciation guide on next line.

Rules:
- Use varied vocabulary and natural expressions
- Include appropriate theological terms
- Keep an engaging tone for teenagers

Text to translate: {sentence}"""
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a translation assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            output = response.choices[0].message.content.strip()
            lines = [line.strip() for line in output.split("\n") if line.strip()]
            
            if len(lines) == 2:
                translations.append(lines[0])
                pronunciations.append(lines[1])
            else:
                st.warning(f"API 응답이 예상과 다릅니다: {output}")
                translations.append("번역 오류")
                pronunciations.append("발음 오류")
        
        return "\n".join(translations), "\n".join(pronunciations)
        
    except Exception as e:
        st.error(f"번역 중 오류 발생: {str(e)}")
        return "", ""

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
