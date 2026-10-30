import re
import joblib
import numpy as np
from scipy.sparse import hstack
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from config import Config

# Import Zero Trust analysis
from zero_trust import zero_trust_analysis


# =========================
# LOAD TRAINED ARTIFACTS
# =========================
ml_model = joblib.load(Config.ML_MODEL_PATH)
tfidf = joblib.load(Config.TFIDF_VECTORIZER_PATH)
dl_model = load_model(Config.DL_MODEL_PATH)
tokenizer = joblib.load(Config.TOKENIZER_PATH)

# Same value as training notebook
MAX_LEN = 200


# =========================
# TEXT PREPROCESSING
# =========================
def clean_text(text):
    """
    Clean email text:
    - lower case
    - remove URLs
    - remove special characters
    - remove extra spaces
    """
    if text is None:
        return ""

    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)   # remove urls
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)   # keep only letters/numbers/spaces
    text = re.sub(r"\s+", " ", text).strip()      # remove extra spaces
    return text


# =========================
# FEATURE PREPARATION
# =========================
def prepare_email_input(subject, sender, email_text, has_link, has_attachment, urgency_flag):
    """
    Prepare input exactly like training time.
    Returns:
        combined_text_clean
        meta_array
    """
    subject = "" if subject is None else str(subject)
    sender = "" if sender is None else str(sender)
    email_text = "" if email_text is None else str(email_text)

    # Combine text same as notebook
    combined_text = subject + " " + sender + " " + email_text
    combined_text_clean = clean_text(combined_text)

    # Metadata array shape: (1, 3)
    meta_array = np.array([[int(has_link), int(has_attachment), int(urgency_flag)]])

    return combined_text_clean, meta_array


# =========================
# ML PREDICTION
# =========================
def predict_ml(subject, sender, email_text, has_link, has_attachment, urgency_flag):
    """
    Predict using Logistic Regression model
    """
    combined_text_clean, meta_array = prepare_email_input(
        subject, sender, email_text, has_link, has_attachment, urgency_flag
    )

    # TF-IDF transform
    text_tfidf = tfidf.transform([combined_text_clean])

    # Combine text features + metadata
    final_features = hstack([text_tfidf, meta_array])

    # Predict label
    pred_label = ml_model.predict(final_features)[0]

    # Predict phishing probability
    pred_proba = ml_model.predict_proba(final_features)[0][1]

    label_name = "phishing" if pred_label == 1 else "legitimate"

    return {
        "model": "Machine Learning (Logistic Regression)",
        "label": int(pred_label),
        "label_name": label_name,
        "phishing_confidence": round(float(pred_proba) * 100, 2)
    }


# =========================
# DL PREDICTION
# =========================
def predict_dl(subject, sender, email_text, has_link, has_attachment, urgency_flag):
    """
    Predict using Deep Learning model
    Note:
    Current DL model uses only text input (same as notebook training).
    Metadata is accepted for API consistency but not used inside DL model right now.
    """
    combined_text_clean, meta_array = prepare_email_input(
        subject, sender, email_text, has_link, has_attachment, urgency_flag
    )

    # Convert text to sequence
    seq = tokenizer.texts_to_sequences([combined_text_clean])

    # Pad sequence
    padded = pad_sequences(seq, maxlen=MAX_LEN, padding="post", truncating="post")

    # Predict probability
    dl_prob = float(dl_model.predict(padded, verbose=0)[0][0])

    # Convert to label
    pred_label = 1 if dl_prob > 0.5 else 0
    label_name = "phishing" if pred_label == 1 else "legitimate"

    return {
        "model": "Deep Learning (TensorFlow/Keras)",
        "label": int(pred_label),
        "label_name": label_name,
        "phishing_confidence": round(dl_prob * 100, 2)
    }


# =========================
# FINAL HYBRID + ZERO TRUST PREDICTION
# =========================
def predict_email(subject, sender, email_text, has_link, has_attachment, urgency_flag):
    """
    Run ML + DL + Zero Trust analysis and return a combined response.
    """
    # Step 1: ML result
    ml_result = predict_ml(subject, sender, email_text, has_link, has_attachment, urgency_flag)

    # Step 2: DL result
    dl_result = predict_dl(subject, sender, email_text, has_link, has_attachment, urgency_flag)

    # Step 3: Final decision strategy
    # If either model says phishing -> final phishing
    if ml_result["label"] == 1 or dl_result["label"] == 1:
        final_label = 1
        final_label_name = "phishing"
    else:
        final_label = 0
        final_label_name = "legitimate"

    # Final confidence = max of both phishing confidences
    final_confidence = max(
        ml_result["phishing_confidence"],
        dl_result["phishing_confidence"]
    )

    # Step 4: Zero Trust Analysis
    zero_trust_result = zero_trust_analysis(
        subject=subject,
        sender=sender,
        email_text=email_text,
        has_link=has_link,
        has_attachment=has_attachment,
        urgency_flag=urgency_flag,
        ml_result=ml_result,
        dl_result=dl_result
    )

    # Step 5: Final combined output
    return {
        "final_prediction": final_label_name,
        "final_label": final_label,
        "final_confidence": final_confidence,
        "ml_result": ml_result,
        "dl_result": dl_result,
        "zero_trust_result": zero_trust_result
    }


# =========================
# TEST RUN (optional)
# =========================
if __name__ == "__main__":
    sample = predict_email(
        subject="Urgent Account Verification",
        sender="support@fakebank.com",
        email_text="Your account will be suspended. Click here to verify your login immediately.",
        has_link=1,
        has_attachment=0,
        urgency_flag=1
    )

    print("Sample Prediction Result:")
    print(sample)