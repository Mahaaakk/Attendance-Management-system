from flask import Flask, render_template, request, redirect, session
from db import get_connection

app = Flask(__name__)
app.secret_key = "attendance_secret"


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_connection()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid Username or Password"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# ---------------- STUDENTS ----------------
@app.route("/students", methods=["GET", "POST"])
def students():
    if "user" not in session:
        return redirect("/")

    db = get_connection()
    cursor = db.cursor()

    if request.method == "POST":
        roll_no = request.form["roll_no"]
        name = request.form["name"]
        department = request.form["department"]
        year = request.form["year"]

        cursor.execute(
            "INSERT INTO students (roll_no, name, department, year) VALUES (%s,%s,%s,%s)",
            (roll_no, name, department, year)
        )
        db.commit()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("students.html", students=students)


# ---------------- ATTENDANCE ----------------
@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if "user" not in session:
        return redirect("/")

    db = get_connection()
    cursor = db.cursor()

    if request.method == "POST":
        date = request.form["date"]

        cursor.execute("SELECT student_id FROM students")
        all_students = cursor.fetchall()

        for s in all_students:
            status = request.form.get(f"status_{s[0]}")
            cursor.execute(
                "INSERT IGNORE INTO attendance (student_id, date, status) VALUES (%s,%s,%s)",
                (s[0], date, status)
            )

        db.commit()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("attendance.html", students=students)


# ---------------- REPORT ----------------
@app.route("/report")
def report():
    if "user" not in session:
        return redirect("/")

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        SELECT s.roll_no, s.name,
        SUM(a.status='Present') AS present_days,
        COUNT(a.id) AS total_days
        FROM students s
        LEFT JOIN attendance a ON s.student_id = a.student_id
        GROUP BY s.student_id
    """)
    data = cursor.fetchall()

    report = []
    for d in data:
        present = d[2] if d[2] is not None else 0
        total = d[3] if d[3] is not None else 0

        percent = 0
        if total > 0:
            percent = round((present / total) * 100, 2)

        report.append({
            "roll": d[0],
            "name": d[1],
            "present": present,
            "total": total,
            "percent": percent
        })

    cursor.close()
    db.close()

    return render_template("report.html", report=report)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)
