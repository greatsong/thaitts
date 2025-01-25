@st.cache_data(ttl=3600)
def translate_and_transliterate(text, source_lang, target_audience):
    if not text.strip():
        return "", ""
        
    try:
        if target_audience == "유치원생":
            prompt = f"""Your task:
1. Translate the given text into Thai in a way that a kindergarten child can easily understand.
2. Make the translation simple, warm, and friendly, with short sentences.
3. On the next line, write the Korean pronunciation guide for the Thai translation (how to read the Thai words in Korean).

Rules:
- Keep sentences short and clear.
- Use vocabulary that is appropriate for children aged 3–6 years old.
- Do not add labels, numbers, or extra explanations.
- The translation should feel kind and loving, suitable for a Christian missionary message to young children.

Text to translate: {text}"""
        elif target_audience == "초등학생":
            prompt = f"""Your task:
1. Translate the given text into Thai in a way that a primary school child (aged 7–12) can easily understand.
2. Use simple and engaging language that makes the text interesting and relatable for children.
3. On the next line, write the Korean pronunciation guide for the Thai translation (how to read the Thai words in Korean).

Rules:
- Keep sentences clear and moderately short.
- Use age-appropriate vocabulary that encourages curiosity and learning.
- Make the tone friendly and hopeful, reflecting a Christian missionary perspective.
- Avoid labels, numbers, or unnecessary explanations.

Text to translate: {text}"""
        else:  # 중고등학생
            prompt = f"""Your task:
1. Translate the given text into Thai in a way that middle and high school students (aged 13–18) can understand and reflect upon.
2. Use thoughtful and respectful language that conveys a deeper meaning while being relatable to teenagers.
3. On the next line, write the Korean pronunciation guide for the Thai translation (how to read the Thai words in Korean).

Rules:
- Use language that encourages understanding and self-reflection.
- The tone should be inspiring, respectful, and in line with Christian missionary values.
- Do not add labels, numbers, or additional explanations.

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
        
        # 검증: 응답이 예상 형식(2줄)인지 확인
        if len(lines) != 2:
            st.warning(f"API 응답이 예상과 다릅니다. 원본 응답: {output}")
            return "번역 결과를 생성할 수 없습니다.", "발음을 생성할 수 없습니다."
        
        return lines[0], lines[1]
        
    except Exception as e:
        st.error(f"번역 중 오류가 발생했습니다: {str(e)}")
        return "", ""
