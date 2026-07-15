import re


# =========================
# TRUSTED DOMAINS / SENDERS
# =========================
TRUSTED_DOMAINS = {
    "gmail.com",
    "outlook.com",
    "yahoo.com",
    "company.com",
    "microsoft.com",
    "google.com"
}


# =========================
# EXTRACT DOMAIN FROM SENDER
# =========================
def extract_domain(sender):
    """
    Extract domain from sender email address.
    Example:
        support@bank.com -> bank.com
    """
    if sender is None:
        return ""

    sender = str(sender).strip().lower()

    if "@" in sender:
        return sender.split("@")[-1]

    return ""


# =========================
# CHECK IF DOMAIN IS TRUSTED
# =========================
def is_trusted_sender(sender):
    """
    Return True if sender domain is in trusted domain list.
    """
    domain = extract_domain(sender)
    return domain in TRUSTED_DOMAINS


# =========================
# SUSPICIOUS KEYWORD CHECK
# =========================
def has_suspicious_keywords(text):
    """
    Check for common phishing / urgency / scam keywords.
    """
    if text is None:
        return False

    text = str(text).lower()

    suspicious_keywords = [
        "urgent",
        "verify",
        "suspend",
        "click here",
        "update account",
        "reset password",
        "bank",
        "lottery",
        "winner",
        "limited time",
        "security alert",
        "confirm identity",
        "payment failed",
        "account blocked"
    ]

    for keyword in suspicious_keywords:
        if keyword in text:
            return True

    return False


# =========================
# ZERO TRUST RISK ENGINE
# =========================
def zero_trust_analysis(subject, sender, email_text,
                        has_link, has_attachment, urgency_flag,
                        ml_result, dl_result):
    """
    Build a Zero Trust risk score using:
    - ML/DL predictions
    - confidence
    - sender trust
    - links
    - attachments
    - urgency
    - suspicious keywords
    """

    risk_score = 0
    reasons = []

    # Combine all text for keyword inspection
    combined_text = f"{subject} {sender} {email_text}"

    # 1) ML phishing prediction
    if ml_result["label"] == 1:
        risk_score += 25
        reasons.append("ML model flagged the email as phishing.")

    # 2) DL phishing prediction
    if dl_result["label"] == 1:
        risk_score += 25
        reasons.append("DL model flagged the email as phishing.")

    # 3) High ML confidence
    if ml_result["phishing_confidence"] >= 80:
        risk_score += 10
        reasons.append("ML phishing confidence is high.")

    # 4) High DL confidence
    if dl_result["phishing_confidence"] >= 70:
        risk_score += 10
        reasons.append("DL phishing confidence is high.")

    # 5) Suspicious / unknown sender
    if not is_trusted_sender(sender):
        risk_score += 10
        reasons.append("Sender domain is not in trusted domain list.")

    # 6) Link present
    if int(has_link) == 1:
        risk_score += 5
        reasons.append("Email contains a link.")

    # 7) Attachment present
    if int(has_attachment) == 1:
        risk_score += 5
        reasons.append("Email contains an attachment.")

    # 8) Urgency flag
    if int(urgency_flag) == 1:
        risk_score += 5
        reasons.append("Urgency indicator is present.")

    # 9) Suspicious keywords in content
    if has_suspicious_keywords(combined_text):
        risk_score += 5
        reasons.append("Suspicious phishing-related keywords found in email content.")

    # Cap score at 100
    risk_score = min(risk_score, 100)

    # Final risk level
    if risk_score >= 70:
        risk_level = "Critical"
        zero_trust_verdict = "Block / Quarantine immediately"
    elif risk_score >= 50:
        risk_level = "High"
        zero_trust_verdict = "Treat as highly suspicious"
    elif risk_score >= 30:
        risk_level = "Medium"
        zero_trust_verdict = "Needs caution and manual review"
    else:
        risk_level = "Low"
        zero_trust_verdict = "Low immediate phishing risk"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "trusted_sender": is_trusted_sender(sender),
        "zero_trust_verdict": zero_trust_verdict,
        "reasons": reasons
    }