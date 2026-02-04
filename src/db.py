import sqlite3, json
from datetime import datetime

DB_PATH = "futurizar.db"

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            created_at TEXT NOT NULL,
            quiz_json TEXT NOT NULL
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            submitted_at TEXT NOT NULL,
            answers_json TEXT NOT NULL,
            score INTEGER NOT NULL,
            feedback_json TEXT NOT NULL,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
        )
        """)
        con.commit()

def save_quiz(subject: str, quiz: dict) -> int:
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO quizzes(subject, created_at, quiz_json) VALUES(?,?,?)",
            (subject, datetime.utcnow().isoformat(), json.dumps(quiz, ensure_ascii=False))
        )
        con.commit()
        return cur.lastrowid

def save_attempt(quiz_id: int, answers: dict, score: int, feedback: list) -> int:
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO attempts(quiz_id, submitted_at, answers_json, score, feedback_json) VALUES(?,?,?,?,?)",
            (quiz_id, datetime.utcnow().isoformat(),
             json.dumps(answers, ensure_ascii=False),
             score,
             json.dumps(feedback, ensure_ascii=False))
        )
        con.commit()
        return cur.lastrowid

def list_attempts(limit=20):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
        SELECT a.id, a.quiz_id, a.submitted_at, a.score, q.subject
        FROM attempts a
        JOIN quizzes q ON q.id = a.quiz_id
        ORDER BY a.id DESC
        LIMIT ?
        """, (limit,))
        return cur.fetchall()

def load_attempt(attempt_id: int):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
        SELECT a.id, a.quiz_id, a.submitted_at, a.score, a.answers_json, a.feedback_json, q.quiz_json, q.subject
        FROM attempts a
        JOIN quizzes q ON q.id = a.quiz_id
        WHERE a.id = ?
        """, (attempt_id,))
        row = cur.fetchone()
        return row
