import pandas as pd
import joblib
from scipy.sparse import hstack, csr_matrix

# =========================
# 1) Load trained model and vectorizer
# =========================
model = joblib.load("models/ml_model.pkl")
tfidf = joblib.load("models/tfidf_vectorizer.pkl")

print("Model and vectorizer loaded successfully!")

# =========================
# 2) New email example
# =========================
new_email = {
    "subject": "Urgent: Verify Your Bank Account",
    "sender": "support@secure-bank-login.com",
    "email_text": "Your account has been suspended. Click here immediately to verify your identity and avoid permanent closure.",
    "has_link": 1,
    "has_attachment": 0,
    "urgency_flag": 1
}

# =========================
# 3) Combine text
# =========================
combined_text = (
    str(new_email["subject"]) + " " +
    str(new_email["sender"]) + " " +
    str(new_email["email_text"])
)

# =========================
# 4) Convert text into TF-IDF
# =========================
text_vector = tfidf.transform([combined_text])

# =========================
# 5) Metadata features
# =========================
meta_features = csr_matrix([[
    new_email["has_link"],
    new_email["has_attachment"],
    new_email["urgency_flag"]
]])

# =========================
# 6) Combine text + metadata
# =========================
final_input = hstack([text_vector, meta_features])

# =========================
# 7) Predict
# =========================
prediction = model.predict(final_input)[0]
confidence = model.predict_proba(final_input)[0][1]

# =========================
# 8) Show result
# =========================
if prediction == 1:
    print("\nPrediction: PHISHING EMAIL")
else:
    print("\nPrediction: LEGITIMATE EMAIL")

print("Phishing confidence:", round(confidence * 100, 2), "%")