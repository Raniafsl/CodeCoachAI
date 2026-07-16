from flask import Flask, render_template, request, session, redirect
import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash

from services.ai_service import generate_ai_analysis
from services.analyzer import analyze_code, calculate_score


app = Flask(__name__)
app.secret_key = "codecoach-secret-key"


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


# ---------------- ROUTES ----------------

@app.route("/")
def home():

    return render_template("index.html")


@app.route("/coach")
def coach():

    return render_template("coach.html")


# ---------------- SIGNUP ----------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if username == "" or password == "":
            return "Username and password are required."

        hashed_password = generate_password_hash(password)

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
            return "Username already exists."

        conn.close()

        return redirect("/login")

    return render_template("signup.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, username, password
        FROM users
        WHERE username = ?
        """, (username,))

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect("/")

        return "Invalid username or password."

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ---------------- ANALYZE ----------------

@app.route("/analyze", methods=["GET", "POST"])
def analyze():

    if request.method == "POST":

        code = request.form["code"]
        course = request.form["course"]
        problem = request.form.get("problem", "")

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
            ai_analysis["explanation"],
            ai_analysis["learning_tips"]
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

    return render_template("analyze.html")


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
        """, (session["user_id"],))

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

@app.route("/history/<int:id>")
def history_detail(id):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    if "user_id" in session:

        cursor.execute("""
        SELECT course, problem, code, score, explanation, improvement
        FROM history
        WHERE id = ? AND user_id = ?
        """, (
            id,
            session["user_id"]
        ))

    else:

        cursor.execute("""
        SELECT course, problem, code, score, explanation, improvement
        FROM history
        WHERE id = ? AND user_id IS NULL
        """, (id,))

    analysis = cursor.fetchone()

    conn.close()

    return render_template(
        "history_detail.html",
        analysis=analysis
    )


# ---------------- START ----------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)