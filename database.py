import sqlite3
from datetime import datetime


class Database:
    """SQLite-backed storage for LLM call logs and evaluation scores."""

    def __init__(self, db_path='llm_observability.db'):
        self.db_path = db_path
        self.init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self._connect() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS llm_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    model TEXT,
                    prompt TEXT,
                    response TEXT,
                    latency REAL,
                    cost REAL,
                    tokens_used INTEGER,
                    eval_score REAL,
                    eval_feedback TEXT
                )
            ''')

    def log_call(self, model, prompt, response, latency, cost, tokens_used):
        """Record a call and return its row id so callers can attach eval data to it."""
        with self._connect() as conn:
            cursor = conn.execute('''
                INSERT INTO llm_calls (timestamp, model, prompt, response, latency, cost, tokens_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), model, prompt, response, latency, cost, tokens_used))
            return cursor.lastrowid

    def update_eval(self, call_id, eval_score, eval_feedback):
        with self._connect() as conn:
            conn.execute('''
                UPDATE llm_calls SET eval_score = ?, eval_feedback = ?
                WHERE id = ?
            ''', (eval_score, eval_feedback, call_id))

    def get_recent_calls(self, limit=100):
        with self._connect() as conn:
            rows = conn.execute('''
                SELECT * FROM llm_calls ORDER BY id DESC LIMIT ?
            ''', (limit,)).fetchall()
        return [dict(row) for row in rows]

    def get_metrics(self):
        with self._connect() as conn:
            row = conn.execute('''
                SELECT
                    COUNT(*) as total_calls,
                    AVG(latency) as avg_latency,
                    SUM(cost) as total_cost,
                    AVG(eval_score) as avg_eval_score
                FROM llm_calls
            ''').fetchone()
        return dict(row)