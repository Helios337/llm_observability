import openai
import time
import os
from database import Database


class LLMWrapper:
    def __init__(self, model='google/gemma-4-26b-a4b-it:free', db_path='llm_observability.db'):
        self.model = model
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv('OPENROUTER_API_KEY')
        )
        self.db = Database(db_path)

    def call(self, prompt, temperature=0.7, max_tokens=1000, log=True):
        """Run a chat completion and return its metadata.

        When `log` is True the call is persisted to the database and `id`
        holds the row. Internal calls (e.g. judge evaluations) pass
        `log=False` to avoid polluting user-facing metrics.
        """
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            result = {
                'content': content,
                'latency': time.time() - start_time,
                'cost': self._calculate_cost(tokens_used),
                'tokens_used': tokens_used
            }

            if log:
                result['id'] = self.db.log_call(
                    model=self.model,
                    prompt=prompt,
                    response=content,
                    latency=result['latency'],
                    cost=result['cost'],
                    tokens_used=tokens_used
                )

            return result

        except Exception as e:
            print(f"Error calling LLM: {e}")
            return None

    def _calculate_cost(self, tokens_used):
        if 'free' in self.model.lower():
            return 0.0
        return tokens_used * 0.00001