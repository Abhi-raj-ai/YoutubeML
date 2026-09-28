import re
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# Model paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "comment_summary"
    / "distilbert_v2"
)


# --------------------------------------------------
# Load tokenizer and model
# --------------------------------------------------

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_PATH
)


# --------------------------------------------------
# Label mapping
# --------------------------------------------------

label_map = {
    0: "Complaint",
    1: "Other",
    2: "Praise",
    3: "Question",
    4: "Suggestion"
}


# --------------------------------------------------
# Preprocess comments
# --------------------------------------------------

def preprocess_comments(comments):

    cleaned_comments = []

    for comment in comments:

        # Convert to string
        comment = str(comment)

        # 1. Remove numbers
        comment = re.sub(
            r'\d+',
            '',
            comment
        )

        # 2. Remove URLs
        comment = re.sub(
            r"http\S+|www\S+",
            "",
            comment
        )

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


# --------------------------------------------------
# Confidence thresholds
# --------------------------------------------------

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

    results = []

    # --------------------------------------------------
    # Extract comment text
    # --------------------------------------------------

    comments_text = [
        comment["comment_text"]
        for comment in comments
    ]

    # --------------------------------------------------
    # Keep original comment dictionaries
    # --------------------------------------------------

    original_comments = comments

    # --------------------------------------------------
    # Preprocess comment text
    # --------------------------------------------------

    clean_comments = preprocess_comments(
        comments_text
    )

    # --------------------------------------------------
    # Tokenize comments
    # --------------------------------------------------

    tokenizer_comments = tokenizer(
        clean_comments,
        padding=True,
        truncation=True,
        return_tensors="pt",
        max_length=32
    )

    # --------------------------------------------------
    # Evaluation mode
    # --------------------------------------------------

    model.eval()

    # --------------------------------------------------
    # Model prediction
    # --------------------------------------------------

    with torch.no_grad():

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
    # Create prediction results
    # --------------------------------------------------

    for i in range(len(predicted_ids)):

        # Get predicted class ID
        predicted_id = predicted_ids[i].item()

        # Convert class ID to intent
        intent = label_map[predicted_id]

        # Get confidence score
        confidence = round(
            probabilities[i][predicted_ids[i]].item() * 100,
            2
        )

        # Apply class-specific threshold
        final_intent = apply_threshold(
            intent,
            confidence
        )

        # --------------------------------------------------
        # Create result
        # --------------------------------------------------

        result = {
            "comment_id": original_comments[i]["comment_id"],
            "Comment": original_comments[i]["comment_text"],
            "Intent": intent,
            "Intent_Confidence": confidence,
            "Final_Intent": final_intent
        }

        results.append(result)

    return results


# --------------------------------------------------
# Create intent analytics
# --------------------------------------------------

def get_intent_analytics(comments):

    # Calculate total comments
    total_comments = len(comments)

    # Convert predictions to DataFrame
    df = pd.DataFrame(comments)

    # Calculate intent count
    intent_count = df["Final_Intent"].value_counts()

    # Calculate intent percentage
    intent_percentage = (
        df["Final_Intent"]
        .value_counts(normalize=True)
        * 100
    )

    result = {
        "total_comments": total_comments,
        "intent_count": intent_count,
        "intent_percentage": intent_percentage
    }

    return result