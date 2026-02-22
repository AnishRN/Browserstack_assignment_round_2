import re
import string
from collections import Counter


def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_words(text):
    stop_words = {"the", "and", "is", "are", "to", "in", "on", "de", "la", "el", "que"}
    words = clean_text(text).split()
    return [w for w in words if len(w) > 2 and w not in stop_words]


def analyze_word_frequency(headers):
    all_words = []
    for h in headers:
        all_words.extend(extract_words(h))
    return Counter(all_words)


def find_repeated_words(headers, min_count=2):
    freq = analyze_word_frequency(headers)
    return {w: c for w, c in freq.items() if c > min_count}


def get_top_words(headers, n=10):
    freq = analyze_word_frequency(headers)
    return freq.most_common(n)
