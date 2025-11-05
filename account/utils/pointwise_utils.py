# account/utils/pointwise_utils.py
import nltk
from nltk.tokenize import sent_tokenize

# Download punkt tokenizer once
nltk.download('punkt', quiet=True)

def convert_to_pointwise(text):
    """
    Converts a block of text into point-wise numbered sentences.

    Args:
        text (str): The input text to convert.

    Returns:
        list: A list of numbered sentences as strings.
    """
    if not text or not text.strip():
        return []

    # Split text into sentences
    sentences = sent_tokenize(text)

    # Number each sentence
    pointwise_sentences = [f"{i+1}. {sentence.strip()}" for i, sentence in enumerate(sentences)]

    return pointwise_sentences