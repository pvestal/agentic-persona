#!/bin/bash
# Prepare repository for local deployment

echo "🚀 Preparing for local deployment..."

# Ensure all environment examples exist
echo "📄 Creating environment templates..."

# Backend .env.example
cat > echo-backend/.env.example << 'EOF'
# COST PROTECTION - CONFIGURE THESE FIRST!
MAX_DAILY_COST=10.00
MAX_MONTHLY_COST=100.00
EMERGENCY_SHUTDOWN_COST=500.00
MAX_PER_REQUEST=1.00

# LLM Configuration
# Use 'mock' for testing (no costs), 'real' for production ($$$$)
LLM_MODE=mock
MOCK_MODE=true

# API Keys (only needed if LLM_MODE=real)
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here

# Database
DATABASE_URL=sqlite:///./app.db

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Integration Keys (optional)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# Gmail OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
EOF

# Frontend .env.example
cat > echo-frontend/.env.example << 'EOF'
# API Configuration
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws

# Feature Flags
VITE_ENABLE_COST_TRACKING=true
VITE_ENABLE_MOCK_MODE=true
EOF

# Create .gitignore updates
echo "📝 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Personal configuration
personal_config.py
personal_settings.json
vip_contacts.txt

# Cost tracking
costs/
usage_tracking.json
EMERGENCY_SHUTDOWN.flag

# Local development
*.local
.env.local
.env.production

# API keys and secrets
api_keys.json
credentials/
*.key
*.pem

# Personal data
user_data/
conversations/
learning_data/
EOF

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p echo-backend/costs
mkdir -p echo-backend/logs
mkdir -p echo-backend/data
mkdir -p credentials

# Create cost tracking template
cat > echo-backend/costs/.gitkeep << 'EOF'
# Cost tracking directory
EOF

# Final checklist
echo "✅ Environment templates created"
echo "✅ Directory structure ready"
echo "✅ .gitignore updated"

echo ""
echo "📋 FINAL CHECKLIST:"
echo "1. ⚠️  Make repository PRIVATE on GitHub"
echo "2. 📥 Pull to local machine"
echo "3. 🔧 Copy .env.example to .env and configure"
echo "4. 🧪 Test with LLM_MODE=mock first"
echo "5. 💰 Set cost limits before using real APIs"
echo ""
echo "🎯 Ready for local deployment!"
EOF