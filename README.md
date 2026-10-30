# AI-Powered Email Phishing Detection System Using Machine Learning, Deep Learning, and Flask API

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd phishing_detector
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
```
Edit `.env` file with your configuration (optional - defaults will work for development)

4. **Run the application**
```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

### Training Models (Optional)

The models are already trained and included in the `models/` directory. If you want to retrain:

```bash
# Train Machine Learning model
python train_ml.py

# Train Deep Learning model
python train_dl.py
```

### API Usage

**Web Interface:** Open http://127.0.0.1:5000 in your browser

**REST API Endpoint:** POST to http://127.0.0.1:5000/api/predict

Example API request:
```bash
curl -X POST http://127.0.0.1:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Urgent Account Verification",
    "sender": "support@fakebank.com",
    "email_text": "Your account will be suspended. Click here to verify.",
    "has_link": 1,
    "has_attachment": 0,
    "urgency_flag": 1
  }'
```

**Health Check:** GET http://127.0.0.1:5000/health

---

## 1. Project Overview
The **AI-Powered Email Phishing Detection System** is a Python-based cybersecurity project designed to detect phishing emails using **Machine Learning**, **Deep Learning**, and **Zero Trust risk analysis**.  

The system analyzes multiple email attributes such as:
- **Email subject**
- **Sender email**
- **Email content / body**
- **Presence of suspicious links**
- **Presence of attachments**
- **Urgency indicators**

Based on these features, the system classifies an email as **Phishing** or **Legitimate**. It also generates a **confidence score** and performs **Zero Trust security analysis** to assign a risk score and verdict such as **Low**, **Medium**, **High**, or **Critical**.

The project also provides:
- A **Flask-based web application**
- A **REST API endpoint**
- A **local SQLite database** to store analyzed email logs

---

## 2. Problem Statement
Email phishing is one of the most common and dangerous cyber threats. Attackers send fake emails that look like trusted messages in order to steal passwords, banking details, or personal information.

Traditional spam filters often depend on fixed rules and may fail to detect modern phishing attacks. This project solves the problem by using **Machine Learning and Deep Learning models** to intelligently analyze email text and metadata, improving phishing detection accuracy and supporting real-time cybersecurity analysis.

---

## 3. Objectives
The main objectives of this project are:

1. Build an **AI-powered phishing email detector** that classifies emails as **Phishing** or **Legitimate**.
2. Create a **data preprocessing pipeline** for email text cleaning and feature extraction.
3. Implement and compare **Machine Learning** and **Deep Learning** models.
4. Generate **prediction confidence scores** for email classification.
5. Apply **Zero Trust security principles** to evaluate email risk using sender trust, suspicious keywords, links, attachments, and urgency indicators.
6. Develop a **Flask-based web application** for real-time phishing analysis.
7. Provide a **REST API** for future integration with external systems such as Gmail or enterprise security tools.
8. Store analyzed email records in a **local database** for logging and future monitoring.

---

## 4. Key Features
- Detects **Phishing** and **Legitimate** emails
- Uses **Machine Learning (Logistic Regression)** for phishing classification
- Uses **Deep Learning (TensorFlow/Keras)** for additional phishing detection
- Combines **AI prediction + Zero Trust risk analysis**
- Shows **confidence percentage**
- Assigns **risk score** and **risk level**
- Displays **risk reasons** such as:
  - suspicious sender
  - suspicious keywords
  - urgency indicators
  - links and attachments
- Provides a **Flask web interface**
- Provides a **REST API endpoint**
- Saves results in a **SQLite database**

---

## 5. Project Architecture
The project is divided into the following layers:

### 5.1 Presentation Layer
A **Flask web interface** where the user enters:
- email subject
- sender email
- email body
- link information
- attachment information
- urgency flag

The result is displayed directly in the browser.

### 5.2 Processing Layer
This layer performs:
- text cleaning
- lowercase conversion
- punctuation removal
- whitespace cleanup
- feature engineering

### 5.3 Intelligence Layer
This layer contains:
- **Machine Learning model**
- **Deep Learning model**

The ML model uses **TF-IDF + metadata features** for classification.  
The DL model uses **tokenized padded sequences** for email text learning.

### 5.4 Zero Trust Security Layer
This layer checks:
- whether sender is trusted
- whether suspicious phishing keywords are present
- whether the email contains a link
- whether the email contains an attachment
- whether urgency indicators are present
- whether ML and DL confidence scores are high

It then generates:
- **risk score**
- **risk level**
- **Zero Trust verdict**

### 5.5 Data Storage Layer
A **SQLite database** stores all analyzed email logs for future use and record keeping.

---

## 6. Technologies Used
### Programming Language
- Python 3.x

### Machine Learning / Deep Learning
- Scikit-learn
- TensorFlow
- Keras

### Data Processing
- Pandas
- NumPy
- SciPy
- Joblib

### Data Visualization
- Matplotlib
- Seaborn
- Plotly

### Web Framework
- Flask

### File Handling
- OpenPyXL

### Database
- SQLite

### Development Environment
- Jupyter Notebook
- Visual Studio Code (VS Code)

---

## 7. Configuration

The application uses environment variables for configuration. Create a `.env` file based on `.env.example`:

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions | `dev-secret-key-change-in-production` |
| `DEBUG` | Enable debug mode | `True` |
| `HOST` | Server host address | `127.0.0.1` |
| `PORT` | Server port | `5000` |
| `DB_NAME` | Database filename | `email_logs.db` |
| `DB_PATH` | Database directory | `database` |
| `MODELS_DIR` | Models directory | `models` |
| `DATASET_DIR` | Dataset directory | `dataset` |
| `ML_CONFIDENCE_THRESHOLD` | ML confidence threshold for risk scoring | `80` |
| `DL_CONFIDENCE_THRESHOLD` | DL confidence threshold for risk scoring | `70` |

---

## 8. Project Structure
```bash
zero_trust_Email_phishing_detector/
│
├── dataset/
│   └── phishing_dataset.xlsx
│
├── models/
│   ├── ml_model.pkl
│   ├── tfidf_vectorizer.pkl
│   ├── dl_model.keras
│   └── tokenizer.pkl
│
├── database/
│   └── email_logs.db
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
├── notebooks/
│   └── email_phishing_model.ipynb
│
├── app.py              # Flask application
├── predict.py          # Prediction logic
├── zero_trust.py       # Zero Trust risk analysis
├── db.py               # Database operations
├── config.py           # Configuration management
├── train_ml.py         # ML model training script
├── train_dl.py         # DL model training script
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── README.md           # This file
└── .gitignore          # Git ignore rules