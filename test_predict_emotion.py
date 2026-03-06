from app import predict_emotion

# Test cases
test_cases = [
    "This is a neutral comment without keywords",  # Should trigger API fallback
    "I am happy today",  # Should match keyword "happy" -> Joy
    "This makes me sad",  # Should match keyword "sad" -> Sadness
    "",  # Empty text
    "Some text in another language: Je suis content",  # Non-English, should translate and check
]

for text in test_cases:
    try:
        emotion, confidence = predict_emotion(text)
        print(f"Text: '{text}' -> Emotion: {emotion}, Confidence: {confidence}")
    except Exception as e:
        print(f"Error for text '{text}': {e}")
