from __future__ import annotations

import re
from typing import Any


def get_text_statistics(text: str = "") -> dict[str, Any]:
    """Calculates statistics for a block of text."""
    if not text:
        return {
            "tool": "text_statistics",
            "word_count": 0,
            "char_count": 0,
            "sentence_count": 0,
            "estimated_reading_time_min": 0.0,
            "vocabulary_diversity": 0.0,
        }

    # Word and character count
    words = re.findall(r"\w+", text)
    word_count = len(words)
    char_count = len(text)

    # Sentence count (approximated)
    sentences = re.split(r"[.!?]+", text)
    sentence_count = len([s for s in sentences if s.strip()])

    # Estimated reading time (average 200 words per minute)
    reading_time = round(word_count / 200.0, 2)

    # Vocabulary diversity (ratio of unique words to total words)
    unique_words = len(set(w.lower() for w in words))
    diversity = round(unique_words / word_count, 2) if word_count > 0 else 0.0

    return {
        "tool": "text_statistics",
        "word_count": word_count,
        "char_count": char_count,
        "sentence_count": sentence_count,
        "estimated_reading_time_min": reading_time,
        "vocabulary_diversity": diversity,
    }
