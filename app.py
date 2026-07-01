from flask import Flask, render_template
import psycopg2
import os
import time

app = Flask(__name__)

# All values come from environment variables (injected by Docker Compose via .env)
# NEVER hardcode passwords here
def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        database=os.environ.get("DB_NAME", "studentsdb"),
        user=os.environ.get("DB_USER", "admin"),
        password=os.environ.get("DB_PASSWORD", "secret")
    )

def wait_for_db(retries=10, delay=2):
    for i in range(retries):
        try:
            conn = get_db_connection()
            conn.close()
            print("✅ DB connected!")
            return True
        except Exception as e:
            print(f"⏳ Waiting for DB... {i+1}/{retries}: {e}")
            time.sleep(delay)
    return False

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            course VARCHAR(100),
            grade CHAR(2)
        );
    """)
    cur.execute("SELECT COUNT(*) FROM students;")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO students (name, course, grade) VALUES (%s, %s, %s);",
            [
                ("Sharaz Ahmed",  "Docker & DevOps",   "A+"),
                ("Ali Raza",      "Cloud Computing",   "A"),
                ("Sara Khan",     "Generative AI",     "A+"),
                ("Usman Tariq",   "Web Engineering",   "B+"),
                ("Hina Malik",    "Software Testing",  "A"),
            ]
        )
        print("🌱 Seed data inserted.")
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, course, grade FROM students ORDER BY id;")
    students = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", students=students)

if __name__ == "__main__":
    wait_for_db()
    init_db()
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
