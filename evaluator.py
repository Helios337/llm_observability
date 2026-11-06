import re
from llm_wrapper import LLMWrapper

class Evaluator:
    def __init__(self, judge_model='google/gemma-4-26b-a4b-it:free', db_path='llm_observability.db'):
        self.judge_model = judge_model
        self.db_path = db_path
        self.judge_llm = LLMWrapper(model=judge_model, db_path=db_path)
    
    def evaluate_with_rubric(self, prompt, response, rubric=None):
        if rubric is None:
            rubric = {
                'length': {'min': 50, 'max': 1000, 'weight': 0.3},
                'has_numbers': {'weight': 0.2},
                'has_structure': {'weight': 0.2},
                'relevance': {'keywords': [], 'weight': 0.3}
            }
        
        scores = {}
        
        # Length check
        length = len(response)
        if rubric['length']['min'] <= length <= rubric['length']['max']:
            scores['length'] = 1.0
        else:
            scores['length'] = 0.5
        
        # Has numbers check
        scores['has_numbers'] = 1.0 if re.search(r'\d', response) else 0.0
        
        # Has structure check (paragraphs, lists)
        has_paragraphs = '\n\n' in response or '\n' in response
        has_lists = '-' in response or '*' in response or '1.' in response
        scores['has_structure'] = 1.0 if (has_paragraphs or has_lists) else 0.5
        
        # Relevance check (simplified - can be enhanced)
        scores['relevance'] = 0.8  # Placeholder
        
        # Calculate weighted score
        total_score = sum(scores[k] * rubric[k]['weight'] for k in scores.keys())
        
        return {
            'score': total_score,
            'breakdown': scores,
            'method': 'rubric'
        }
    
    def evaluate_with_llm_judge(self, prompt, response):
        judge_prompt = f"""Rate the quality of this LLM response on a scale of 1-10.

Prompt: {prompt}

Response: {response}

Provide a score from 1-10 and brief feedback. Format: Score: X/10, Feedback: [your feedback]"""
        
        # Internal call: don't log to DB so judge requests don't pollute user-facing metrics.
        result = self.judge_llm.call(judge_prompt, temperature=0.3, max_tokens=200, log=False)
        
        if result:
            content = result['content']
            score_match = re.search(r'Score:\s*(\d+)/10', content)
            score = int(score_match.group(1)) / 10.0 if score_match else 0.5
            
            feedback_match = re.search(r'Feedback:\s*(.+)', content, re.DOTALL)
            feedback = feedback_match.group(1).strip() if feedback_match else content
            
            return {
                'score': score,
                'feedback': feedback,
                'method': 'llm_judge'
            }
        
        return {'score': 0.0, 'feedback': 'Evaluation failed', 'method': 'llm_judge'}
    
    def evaluate(self, prompt, response, method='both'):
        if method == 'rubric':
            return self.evaluate_with_rubric(prompt, response)
        elif method == 'llm_judge':
            return self.evaluate_with_llm_judge(prompt, response)
        else:
            rubric_result = self.evaluate_with_rubric(prompt, response)
            llm_result = self.evaluate_with_llm_judge(prompt, response)
            
            combined_score = (rubric_result['score'] + llm_result['score']) / 2
            
            return {
                'score': combined_score,
                'rubric_score': rubric_result['score'],
                'llm_judge_score': llm_result['score'],
                'feedback': llm_result.get('feedback', ''),
                'method': 'combined'
            }
