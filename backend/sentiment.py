from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import numpy as np


model_name = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


LABELS = ['negative', 'neutral', 'positive']

def analyze_sentiment(text: str):
    if not text or not text.strip():
        return {"label": "neutral"}

    # Encode and predict
    encoded_input = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
    output = model(**encoded_input)
    scores = softmax(output.logits.detach().numpy()[0])

    top_label = LABELS[np.argmax(scores)]
    return {"label": top_label}