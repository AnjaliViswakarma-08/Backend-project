import re
from transformers import pipeline

def summarize_text(text):
    """Cleans, splits, and summarizes the given text"""
    if not text:
        return "No notes found for summarization."

    # Preprocess text
    clean_text = re.sub(r'\s+', ' ', text.replace('\n', ' ').replace('\t', ' ')).strip()
    clean_text = re.sub(r'[^A-Za-z0-9.,!?;:\s]', '', clean_text)

    # Split long text
    chunks = [clean_text[i:i+1000] for i in range(0, len(clean_text), 1000)] if len(clean_text) > 1500 else [clean_text]

    # Summarization model
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    # Generate summary
    final_summary = ""
    for chunk in chunks:
        summary = summarizer(chunk, max_length=100, min_length=30, do_sample=False)
        final_summary += summary[0]['summary_text'] + " "

    return final_summary.strip()