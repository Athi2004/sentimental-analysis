from app import predict_emotion

def test_predict_emotion():
    # Test cases: (input_text, expected_language, expected_translation_happens)
    test_cases = [
        ("I am happy today!", "en", False),  # English, no translation
        ("Estoy feliz hoy!", "es", True),    # Spanish, translate to English
        ("Je suis heureux aujourd'hui!", "fr", True),  # French
        ("Ich bin heute glücklich!", "de", True),     # German
        ("今日は幸せです！", "ja", True),             # Japanese
        ("", "en", False),  # Empty string, default to en
        ("123", "en", False),  # Numbers, default to en
    ]

    for text, expected_lang, should_translate in test_cases:
        try:
            emotion, confidence = predict_emotion(text)
            print(f"Input: '{text}' -> Emotion: {emotion}, Confidence: {confidence}%")
            if should_translate:
                print(f"  (Translated from {expected_lang})")
        except Exception as e:
            print(f"Error with '{text}': {e}")

if __name__ == "__main__":
    test_predict_emotion()
