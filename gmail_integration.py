import imaplib
import email
from email.header import decode_header
import re

# ---------------------------------------------------
# GMAIL CONFIG
# ---------------------------------------------------
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993


# ---------------------------------------------------
# HELPER: decode email subject safely
# ---------------------------------------------------
def decode_mime_text(text):
    """
    Decode MIME encoded email subject/text.
    Example: =?UTF-8?...?=
    """
    if not text:
        return ""

    decoded_parts = decode_header(text)
    final_text = ""

    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            try:
                final_text += part.decode(encoding or "utf-8", errors="ignore")
            except:
                final_text += part.decode("utf-8", errors="ignore")
        else:
            final_text += str(part)

    return final_text


# ---------------------------------------------------
# HELPER: extract plain text body from email
# ---------------------------------------------------
def extract_email_body(msg):
    """
    Extract plain text body from email message.
    If multipart, loop through parts and pick text/plain.
    """
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            # Skip attachments
            if "attachment" in content_disposition.lower():
                continue

            if content_type == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    return body
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode(errors="ignore")
        except:
            body = ""

    return body


# ---------------------------------------------------
# HELPER: check if email contains link
# ---------------------------------------------------
def has_link_in_text(text):
    if not text:
        return 0

    url_pattern = r"(https?://\S+|www\.\S+)"
    return 1 if re.search(url_pattern, text, re.IGNORECASE) else 0


# ---------------------------------------------------
# HELPER: detect urgency words
# ---------------------------------------------------
def has_urgency_words(text):
    if not text:
        return 0

    urgency_keywords = [
        "urgent", "immediately", "verify", "suspended",
        "action required", "click now", "password reset",
        "security alert", "limited time", "confirm now"
    ]

    text_lower = text.lower()
    for word in urgency_keywords:
        if word in text_lower:
            return 1
    return 0


# ---------------------------------------------------
# HELPER: check if email has attachment
# ---------------------------------------------------
def has_attachment(msg):
    """
    Return 1 if email has any attachment, else 0
    """
    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition"))
        if "attachment" in content_disposition.lower():
            return 1
    return 0


# ---------------------------------------------------
# MAIN FUNCTION: fetch latest Gmail emails
# ---------------------------------------------------
def fetch_latest_gmail_emails(gmail_address, app_password, max_emails=5):
    """
    Connect to Gmail inbox using IMAP and fetch latest emails.

    Returns a list of dictionaries:
    [
        {
            "subject": "...",
            "sender": "...",
            "email_text": "...",
            "has_link": 0/1,
            "has_attachment": 0/1,
            "urgency_flag": 0/1
        }
    ]
    """

    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(gmail_address, app_password)
    mail.select("inbox")

    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()

    # Get latest emails only
    latest_email_ids = email_ids[-max_emails:]

    email_data_list = []

    for email_id in reversed(latest_email_ids):
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = decode_mime_text(msg.get("Subject"))
        sender = msg.get("From", "")
        body = extract_email_body(msg)

        link_flag = has_link_in_text(body)
        attachment_flag = has_attachment(msg)
        urgency_flag = has_urgency_words(subject + " " + body)

        email_data = {
            "subject": subject,
            "sender": sender,
            "email_text": body,
            "has_link": link_flag,
            "has_attachment": attachment_flag,
            "urgency_flag": urgency_flag
        }

        email_data_list.append(email_data)

    mail.logout()
    return email_data_list


# ---------------------------------------------------
# TEST MODE
# ---------------------------------------------------
if __name__ == "__main__":
    # IMPORTANT:
    # Replace with your Gmail and Gmail App Password
    gmail_address = "airplaneking136@gmail.com"
    app_password = "pxfr hdhv vqde nkva"

    emails = fetch_latest_gmail_emails(gmail_address, app_password, max_emails=3)

    print("Fetched Emails:\n")
    for i, item in enumerate(emails, start=1):
        print(f"Email {i}")
        print("Subject:", item["subject"])
        print("Sender:", item["sender"])
        print("Has Link:", item["has_link"])
        print("Has Attachment:", item["has_attachment"])
        print("Urgency Flag:", item["urgency_flag"])
        print("Body Preview:", item["email_text"][:200])
        print("-" * 80)