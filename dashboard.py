import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, jsonify
import plotly.express as px
import plotly.utils
import pandas as pd
from database import Database
import json

# NOTE: macOS Control Center (AirPlay Receiver) claims port 5000 and returns
# 403 Forbidden for anything else. Default to 5001 to avoid that conflict.
PORT = int(os.environ.get('DASHBOARD_PORT', 5001))

app = Flask(__name__)
db = Database()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/metrics')
def get_metrics():
    metrics = db.get_metrics()
    return jsonify({
        'total_calls': metrics[0],
        'avg_latency': round(metrics[1], 3) if metrics[1] else 0,
        'total_cost': round(metrics[2], 6) if metrics[2] else 0,
        'avg_eval_score': round(metrics[3], 2) if metrics[3] else 0
    })

@app.route('/api/recent-calls')
def get_recent_calls():
    rows = db.get_recent_calls(50)
    calls = []
    for row in rows:
        calls.append({
            'id': row[0],
            'timestamp': row[1],
            'model': row[2],
            'prompt': row[3][:100] + '...' if len(row[3]) > 100 else row[3],
            'response': row[4][:100] + '...' if len(row[4]) > 100 else row[4],
            'latency': round(row[5], 3),
            'cost': round(row[6], 6),
            'tokens_used': row[7],
            'eval_score': round(row[8], 2) if row[8] else None
        })
    return jsonify(calls)

@app.route('/api/latency-chart')
def latency_chart():
    rows = db.get_recent_calls(100)
    df = pd.DataFrame(rows, columns=['id', 'timestamp', 'model', 'prompt', 'response', 'latency', 'cost', 'tokens', 'eval_score', 'eval_feedback'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    fig = px.line(df, x='timestamp', y='latency', title='Latency Over Time')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/api/cost-chart')
def cost_chart():
    rows = db.get_recent_calls(100)
    df = pd.DataFrame(rows, columns=['id', 'timestamp', 'model', 'prompt', 'response', 'latency', 'cost', 'tokens', 'eval_score', 'eval_feedback'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    fig = px.bar(df, x='timestamp', y='cost', title='Cost Over Time')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/api/eval-chart')
def eval_chart():
    rows = db.get_recent_calls(100)
    df = pd.DataFrame(rows, columns=['id', 'timestamp', 'model', 'prompt', 'response', 'latency', 'cost', 'tokens', 'eval_score', 'eval_feedback'])
    df = df[df['eval_score'].notna()]
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    fig = px.scatter(df, x='timestamp', y='eval_score', title='Evaluation Scores Over Time')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

if __name__ == '__main__':
    print(f"Dashboard running on http://localhost:{PORT}")
    app.run(debug=True, host='127.0.0.1', port=PORT)
