# LLM Observability & Evaluation Harness

A Python service that wraps LLM calls, logs prompts/responses, measures latency and cost, scores output quality, and provides an interactive dashboard for monitoring.

## Features

- **LLM Call Wrapper**: Intercepts all LLM calls via OpenRouter API
- **Metrics Collection**: Tracks latency, cost, and token usage
- **Quality Evaluation**: Both rule-based rubrics and LLM-as-judge evaluation
- **Interactive Dashboard**: Real-time visualization of metrics and trends
- **Regression Detection**: Monitor quality scores over time
- **SQLite Storage**: Lightweight, zero-config database

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your OpenRouter API key:
```bash
export OPENROUTER_API_KEY='your-api-key-here'
```

3. Run the test script:
```bash
python main.py
```

4. Start the dashboard:
```bash
python dashboard.py
```

5. Open http://localhost:5000 in your browser

## Usage

### Basic LLM Call with Observability

```python
from llm_wrapper import LLMWrapper

wrapper = LLMWrapper(model='openai/gpt-3.5-turbo')
result = wrapper.call("Your prompt here")

print(f"Response: {result['content']}")
print(f"Latency: {result['latency']}s")
print(f"Cost: ${result['cost']}")
```

### Evaluation

```python
from evaluator import Evaluator

evaluator = Evaluator()

# Rule-based evaluation
rubric_result = evaluator.evaluate_with_rubric(prompt, response)

# LLM-as-judge evaluation
judge_result = evaluator.evaluate_with_llm_judge(prompt, response)

# Combined evaluation
combined = evaluator.evaluate(prompt, response, method='both')
```

### Dashboard

The dashboard provides:
- Total calls, average latency, total cost, average eval score
- Latency trends over time
- Cost tracking
- Evaluation score trends
- Recent calls table

## Using Free Models

To use free models from OpenRouter, specify the model name:

```python
wrapper = LLMWrapper(model='meta-llama/llama-3-8b-instruct:free')
```

Popular free models:
- `meta-llama/llama-3-8b-instruct:free`
- `mistralai/mistral-7b-instruct:free`
- `google/gemma-7b-it:free`

## Database Schema

The SQLite database stores:
- Timestamp
- Model used
- Prompt
- Response
- Latency (seconds)
- Cost (USD)
- Tokens used
- Evaluation score
- Evaluation feedback

## Project Structure

```
llm_observability/
├── main.py              # Test script and demo
├── llm_wrapper.py       # LLM call wrapper with logging
├── evaluator.py         # Quality evaluation (rubric + LLM judge)
├── dashboard.py         # Flask web dashboard
├── database.py          # SQLite database handler
├── templates/
│   └── dashboard.html   # Dashboard UI
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Configuration

You can customize:
- Database path in `Database(db_path='your.db')`
- Model selection in `LLMWrapper(model='your-model')`
- Evaluation rubrics in `Evaluator`
- Dashboard port in `dashboard.py`

## Cost Calculation

Free models have $0 cost. For paid models, update the `_calculate_cost()` method in `llm_wrapper.py` with actual pricing from OpenRouter.

## License

MIT
