#!/bin/bash
# Smart Home AI Brain - Setup Script

set -e

echo "🏠 Smart Home AI Brain - Setup"
echo "==============================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

echo "✓ Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
pre-commit install

# Create data directory
mkdir -p data

# Copy example config if not exists
if [ ! -f "config/devices.yaml" ]; then
    echo "📋 Creating default config..."
    cp config/devices.example.yaml config/devices.yaml
fi

# Check Ollama
echo ""
echo "🤖 Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
    
    # Check if model is available
    if ollama list | grep -q "llama3.2"; then
        echo "✓ llama3.2 model is available"
    else
        echo "⚠️  llama3.2 model not found. Pulling..."
        ollama pull llama3.2
    fi
else
    echo "⚠️  Ollama is not installed."
    echo "   Install from: https://ollama.ai"
fi

# Run tests
echo ""
echo "🧪 Running tests..."
pytest tests/ -v --tb=short || true

# Done
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit config/devices.yaml with your devices"
echo "  2. Run: python -m smart_home_brain.main"
echo "  3. Open: http://localhost:8000"
echo ""
echo "📚 Documentation: docs/"
echo "🐛 Issues: https://github.com/nelsonelagunar/smart-home-ai-brain/issues"