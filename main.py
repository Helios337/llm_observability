from dotenv import load_dotenv
load_dotenv()

from llm_wrapper import LLMWrapper
from evaluator import Evaluator
from database import Database

def main():
    print("LLM Observability & Evaluation Harness")
    print("=" * 50)
    
    # Initialize components
    wrapper = LLMWrapper(model='google/gemma-4-26b-a4b-it:free')
    evaluator = Evaluator(judge_model='google/gemma-4-26b-a4b-it:free')
    db = Database()
    
    # Example prompts to test
    test_prompts = [
        "What is the capital of France?",
        "Explain quantum computing in simple terms.",
        "Write a haiku about programming."
    ]
    
    print("\nRunning test prompts...")
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest {i}: {prompt}")
        
        # Call LLM
        result = wrapper.call(prompt, temperature=0.7, max_tokens=500)
        
        if result:
            print(f"Response: {result['content'][:100]}...")
            print(f"Latency: {result['latency']:.3f}s")
            print(f"Cost: ${result['cost']:.6f}")
            print(f"Tokens: {result['tokens_used']}")
            
            # Evaluate response
            eval_result = evaluator.evaluate(prompt, result['content'], method='both')
            print(f"Eval Score: {eval_result['score']:.2f}")
            if 'feedback' in eval_result:
                print(f"Feedback: {eval_result['feedback']}")

            db.update_eval(result['id'], eval_result['score'], eval_result.get('feedback', ''))
        else:
            print("Failed to get response")
    
    print("\n" + "=" * 50)
    print("Test complete! Run 'python dashboard.py' to view the dashboard.")

if __name__ == '__main__':
    main()
