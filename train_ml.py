import pandas as pd
import numpy as np
import re 
import joblib 

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

#load dataset
df = pd.read_excel(r"C:\Users\DELL\Documents\zero_trust_Email_phishing_detector\dataset\phishing_dataset.xlsx")
print(df.head())

print("dataset shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

#missing values
print(df.isnull().sum())

# Create one final text field for the email
df["combined_text"] = (
    df["subject"].astype(str) + " " +
    df["sender"].astype(str) + " " +
    df["email_text"].astype(str)
)

df[["subject", "sender", "email_text", "combined_text"]].head()


# numeric form

df["label_num"] = df["label"].map({"phishing": 1, "legitimate": 0})

df_model = df[[
    "combined_text",
    "has_link",
    "has_attachment",
    "urgency_flag",
    "label_num"
]]

df_model.head()
df_model["label_num"].value_counts()
df["label"].value_counts()

# Text input for TF-IDF
X_text = df_model["combined_text"]

# Extra metadata / security indicators
X_meta = df_model[["has_link", "has_attachment", "urgency_flag"]]

# Target labels
y = df_model["label_num"]

print("X_text sample:")
print(X_text.head())

print("\nX_meta sample:")
print(X_meta.head())

print("\ny sample:")
print(y.head())

X_text_train, X_text_test, X_meta_train, X_meta_test, y_train, y_test = train_test_split(
    X_text,
    X_meta,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training text samples:", X_text_train.shape)
print("Testing text samples:", X_text_test.shape)

print("\nTraining metadata shape:", X_meta_train.shape)
print("Testing metadata shape:", X_meta_test.shape)

print("\nTraining labels shape:", y_train.shape)
print("Testing labels shape:", y_test.shape)

# Create TF-IDF Vectorizer
tfidf = TfidfVectorizer(stop_words="english", max_features=5000)

# Learn vocabulary from training data
X_train_tfidf = tfidf.fit_transform(X_text_train)

# Transform testing data using the same vocabulary
X_test_tfidf = tfidf.transform(X_text_test)

print("Training TF-IDF Shape:", X_train_tfidf.shape)
print("Testing TF-IDF Shape:", X_test_tfidf.shape)

#for check word
print(tfidf.get_feature_names_out())

#for check ciunr
print(len(tfidf.get_feature_names_out()))

from scipy.sparse import hstack

# Combine TF-IDF text features with metadata features
X_train_final = hstack([X_train_tfidf, X_meta_train.values])
X_test_final = hstack([X_test_tfidf, X_meta_test.values])

print("Final Training Shape:", X_train_final.shape)
print("Final Testing Shape:", X_test_final.shape)

from sklearn.linear_model import LogisticRegression

# Create and train the ML model
ml_model = LogisticRegression(max_iter=1000)
ml_model.fit(X_train_final, y_train)

print("Machine Learning model trained successfully!")

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Predict on test data
y_pred = ml_model.predict(X_test_final)

# Accuracy
acc = accuracy_score(y_test, y_pred)
print("Accuracy:", acc)

# Classification Report
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# Confusion Matrix
print("\nConfusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))

# Get prediction probabilities
y_proba = ml_model.predict_proba(X_test_final)

# Probability of phishing class (class 1)
phishing_confidence = y_proba[:, 1]

print("First 10 phishing confidence scores:")
print(phishing_confidence[:10])

# Create readable predictions
results_df = pd.DataFrame({
    "email_text": X_text_test.values,
    "actual_label": y_test.values,
    "predicted_label": y_pred,
    "phishing_confidence": phishing_confidence
})

# Convert labels into readable text
results_df["actual_label"] = results_df["actual_label"].map({1: "phishing", 0: "legitimate"})
results_df["predicted_label"] = results_df["predicted_label"].map({1: "phishing", 0: "legitimate"})

# Show first 10 results
results_df.head(10)

import joblib
import os

# Create models folder if it does not exist
os.makedirs("models", exist_ok=True)

# Save trained ML model
joblib.dump(ml_model, "models/ml_model.pkl")

# Save TF-IDF vectorizer
joblib.dump(tfidf, "models/tfidf_vectorizer.pkl")

print("ML model and TF-IDF vectorizer saved successfully!")


