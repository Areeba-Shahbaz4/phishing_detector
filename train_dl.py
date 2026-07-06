import pandas as pd 
import joblib 
import os

from sklearn.model_selection import train_test_split

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
# numeric form

df["label_num"] = df["label"].map({"phishing": 1, "legitimate": 0})

# Text input for TF-IDF
X_text = df["combined_text"]

# Target labels
y = df["label_num"]

print("X_text sample:")
print(X_text.head())

print("\ny sample:")
print(y.head())
#Train / test split
X_text_train, X_text_test, y_train, y_test = train_test_split(
    X_text,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training text samples:", X_text_train.shape)
print("Testing text samples:", X_text_test.shape)

print("\nTraining labels shape:", y_train.shape)
print("Testing labels shape:", y_test.shape)