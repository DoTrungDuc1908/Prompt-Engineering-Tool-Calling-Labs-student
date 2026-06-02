from __future__ import annotations

import re
from typing import Any


def analyze_sentiment(text: str = "") -> dict[str, Any]:
    """Performs rule-based sentiment analysis on a block of text."""
    if not text:
        return {
            "tool": "sentiment_analysis",
            "sentiment": "Neutral",
            "score": 0.0,
            "positive_words_found": [],
            "negative_words_found": [],
        }

    # Lexicons
    pos_words = {
        "good", "great", "excellent", "awesome", "perfect", "love", "like", "happy", "beautiful", "wonderful", "amazing",
        "hay", "tốt", "tuyệt", "đẹp", "thích", "yêu", "vui", "hài lòng", "ổn", "ngon", "thú vị", "hoàn hảo", "ưu điểm"
    }
    neg_words = {
        "bad", "terrible", "worst", "hate", "dislike", "sad", "ugly", "broken", "useless", "poor", "pain", "annoying",
        "dở", "tồi", "xấu", "ghét", "chán", "buồn", "hỏng", "kém", "tệ", "thất vọng", "khó chịu", "nhược điểm", "lỗi"
    }

    # Tokenize and fold text
    words = re.findall(r"\w+", text.lower())
    
    pos_found = [w for w in words if w in pos_words]
    neg_found = [w for w in words if w in neg_words]

    pos_count = len(pos_found)
    neg_count = len(neg_found)
    total_words = pos_count + neg_count

    if total_words == 0:
        sentiment = "Neutral"
        score = 0.0
    else:
        score = (pos_count - neg_count) / total_words
        score = round(score, 2)
        if score > 0.15:
            sentiment = "Positive"
        elif score < -0.15:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

    return {
        "tool": "sentiment_analysis",
        "sentiment": sentiment,
        "score": score,
        "positive_words_found": list(set(pos_found)),
        "negative_words_found": list(set(neg_found)),
    }
