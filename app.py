import os
import json
import hmac
import smtplib
from functools import wraps
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

DATA_FILE = "responses.json"


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def load_responses():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"skills": [], "nps": []}
    return {"skills": [], "nps": []}


def save_response(kind, entry):
    data = load_responses()
    entry["timestamp"] = datetime.utcnow().isoformat()
    data[kind].append(entry)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def find_review_by_email(email):
    if not email:
        return None
    email = email.strip().lower()
    for r in load_responses()["nps"]:
        if r.get("email", "").strip().lower() == email:
            return r
    return None


RED = "#D64545"
AMBER = "#F2A93B"
GREEN = "#2E9E5B"
GRAY = "#6b6b6b"


def score_tier(score):
    """Map an NPS score to a color-coded tier with a concrete action step."""
    try:
        score = int(score)
    except (TypeError, ValueError):
        return {
            "label": "No Score",
            "color": GRAY,
            "action": "No score was given — follow up with the client directly to learn more about their experience.",
        }
    if score <= 6:
        return {
            "label": "Detractor",
            "color": RED,
            "action": (
                "Reach out personally within 48 hours, acknowledge the specific concern in their "
                "comments, and offer a concrete next step to fix it."
            ),
        }
    if score <= 8:
        return {
            "label": "Passive",
            "color": AMBER,
            "action": (
                "Ask what would move them to a 9 or 10, and look for one concrete improvement "
                "you can make before their next meeting."
            ),
        }
    return {
        "label": "Promoter",
        "color": GREEN,
        "action": (
            "Keep doing what worked here, and consider asking them for a referral or testimonial."
        ),
    }


def send_review_email(entry):
    to_addr = os.environ.get("OWNER_EMAIL", "ladyem34@gmail.com")
    host = os.environ.get("SMTP_HOST")
    if not host:
        print("SMTP_HOST not configured — skipping review email send.")
        return
    port = int(os.environ.get("SMTP_PORT", 587))
    username = os.environ.get("SMTP_USERNAME")
    password = os.environ.get("SMTP_PASSWORD")
    from_addr = os.environ.get("SMTP_FROM", username or to_addr)

    tier = score_tier(entry.get("score"))
    text_body = (
        "A client just submitted a review.\n\n"
        f"Name: {entry.get('name') or 'Anonymous'}\n"
        f"Email: {entry.get('email') or 'Not provided'}\n"
        f"Score: {entry.get('score', 'N/A')}/10 [{tier['label']}]\n"
        f"Comments: {entry.get('comments') or '(none)'}\n"
        f"Submitted: {entry.get('timestamp')}\n\n"
        f"Actionable step:\n{tier['action']}\n"
    )
    html_body = f"""
    <div style="font-family: Arial, sans-serif; color: #2C2C2C; max-width: 480px;">
      <h2 style="margin-bottom:4px;">New Client Review</h2>
      <p style="margin-top:0; color:#6b6b6b;">Submitted {entry.get('timestamp')}</p>
      <p>
        <b>Name:</b> {entry.get('name') or 'Anonymous'}<br>
        <b>Email:</b> {entry.get('email') or 'Not provided'}<br>
        <b>Score:</b> {entry.get('score', 'N/A')}/10
      </p>
      <p>
        <span style="display:inline-block; background:{tier['color']}; color:white; font-weight:bold;
                     padding:6px 14px; border-radius:20px; font-size:0.85rem;">
          {tier['label'].upper()}
        </span>
      </p>
      <p><b>Comments:</b><br>{entry.get('comments') or '(none)'}</p>
      <div style="border-left: 4px solid {tier['color']}; padding: 10px 14px; background:#f7f5fb; margin-top:16px;">
        <b>Actionable step:</b><br>{tier['action']}
      </div>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    msg["Subject"] = f"New Client Review — {tier['label']} (Score: {entry.get('score', 'N/A')}/10)"
    msg["From"] = from_addr
    msg["To"] = to_addr

    try:
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.starttls()
            if username and password:
                server.login(username, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
    except Exception as e:
        print(f"Failed to send review email: {e}")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/skills", methods=["GET", "POST"])
def skills():
    if request.method == "POST":
        entry = {
            "name": request.form.get("name", ""),
            "coding": request.form.get("coding"),
            "problem_solving": request.form.get("problem_solving"),
            "ai_tools": request.form.get("ai_tools"),
            "confidence": request.form.get("confidence"),
            "comments": request.form.get("comments", ""),
        }
        save_response("skills", entry)
        return redirect(url_for("thanks"))
    return render_template("skills.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()

        if session.get("nps_submitted") or find_review_by_email(email):
            return render_template("already_reviewed.html")

        session["reviewer_name"] = name
        session["reviewer_email"] = email
        return redirect(url_for("nps"))
    return render_template("login.html")


@app.route("/nps", methods=["GET", "POST"])
def nps():
    if request.method == "POST":
        email = request.form.get("email", session.get("reviewer_email", "")).strip().lower()

        if session.get("nps_submitted") or find_review_by_email(email):
            return render_template("already_reviewed.html")

        entry = {
            "name": request.form.get("name", ""),
            "email": email,
            "score": request.form.get("score"),
            "comments": request.form.get("comments", ""),
        }
        save_response("nps", entry)
        session["nps_submitted"] = True
        send_review_email(entry)
        return redirect(url_for("thanks"))

    if session.get("nps_submitted"):
        return render_template("already_reviewed.html")
    return render_template(
        "nps.html",
        name=session.get("reviewer_name", ""),
        email=session.get("reviewer_email", ""),
    )


@app.route("/thanks")
def thanks():
    return render_template("thanks.html")


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    error = None
    next_url = request.values.get("next") or url_for("results")
    if request.method == "POST":
        admin_password = os.environ.get("ADMIN_PASSWORD")
        submitted = request.form.get("password", "")
        if admin_password and hmac.compare_digest(submitted, admin_password):
            session["is_admin"] = True
            return redirect(request.form.get("next") or url_for("results"))
        error = "Incorrect password."
    return render_template("admin_login.html", error=error, next=next_url)


@app.route("/admin-logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("home"))


@app.route("/results")
@admin_required
def results():
    data = load_responses()
    return render_template("results.html", data=data, score_tier=score_tier)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
