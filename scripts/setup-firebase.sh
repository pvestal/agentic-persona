#!/bin/bash

# Firebase Setup Script for Agentic Persona
# This script helps set up the Firebase project

set -e

echo "🚀 Agentic Persona - Firebase Setup"
echo "===================================="

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

if ! command -v firebase &> /dev/null; then
    echo "📦 Installing Firebase CLI..."
    npm install -g firebase-tools
fi

# Login to Firebase
echo "🔐 Logging into Firebase..."
firebase login

# Initialize Firebase (if not already done)
if [ ! -f "firebase.json" ]; then
    echo "🔧 Initializing Firebase..."
    firebase init
else
    echo "✅ Firebase already initialized"
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd echo-frontend
npm install

# Build frontend
echo "🏗️ Building frontend..."
npm run build

cd ..

# Install Python dependencies for functions
echo "📦 Installing Python dependencies for Firebase Functions..."
cd firebase-functions
pip install -r requirements.txt

cd ..

# Create environment files if they don't exist
if [ ! -f "echo-frontend/.env.production" ]; then
    echo "📝 Creating frontend .env.production file..."
    cp echo-frontend/.env.example echo-frontend/.env.production
    echo "⚠️  Please edit echo-frontend/.env.production with your Firebase config"
fi

if [ ! -f "firebase-functions/.env.yaml" ]; then
    echo "📝 Creating functions .env.yaml file..."
    cp firebase-functions/.env.yaml.example firebase-functions/.env.yaml
    echo "⚠️  Please edit firebase-functions/.env.yaml with your API keys"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit echo-frontend/.env.production with your Firebase config"
echo "2. Edit firebase-functions/.env.yaml with your API keys"
echo "3. Run 'firebase deploy' to deploy everything"
echo ""
echo "For local development:"
echo "- Frontend: cd echo-frontend && npm run dev"
echo "- Functions: firebase emulators:start"
echo ""
echo "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"