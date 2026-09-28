from pathlib import Path
import joblib


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models" / "sentiment_model"

MODEL_PATH = MODEL_DIR / "sentiment_model.pkl"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.pkl"


sentiment_model = joblib.load(MODEL_PATH)

tfidf_vectorizer = joblib.load(VECTORIZER_PATH)


def predict_sentiments(comments):

    results = []

    comments_text = [comment['comment_text'] for comment in comments]

    # Convert all comments into TF-IDF vectors at once
    comments_tfidf = tfidf_vectorizer.transform(comments_text)

    # Predict sentiment for all comments
    predict_sentiments = sentiment_model.predict(comments_tfidf)

    # Get probabilities for all comments
    probabilities = sentiment_model.predict_proba(comments_tfidf)

    # Process each prediction
    for comment, sentiment, probability in zip(comments,predict_sentiments, probabilities):

        # Find the position of the predicted class
        prediction_index = list(sentiment_model.classes_).index(sentiment)

        # Get probability of the predicted class
        confidence_score = probability[prediction_index]

        # if confidence_score < 0.8:
        #     prediction = "Neutral"

        # Store result
        result = {
            "comment_id": comment['comment_id'],
            "Comment": comment['comment_text'],
            "Sentiment": sentiment,
            "Sentiment_Confidence": float(round(confidence_score * 100,2))
        }

        results.append(result)

    return results

