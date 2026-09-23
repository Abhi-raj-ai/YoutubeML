import re
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "comment_summary" / "distilbert_v2"


tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
label_map = {
    0: "Complaint",
    1: "Other",
    2: "Praise",
    3: "Question",
    4: "Suggestion"

}



def preprocess_comments(comments):

    cleaned_comments = []

    for comment in comments:

        # Convert to string
        comment = str(comment)

        # 1. Remove numbers
        comment = re.sub(r'\d+', '', comment)

        # 2. Remove URLs
        comment = re.sub(r"http\S+|www\S+", "", comment)

        # 3. Remove HTML tags
        comment = BeautifulSoup(
            comment,
            "html.parser"
        ).get_text()

        # 4. Remove duplicate punctuation
        comment = re.sub(
            r'([!?.,])\1+',
            r'\1',
            comment
        )

        # 5. Remove extra spaces
        comment = re.sub(
            r"\s+",
            " ",
            comment
        ).strip()

        cleaned_comments.append(comment)

    return cleaned_comments


thresholds = {
    "Complaint": 80,
    "Other": 65,
    "Praise": 85,
    "Question": 70,
    "Suggestion": 55
}


# --------------------------------------------------
# Apply confidence threshold
# --------------------------------------------------

def apply_threshold(intent, confidence):

    threshold = thresholds[intent]

    if confidence >= threshold:
        return intent

    return "Uncertain"


# --------------------------------------------------
# Predict intent for multiple comments
# --------------------------------------------------

def predict_comments(comments):

    # Keep original comments
    original_comments = comments

    # Preprocess comments
    clean_comments = preprocess_comments(comments)

    # Tokenize
    tokenizer_comments = tokenizer(
        clean_comments,
        padding=True,
        truncation=True,
        return_tensors="pt",
        max_length=32
    )

    # Evaluation mode
    model.eval()

    with torch.no_grad():

        # Model prediction
        distill_model = model(
            **tokenizer_comments
        )

        logits = distill_model.logits

        # Convert logits to probabilities
        probabilities = torch.softmax(
            logits,
            dim=1
        )

        # Get predicted class
        predicted_ids = torch.argmax(
            probabilities,
            dim=1
        )

    # --------------------------------------------------
    # Create results
    # --------------------------------------------------

    results = []

    for i in range(len(predicted_ids)):

        # Convert ID to intent name
        predicted_id = predicted_ids[i].item()

        intent = label_map[predicted_id]

        # Get confidence
        confidence = round(
            probabilities[i][predicted_ids[i]].item() * 100,
            2
        )

        # Apply class-specific threshold
        final_intent = apply_threshold(
            intent,
            confidence
        )

        # Store result
        result = {
            "Comment": original_comments[i],
            "Intent": intent,
            "Intent_Confidence": confidence,
            "Final_Intent": final_intent
        }

        results.append(result)

    return results


    # --------------------------------------------------
    # Create comments analytics
    # --------------------------------------------------


def get_intent_analytics(comments):

    # cal total comments
    total_comments = len(comments)


    # cal final intent count and it's percentage
    df = pd.DataFrame(comments)
    intent_count = df['Final_Intent'].value_counts()
    intent_percentage = df['Final_Intent'].value_counts(normalize=True) * 100

    result = {
        'total_comments': total_comments,
        'intent_count': intent_count,
        'intent_percentage': intent_percentage
    }
    return result

