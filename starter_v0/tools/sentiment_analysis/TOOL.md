---
name: sentiment_analysis
track: bonus
kind: local_formatter
requires_env: []
inputs: [text]
outputs: [sentiment, score, positive_words_found, negative_words_found]
side_effect: false
---
# sentiment_analysis

Performs rule-based sentiment analysis on a block of text. Analyzes both English and Vietnamese text for positive and negative emotional words, and returns a sentiment label (Positive, Negative, or Neutral) and confidence score. Useful for analyzing comments, articles, or social media posts.
