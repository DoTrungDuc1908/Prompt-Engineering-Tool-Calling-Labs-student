---
name: text_statistics
track: bonus
kind: local_formatter
requires_env: []
inputs: [text]
outputs: [word_count, char_count, sentence_count, estimated_reading_time_min, vocabulary_diversity]
side_effect: false
---
# text_statistics

Calculates statistics for a block of text, including word count, character count, sentence count, estimated reading time (in minutes), and vocabulary diversity. Useful for analyzing articles, summaries, or reports.
