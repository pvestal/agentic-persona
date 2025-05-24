#!/bin/bash

# ECHO Development Environment Setup Script

echo "🔊 Setting up ECHO development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [[ ! "$python_version" =~ ^3\.(9|10|11|12) ]]; then
    echo "❌ Python 3.9+ required. Found: $python_version"
    exit 1
fi

# Check Node version
node_version=$(node --version 2>&1 | cut -d'v' -f2)
if [[ ! "$node_version" =~ ^(18|20|21) ]]; then
    echo "❌ Node.js 18+ required. Found: v$node_version"
    exit 1
fi

echo "✅ Prerequisites checked"

# Install pre-commit
echo "📦 Installing pre-commit..."
pip install pre-commit

# Install pre-commit hooks
echo "🔗 Installing git hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Backend setup
echo "🐍 Setting up backend..."
cd echo-backend
pip install -r requirements.txt
pip install -e .  # Install in editable mode if setup.py exists

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Database
DATABASE_URL=sqlite:///./echo.db

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Environment
ENV=development
DEBUG=true
EOF
    echo "⚠️  Please update .env with your API keys"
fi

# Frontend setup
echo "⚛️  Setting up frontend..."
cd ../echo-frontend
npm install

# Run initial tests
echo "🧪 Running initial tests..."
cd ../echo-backend
pytest tests/test_agents/test_base_agent.py -v

cd ../echo-frontend
npm test -- --run

# Create secrets baseline
echo "🔒 Creating secrets baseline..."
cd ..
detect-secrets scan > .secrets.baseline

echo "
✨ ECHO development environment setup complete!

Next steps:
1. Update echo-backend/.env with your API keys
2. Run 'cd echo-backend && uvicorn main:app --reload' to start backend
3. Run 'cd echo-frontend && npm run dev' to start frontend
4. Visit http://localhost:5173

Pre-commit hooks are now active. They will run automatically on:
- git commit (linting, formatting, tests)
- git push (full test suite)

Happy coding! 🚀
"