import sqlite3
from datetime import datetime

# Database file name
DB_NAME = "email_logs.db"


# =========================
# CONNECT TO DATABASE
# =========================
def get_connection():
    """
    Create and return a SQLite database connection.
    """
    conn = sqlite3.connect(DB_NAME)
    return conn


# =========================
# CREATE TABLES
# =========================
def create_tables():
    """
    Create required tables if they do not exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Main prediction log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_analysis_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            sender TEXT,
            email_text TEXT,
            has_link INTEGER,
            has_attachment INTEGER,
            urgency_flag INTEGER,

            final_prediction TEXT,
            final_confidence REAL,

            ml_label TEXT,
            ml_confidence REAL,

            dl_label TEXT,
            dl_confidence REAL,

            risk_score INTEGER,
            risk_level TEXT,
            zero_trust_verdict TEXT,
            trusted_sender INTEGER,
            reasons TEXT,

            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================
# INSERT EMAIL ANALYSIS LOG
# =========================
def insert_email_log(subject, sender, email_text,
                     has_link, has_attachment, urgency_flag,
                     prediction_result, zero_trust_result):
    """
    Insert one analyzed email record into database.
    prediction_result = output of predict_email()
    zero_trust_result = output of zero_trust_analysis()
    """
    conn = get_connection()
    cursor = conn.cursor()

    ml_result = prediction_result.get("ml_result", {})
    dl_result = prediction_result.get("dl_result", {})

    reasons_text = " | ".join(zero_trust_result.get("reasons", []))

    cursor.execute("""
        INSERT INTO email_analysis_logs (
            subject, sender, email_text,
            has_link, has_attachment, urgency_flag,

            final_prediction, final_confidence,

            ml_label, ml_confidence,
            dl_label, dl_confidence,

            risk_score, risk_level, zero_trust_verdict,
            trusted_sender, reasons, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        subject,
        sender,
        email_text,
        int(has_link),
        int(has_attachment),
        int(urgency_flag),

        prediction_result.get("final_prediction"),
        prediction_result.get("final_confidence"),

        ml_result.get("label_name"),
        ml_result.get("phishing_confidence"),

        dl_result.get("label_name"),
        dl_result.get("phishing_confidence"),

        zero_trust_result.get("risk_score"),
        zero_trust_result.get("risk_level"),
        zero_trust_result.get("zero_trust_verdict"),
        1 if zero_trust_result.get("trusted_sender") else 0,
        reasons_text,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


# =========================
# FETCH ALL LOGS
# =========================
def get_all_logs():
    """
    Return all email analysis logs, newest first.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM email_analysis_logs
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


# =========================
# FETCH RECENT LOGS LIMIT
# =========================
def get_recent_logs(limit=10):
    """
    Return recent N logs.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM email_analysis_logs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows


# =========================
# SEARCH LOGS BY PREDICTION
# =========================
def get_logs_by_prediction(prediction_label):
    """
    Fetch logs by final prediction label:
    e.g. 'phishing' or 'legitimate'
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM email_analysis_logs
        WHERE final_prediction = ?
        ORDER BY id DESC
    """, (prediction_label,))

    rows = cursor.fetchall()
    conn.close()
    return rows


# =========================
# TEST DB FILE DIRECTLY
# =========================
if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully!")