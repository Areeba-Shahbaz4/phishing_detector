from flask import Flask, render_template, request, jsonify
from predict import predict_email
from zero_trust import zero_trust_analysis
from db import create_tables, insert_email_log
from gmail_integration import fetch_latest_gmail_emails

app = Flask(__name__)

# Create DB tables when app starts
create_tables()


# =========================
# HOME PAGE
# =========================
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# =========================
# WEB FORM PREDICTION
# =========================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Get form data
        subject = request.form.get("subject", "")
        sender = request.form.get("sender", "")
        email_text = request.form.get("email_text", "")
        has_link = int(request.form.get("has_link", 0))
        has_attachment = int(request.form.get("has_attachment", 0))
        urgency_flag = int(request.form.get("urgency_flag", 0))

        # Run ML + DL prediction
        prediction_result = predict_email(
            subject=subject,
            sender=sender,
            email_text=email_text,
            has_link=has_link,
            has_attachment=has_attachment,
            urgency_flag=urgency_flag
        )

        # Run Zero Trust analysis
        zero_trust_result = zero_trust_analysis(
            subject=subject,
            sender=sender,
            email_text=email_text,
            has_link=has_link,
            has_attachment=has_attachment,
            urgency_flag=urgency_flag,
            ml_result=prediction_result["ml_result"],
            dl_result=prediction_result["dl_result"]
        )

        # Save to database
        insert_email_log(
            subject=subject,
            sender=sender,
            email_text=email_text,
            has_link=has_link,
            has_attachment=has_attachment,
            urgency_flag=urgency_flag,
            prediction_result=prediction_result,
            zero_trust_result=zero_trust_result
        )

        # Show result on same page
        return render_template(
            "index.html",
            prediction=prediction_result,
            zero_trust=zero_trust_result,
            subject=subject,
            sender=sender,
            email_text=email_text,
            has_link=has_link,
            has_attachment=has_attachment,
            urgency_flag=urgency_flag
        )

    except Exception as e:
        return render_template("index.html", error=str(e))


# =========================
# REST API PREDICTION
# =========================
@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        data = request.get_json()

        subject = data.get("subject", "")
        sender = data.get("sender", "")
        email_text = data.get("email_text", "")
        has_link = int(data.get("has_link", 0))
        has_attachment = int(data.get("has_attachment", 0))
        urgency_flag = int(data.get("urgency_flag", 0))

        # Run prediction
        prediction_result = predict_email(
            subject=subject,
            sender=sender,
            email_text=email_text,
            has_link=has_link,
            has_attachment=has_attachment,
            urgency_flag=urgency_flag
        )

        # Run Zero Trust
        zero_trust_result = zero_trust_analysis(
            subject=subject,
            sender=sender,
            email_text=email_text,
            has_link=has_link,
            has_attachment=has_attachment,
            urgency_flag=urgency_flag,
            ml_result=prediction_result["ml_result"],
            dl_result=prediction_result["dl_result"]
        )

        # Save to DB
        insert_email_log(
            subject=subject,
            sender=sender,
            email_text=email_text,
            has_link=has_link,
            has_attachment=has_attachment,
            urgency_flag=urgency_flag,
            prediction_result=prediction_result,
            zero_trust_result=zero_trust_result
        )

        return jsonify({
            "status": "success",
            "prediction": prediction_result,
            "zero_trust": zero_trust_result
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route("/gmail-demo")
def gmail_demo():

    gmail_address = "airplaneking136@gmail.com"
    app_password = "pxfr hdhv vqde nkva"

    try:
        emails = fetch_latest_gmail_emails(
            gmail_address,
            app_password,
            max_emails=5
        )

        results = []

        for email in emails:

            prediction = predict_email(
                subject=email["subject"],
                sender=email["sender"],
                email_text=email["email_text"],
                has_link=email["has_link"],
                has_attachment=email["has_attachment"],
                urgency_flag=email["urgency_flag"]
            )

            zero = zero_trust_analysis(
                subject=email["subject"],
                sender=email["sender"],
                email_text=email["email_text"],
                has_link=email["has_link"],
                has_attachment=email["has_attachment"],
                urgency_flag=email["urgency_flag"],
                ml_result=prediction["ml_result"],
                dl_result=prediction["dl_result"]
            )

            results.append({
                "subject": email["subject"],
                "sender": email["sender"],
                "prediction": prediction["final_prediction"],
                "confidence": prediction["final_confidence"],
                "risk_score": zero["risk_score"]
            })

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)})


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)