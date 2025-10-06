import re
import nltk
from nltk.corpus import stopwords
from textblob import TextBlob

# Download necessary data files (run once)
nltk.download("stopwords")

def clean_text(text: str) -> str:
    """Cleans and normalizes text input."""
    text = text.lower().strip()  # Lowercase and remove extra spaces
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)  # Remove URLs
    text = re.sub(r"[^a-zA-Z\s]", "", text)  # Remove special characters/numbers
    text = " ".join(word for word in text.split() if word not in stopwords.words("english"))
    return text

def correct_spelling(text: str) -> str:
    """Automatically corrects minor spelling mistakes."""
    return str(TextBlob(text).correct())

def preprocess_query(query: str) -> str:
    """Complete preprocessing pipeline for user query."""
    cleaned = clean_text(query)
    corrected = correct_spelling(cleaned)
    return corrected
