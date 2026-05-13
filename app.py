from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import random
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from datetime import datetime
app = Flask(__name__)
app.secret_key = "secret123"

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("quiz.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS scores(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        score INTEGER,
        total INTEGER,
        date TEXT
    )""")

    conn.commit()
    conn.close()

init_db()

# ================= QUESTIONS =================
questions = {

    # 🟢 EASY (basic awareness)
    "easy": [
        {"q": "What is a strong password?",
         "options": ["1234", "password", "Mix of chars", "name"],
         "answer": "Mix of chars"},

        {"q": "Public WiFi is?",
         "options": ["Safe", "Risky", "Fast", "Private"],
         "answer": "Risky"},

        {"q": "Antivirus does?",
         "options": ["Protects", "Deletes files", "Speeds PC", "None"],
         "answer": "Protects"},

        {"q": "OTP means?",
         "options": ["One Time Password", "Open Tool", "Online Password", "None"],
         "answer": "One Time Password"},

        {"q": "Should you share passwords?",
         "options": ["Yes", "No", "Sometimes", "Only friends"],
         "answer": "No"}
    ],

    # 🟡 MEDIUM (concept understanding)
    "medium": [
        {"q": "Phishing means?",
         "options": ["Game", "Fake message", "Virus", "Firewall"],
         "answer": "Fake message"},

        {"q": "2FA stands for?",
         "options": ["Two Factor Auth", "Fast login", "Double file", "None"],
         "answer": "Two Factor Auth"},

        {"q": "HTTPS indicates?",
         "options": ["Secure site", "Slow site", "Broken site", "None"],
         "answer": "Secure site"},

        {"q": "Firewall is used for?",
         "options": ["Security", "Gaming", "Storage", "Display"],
         "answer": "Security"},

        {"q": "Malware is?",
         "options": ["Helpful software", "Harmful software", "Game", "Tool"],
         "answer": "Harmful software"}
    ],

    # 🔴 HARD (technical level)
    "hard": [
        {"q": "SQL Injection is?",
         "options": ["Attack", "Database", "Tool", "None"],
         "answer": "Attack"},

        {"q": "XSS attack affects?",
         "options": ["Browser", "CPU", "RAM", "Disk"],
         "answer": "Browser"},

        {"q": "Brute force attack is?",
         "options": ["Guessing passwords", "Firewall", "Encryption", "Backup"],
         "answer": "Guessing passwords"},

        {"q": "Encryption is used for?",
         "options": ["Hide data", "Delete data", "Share data", "Store data"],
         "answer": "Hide data"},

        {"q": "Zero-day attack means?",
         "options": ["Known bug", "Unknown vulnerability", "Update", "Patch"],
         "answer": "Unknown vulnerability"}
    ]
}
# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("login.html")

# LOGIN
@app.route("/login", methods=["POST"])
def login():
    user = request.form["username"]
    pw = request.form["password"]

    conn = sqlite3.connect("quiz.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
    data = c.fetchone()
    conn.close()

    if data:
        session["user"] = user
        return redirect("/index")
    return "Invalid login"

# REGISTER
@app.route("/register", methods=["POST"])
def register():
    user = request.form["username"]
    pw = request.form["password"]

    conn = sqlite3.connect("quiz.db")
    c = conn.cursor()
    c.execute("INSERT INTO users(username,password) VALUES(?,?)", (user,pw))
    conn.commit()
    conn.close()

    return redirect("/")

# LEVEL PAGE
@app.route("/index")
def index():
    if "user" not in session:
        return redirect("/")
    return render_template("index.html", user=session["user"])

# GAME
@app.route("/game/<level>")
def game(level):
    if "user" not in session:
        return redirect("/")

    q = random.sample(questions[level], len(questions[level]))
    return render_template("game.html", questions=q)

# RESULT
@app.route("/result", methods=["POST"])
def result():
    score = int(request.form.get("score") or 0)
    total = int(request.form.get("total") or 0)
    user = session.get("user", "Guest")

    conn = sqlite3.connect("quiz.db")
    c = conn.cursor()
    c.execute("INSERT INTO scores(username,score,total,date) VALUES(?,?,?,?)",
              (user, score, total, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

    return render_template("result.html", score=score, total=total, name=user)

# LEADERBOARD
@app.route("/leaderboard")
def leaderboard():
    conn = sqlite3.connect("quiz.db")
    c = conn.cursor()
    c.execute("SELECT username, MAX(score) FROM scores GROUP BY username ORDER BY MAX(score) DESC")
    data = c.fetchall()
    conn.close()

    return render_template("leaderboard.html", data=data)

# CERTIFICATE
@app.route("/certificate", methods=["POST"])
def certificate():
    name = request.form.get("name", "Player")
    score = request.form.get("score", "0")

    doc = SimpleDocTemplate("certificate.pdf", pagesize=A4,
                            rightMargin=50, leftMargin=50,
                            topMargin=60, bottomMargin=40)

    styles = getSampleStyleSheet()

    # 🎯 FIXED TITLE (no overlap)
    title_style = ParagraphStyle(
        name="Title",
        alignment=TA_CENTER,
        fontSize=26,
        leading=30,  # ✅ prevents overlap
        textColor=colors.darkblue,
        spaceAfter=25
    )

    subtitle_style = ParagraphStyle(
        name="Subtitle",
        alignment=TA_CENTER,
        fontSize=16,
        textColor=colors.grey,
        spaceAfter=20
    )

    name_style = ParagraphStyle(
        name="Name",
        alignment=TA_CENTER,
        fontSize=24,
        leading=28,
        textColor=colors.black,
        spaceAfter=20
    )

    body_style = ParagraphStyle(
        name="Body",
        alignment=TA_CENTER,
        fontSize=14,
        leading=20,
        spaceAfter=15
    )

    score_style = ParagraphStyle(
        name="Score",
        alignment=TA_CENTER,
        fontSize=16,
        textColor=colors.green,
        spaceAfter=30
    )

    footer_style = ParagraphStyle(
        name="Footer",
        alignment=TA_CENTER,
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=10
    )

    content = []

    # 🏆 Proper Title (FIXED)
    content.append(Paragraph("CERTIFICATE OF ACHIEVEMENT", title_style))

    # Subtitle
    content.append(Paragraph("This certificate is proudly presented to", subtitle_style))

    # Name
    content.append(Paragraph(f"<b>{name}</b>", name_style))

    # Description
    content.append(Paragraph(
        "For successfully completing the <b>Cybersecurity Quiz</b>",
        body_style
    ))

    # Score
    content.append(Paragraph(f"Score Achieved: <b>{score}</b>", score_style))

    content.append(Spacer(1, 50))

    # ✍️ Signature Section (Perfectly aligned)
    table_data = [
        ["________________________", "________________________"],
        ["Instructor", "Authorized Signature"]
    ]

    table = Table(table_data, colWidths=[220, 220])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 25)
    ]))

    content.append(table)

    content.append(Spacer(1, 40))

    # Footer
    content.append(Paragraph("Keep Learning • Stay Secure 🔐", footer_style))

    doc.build(content)

    return send_file("certificate.pdf", as_attachment=True)
#LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# RUN
if __name__ == "__main__":
    app.run(debug=True)