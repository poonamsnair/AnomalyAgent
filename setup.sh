#!/bin/bash
# Simple setup script for AnomalyAgent

echo "🚀 AnomalyAgent Setup"
echo "===================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
if [[ $(echo "$python_version >= 3.11" | bc -l) -eq 1 ]]; then
    echo "✅ Python $python_version detected"
else
    echo "❌ Python 3.11+ required, found $python_version"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY environment variable not set"
    echo "   Please set it with: export OPENAI_API_KEY='your-key-here'"
else
    echo "✅ OpenAI API key configured"
fi

# Create logs directory
mkdir -p logs test_logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Set OpenAI API key: export OPENAI_API_KEY='your-key-here'" 
echo "   2. Start server: python3 run.py"
echo "   3. Test API: cd tests && python3 quick_scenario_test.py --list"
echo ""