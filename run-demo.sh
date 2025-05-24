#!/bin/bash

echo "🚀 Starting ECHO Interactive Demo"
echo "================================"

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Backend not running. Starting it now..."
    cd echo-backend
    python main.py > server.log 2>&1 &
    echo "Waiting for backend to start..."
    sleep 5
fi

# Check if frontend is running
if ! curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "⚠️  Frontend not running. Starting it now..."
    cd echo-frontend
    npm run dev > frontend.log 2>&1 &
    echo "Waiting for frontend to start..."
    sleep 5
fi

echo ""
echo "✅ Services are running!"
echo ""
echo "🌐 Access the demos at:"
echo ""
echo "1. Full Frontend Application:"
echo "   http://localhost:5173"
echo ""
echo "2. Interactive LLM Demo:"
echo "   http://localhost:8000/static/interactive-demo.html"
echo ""
echo "3. Audio Demo:"
echo "   http://localhost:8000/static/audio-demo.html"
echo ""
echo "4. Neural Brain Demo:"
echo "   http://localhost:8000/static/neural-brain-demo.html"
echo ""
echo "5. API Documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "📝 Note: Make sure you have API keys set in echo-backend/.env"
echo "   OPENAI_API_KEY=your-key-here"
echo "   or"
echo "   ANTHROPIC_API_KEY=your-key-here"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running
tail -f /dev/null