def translate_and_transliterate(text, source_lang):
    if not text.strip():
        return "", ""
        
    try:
        if source_lang == "한글":
            prompt = f"""Your task:
1. Return ONLY the Thai translation (without any labels or explanation)
2. On the next line, return ONLY the Korean pronunciation guide for that Thai text (how to read the Thai words in Korean)

Text to translate: {text}"""
        else:
            prompt = f"Translate the following Thai text into Korean and provide its pronunciation in Thai script:\n{text}"
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a translation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        output = response.choices[0].message.content.strip()
        
        # 출력 형식을 파싱
        lines = [line.strip() for line in output.split("\n") if line.strip()]
        translation = lines[0] if len(lines) > 0 else "번역 결과를 생성할 수 없습니다."
        pronunciation = lines[1] if len(lines) > 1 else "발음을 생성할 수 없습니다."
        
        # 발음이 'Thai text:'와 같은 불필요한 내용 포함 시 제거
        pronunciation = pronunciation.replace("Thai text:", "").strip()
        return translation, pronunciation
        
    except Exception as e:
        st.error(f"번역 중 오류가 발생했습니다: {str(e)}")
        return "", ""
