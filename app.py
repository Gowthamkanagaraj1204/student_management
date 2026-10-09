from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "student-management-secret-key"

DATABASE = "students.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = get_db_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]
    conn.close()

    return render_template("home.html", count=count)


@app.route("/students", methods=["GET", "POST"])
def students():
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        course = request.form.get("course", "").strip()

        if not name or not email or not course:
            flash("Please fill in all student fields.", "error")
        else:
            try:
                conn.execute(
                    "INSERT INTO students (name, email, course) "
                    "VALUES (?, ?, ?)",
                    (name, email, course)
                )
                conn.commit()
                flash("Student added successfully!", "success")
            except sqlite3.IntegrityError:
                flash("This email address already exists.", "error")

        conn.close()
        return redirect(url_for("students"))

    student_list = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template(
        "students.html",
        students=student_list
    )


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if name and email and message:
            flash(
                "Thank you! Your message was received by this demo form.",
                "success"
            )
        else:
            flash("Please fill in all fields.", "error")

        return redirect(url_for("contact"))

    return render_template("contact.html")


if __name__ == "__main__":
    create_table()
    app.run(debug=True)
