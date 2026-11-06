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
        'total_calls': metrics['total_calls'],
        'avg_latency': round(metrics['avg_latency'], 3) if metrics['avg_latency'] else 0,
        'total_cost': round(metrics['total_cost'], 6) if metrics['total_cost'] else 0,
        'avg_eval_score': round(metrics['avg_eval_score'], 2) if metrics['avg_eval_score'] else 0
    })

@app.route('/api/recent-calls')
def get_recent_calls():
    calls = []
    for call in db.get_recent_calls(50):
        prompt = call['prompt']
        response = call['response']
        calls.append({
            'id': call['id'],
            'timestamp': call['timestamp'],
            'model': call['model'],
            'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            'response': response[:100] + '...' if len(response) > 100 else response,
            'latency': round(call['latency'], 3),
            'cost': round(call['cost'], 6),
            'tokens_used': call['tokens_used'],
            'eval_score': round(call['eval_score'], 2) if call['eval_score'] is not None else None
        })
    return jsonify(calls)


def _recent_calls_dataframe():
    rows = db.get_recent_calls(100)
    columns = ['id', 'timestamp', 'model', 'prompt', 'response', 'latency',
               'cost', 'tokens_used', 'eval_score', 'eval_feedback']
    df = pd.DataFrame([{c: r[c] for c in columns} for r in rows], columns=columns)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


@app.route('/api/latency-chart')
def latency_chart():
    df = _recent_calls_dataframe()
    fig = px.line(df, x='timestamp', y='latency', title='Latency Over Time')
    return jsonify(json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)))


@app.route('/api/cost-chart')
def cost_chart():
    df = _recent_calls_dataframe()
    fig = px.bar(df, x='timestamp', y='cost', title='Cost Over Time')
    return jsonify(json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)))


@app.route('/api/eval-chart')
def eval_chart():
    df = _recent_calls_dataframe()
    df = df[df['eval_score'].notna()]
    fig = px.scatter(df, x='timestamp', y='eval_score', title='Evaluation Scores Over Time')
    return jsonify(json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)))

if __name__ == '__main__':
    print(f"Dashboard running on http://localhost:{PORT}")
    app.run(debug=True, host='127.0.0.1', port=PORT)
