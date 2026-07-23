from flask import Flask, render_template, request, session, redirect, flash
import json
import os
import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash

from services.ai_service import generate_ai_analysis
from services.analyzer import analyze_code, calculate_score


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "codecoach-local-development-key"
)


# ---------------- DATABASE ----------------

def init_db():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        course TEXT,
        problem TEXT,
        code TEXT,
        score INTEGER,
        explanation TEXT,
        improvement TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()


# ---------------- HELPER ----------------

def convert_to_text(value):
    """
    Converts AI-generated lists or dictionaries into text
    before saving them in SQLite.
    """

    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, list):
        return "\n".join(
            f"• {convert_to_text(item)}"
            for item in value
        )

    if isinstance(value, dict):
        return json.dumps(
            value,
            indent=2,
            ensure_ascii=False
        )

    return str(value)


# ---------------- ROUTES ----------------

@app.route("/")
def home():

    return render_template("index.html")


# ---------------- SIGNUP ----------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if username == "" or password == "":
            flash("Username and password are required.", "error")
            return redirect("/signup")

        hashed_password = generate_password_hash(
            password
        )

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:

            cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
            """, (
                username,
                hashed_password
            ))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            flash("Username already exists.", "error")
            return redirect("/signup")

        conn.close()

        return redirect("/login")

    return render_template("signup.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, username, password
        FROM users
        WHERE username = ?
        """, (
            username,
        ))

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(
            user[2],
            password
        ):

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect("/")

        flash("Invalid username or password.", "error")
        return redirect("/login")

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ---------------- ANALYZE ----------------

@app.route("/analyze", methods=["GET", "POST"])
def analyze():

    if request.method == "GET":
        return render_template("analyze.html")

    code = request.form.get(
        "code",
        ""
    )

    course = request.form.get(
        "course",
        ""
    )

    problem = request.form.get(
        "problem",
        ""
    )

    feedback = analyze_code(
        code,
        problem,
        course
    )

    score = calculate_score(
        code,
        feedback
    )

    ai_analysis = generate_ai_analysis(
        code,
        feedback,
        course,
        problem
    )

    explanation = convert_to_text(
        ai_analysis.get(
            "explanation",
            ""
        )
    )

    learning_tips = convert_to_text(
        ai_analysis.get(
            "learning_tips",
            ""
        )
    )

    user_id = session.get("user_id")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO history
    (
        user_id,
        course,
        problem,
        code,
        score,
        explanation,
        improvement
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        course,
        problem,
        code,
        score,
        explanation,
        learning_tips
    ))

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        feedback=feedback,
        course=course,
        score=score,
        ai_analysis=ai_analysis,
        code=code
    )


# ---------------- HISTORY ----------------

@app.route("/history")
def history():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    if "user_id" in session:

        cursor.execute("""
        SELECT id, course, problem, score, created_at
        FROM history
        WHERE user_id = ?
        ORDER BY id DESC
        """, (
            session["user_id"],
        ))

    else:

        cursor.execute("""
        SELECT id, course, problem, score, created_at
        FROM history
        WHERE user_id IS NULL
        ORDER BY id DESC
        """)

    analyses = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        analyses=analyses
    )


# ---------------- HISTORY DETAIL ----------------

@app.route("/history/<int:analysis_id>")
def history_detail(analysis_id):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    if "user_id" in session:

        cursor.execute("""
        SELECT
            course,
            problem,
            code,
            score,
            explanation,
            improvement
        FROM history
        WHERE id = ? AND user_id = ?
        """, (
            analysis_id,
            session["user_id"]
        ))

    else:

        cursor.execute("""
        SELECT
            course,
            problem,
            code,
            score,
            explanation,
            improvement
        FROM history
        WHERE id = ? AND user_id IS NULL
        """, (
            analysis_id,
        ))

    analysis = cursor.fetchone()

    conn.close()

    return render_template(
        "history_detail.html",
        analysis=analysis
    )


# ---------------- START ----------------

init_db()


if __name__ == "__main__":

    app.run(debug=True)