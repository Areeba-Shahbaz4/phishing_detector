from flask import Flask, render_template, request, jsonify
from predict import predict_email
from zero_trust import zero_trust_analysis
from db import create_tables, insert_email_log
from config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Create DB tables when app starts
create_tables()


# =========================
# HOME PAGE
# =========================
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# =========================
# HEALTH CHECK
# =========================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "phishing-detector"
    })


# =========================
# WEB FORM PREDICTION
# =========================
@app.route("/predict", methods=["POST"])
def predict():
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    def respond_error(message, status=400):
        if is_ajax:
            return jsonify({"status": "error", "message": message}), status
        return render_template("index.html", error=message), status

    try:
        # Get form data
        subject = request.form.get("subject", "").strip()
        sender = request.form.get("sender", "").strip()
        email_text = request.form.get("email_text", "").strip()
        has_link = int(request.form.get("has_link", 0))
        has_attachment = int(request.form.get("has_attachment", 0))
        urgency_flag = int(request.form.get("urgency_flag", 0))

        # Input validation
        if not subject and not email_text:
            return respond_error("Please provide at least an email subject or content.")

        if sender and "@" not in sender:
            return respond_error("Please provide a valid email address.")

        if has_link not in [0, 1] or has_attachment not in [0, 1] or urgency_flag not in [0, 1]:
            return respond_error("Invalid checkbox values.")

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

        # Show result on same page (AJAX gets only the result fragment)
        if is_ajax:
            return jsonify({
                "status": "success",
                "html": render_template(
                    "_result.html",
                    prediction=prediction_result,
                    zero_trust=zero_trust_result
                )
            })

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
        if is_ajax:
            return jsonify({"status": "error", "message": str(e)}), 500
        return render_template("index.html", error=str(e)), 500


# =========================
# REST API PREDICTION
# =========================
@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400

        subject = data.get("subject", "").strip()
        sender = data.get("sender", "").strip()
        email_text = data.get("email_text", "").strip()
        has_link = int(data.get("has_link", 0))
        has_attachment = int(data.get("has_attachment", 0))
        urgency_flag = int(data.get("urgency_flag", 0))

        # Input validation
        if not subject and not email_text:
            return jsonify({
                "status": "error",
                "message": "Please provide at least an email subject or content."
            }), 400

        if sender and "@" not in sender:
            return jsonify({
                "status": "error",
                "message": "Please provide a valid email address."
            }), 400

        if has_link not in [0, 1] or has_attachment not in [0, 1] or urgency_flag not in [0, 1]:
            return jsonify({
                "status": "error",
                "message": "Invalid checkbox values. Must be 0 or 1."
            }), 400

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


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)