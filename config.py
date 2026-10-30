import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

    # Database
    DB_NAME = os.getenv('DB_NAME', 'email_logs.db')
    DB_PATH = os.getenv('DB_PATH', 'database')

    # Model paths
    MODELS_DIR = os.getenv('MODELS_DIR', 'models')
    ML_MODEL_PATH = os.path.join(MODELS_DIR, 'ml_model.pkl')
    TFIDF_VECTORIZER_PATH = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')
    DL_MODEL_PATH = os.getenv('DL_MODEL_PATH', 'models/dl_model.keras')
    TOKENIZER_PATH = os.path.join(MODELS_DIR, 'tokenizer.pkl')

    # Dataset
    DATASET_DIR = os.getenv('DATASET_DIR', 'dataset')
    DATASET_PATH = os.path.join(DATASET_DIR, 'phishing_dataset.xlsx')

    # Server
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))

    # Email analysis thresholds
    ML_CONFIDENCE_THRESHOLD = float(os.getenv('ML_CONFIDENCE_THRESHOLD', 80))
    DL_CONFIDENCE_THRESHOLD = float(os.getenv('DL_CONFIDENCE_THRESHOLD', 70))
