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

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

#Tokenizer settings
max_words = 5000
max_len = 200

#create tokenizer
tokenizer = Tokenizer(num_words = max_words, oov_token="<oov>" )
tokenizer.fit_on_texts(X_text_train)

# convert text into sequences
X_train_seq = tokenizer.texts_to_sequences(X_text_train)
X_test_seq = tokenizer.texts_to_sequences(X_text_test)

# pad sequences so all emails have same length
X_train_pad = pad_sequences(X_train_seq, maxlen=max_len, padding="post", truncating="post")
X_test_pad = pad_sequences(X_test_seq, maxlen=max_len, padding="post", truncating="post")

print("Training padded shape:", X_train_pad.shape)
print("Testing padded shape:", X_test_pad.shape)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense, Dropout

# Build Deep Learning model
dl_model = Sequential([
    Embedding(input_dim=max_words, output_dim=64, input_length=max_len),
    GlobalAveragePooling1D(),
    Dense(64, activation="relu"),
    Dropout(0.3),
    Dense(1, activation="sigmoid")
])
# Compile model
dl_model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# Show Model Summary
dl_model.summary()

# Train Deep Learning Model
history =dl_model.fit(
    X_train_pad,
    y_train,
    epochs=10,
    batch_size=32,
    validation_split=0.2,
    verbose=1
)

# Evaluate Deep Learning model on text set
dl_loss, dl_acc = dl_model.evaluate(X_test_pad, y_test, verbose = 0)
print("Deep Learning Test Accuracy:", dl_acc)
print("Deep Learning Test Loss:", dl_loss)

#probablity prediction from Deep Learning Model
dl_probs = dl_model.predict(X_test_pad)

# convert probabilitis into class labels
dl_pred = (dl_probs > 0.5).astype("int32").flatten()

print("First 10 DL phishing Probabilities:")
print(dl_probs[:10].flatten())

print("\nFirst 10 DL predicted labels:")
print(dl_pred[:10])

# Create Readable DL results table
dl_results_df = pd.DataFrame({
    "email_text": X_text_test.values,
    "actual_label": y_test.values,
    "dl_predicted_label": dl_pred,
    "dl_phishing_confidence":dl_probs.flatten()

})

# convert label into readable text
dl_results_df["actual_label"] = dl_results_df["actual_label"].map({1: "phishing", 0: "legitimate"})
dl_results_df["dl_predicted_label"]= dl_results_df["dl_predicted_label"].map({1: "phishing", 0: "legitimate"})

# Show first 10 rows
dl_results_df.head(10)

# Save Deep Learning Model
os.makedirs("model", exist_ok=True)
dl_model.save("models/dl_model.keras")

# Save Tokenizer 
joblib.dump (tokenizer, "models/tokenizer.pkl")
print("Deep learning model and tokenizer saved successfully")