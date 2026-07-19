#!/bin/bash

echo "Setting up LLM Observability Harness..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set your OpenRouter API key:"
echo "   export OPENROUTER_API_KEY='your-api-key-here'"
echo ""
echo "2. Run the test script:"
echo "   python main.py"
echo ""
echo "3. Start the dashboard:"
echo "   python dashboard.py"
echo ""
echo "4. Open http://localhost:5000 in your browser"
