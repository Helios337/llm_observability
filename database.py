import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_path='llm_observability.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
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
        conn.commit()
        conn.close()
    
    def log_call(self, model, prompt, response, latency, cost, tokens_used, eval_score=None, eval_feedback=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO llm_calls (timestamp, model, prompt, response, latency, cost, tokens_used, eval_score, eval_feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), model, prompt, response, latency, cost, tokens_used, eval_score, eval_feedback))
        conn.commit()
        conn.close()
    
    def get_recent_calls(self, limit=100):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM llm_calls ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def update_last_eval(self, eval_score, eval_feedback):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE llm_calls SET eval_score = ?, eval_feedback = ?
            WHERE id = (SELECT MAX(id) FROM llm_calls)
        ''', (eval_score, eval_feedback))
        conn.commit()
        conn.close()
    
    def get_metrics(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total_calls,
                AVG(latency) as avg_latency,
                SUM(cost) as total_cost,
                AVG(eval_score) as avg_eval_score
            FROM llm_calls
        ''')
        metrics = cursor.fetchone()
        conn.close()
        return metrics
