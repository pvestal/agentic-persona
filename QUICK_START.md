# 🚀 ECHO Quick Start Guide

## Testing Locally (No API Keys Required)

### 1. Test the Core Features

Run the test suite to see ECHO's capabilities:

```bash
cd /workspaces/agentic-persona
python test_echo.py
```

This demonstrates:
- ✅ Style morphing (Professional, Casual, Formal, Playful, etc.)
- ✅ Multi-language support (12 languages)
- ✅ Context-aware communication
- ✅ Style analysis
- ✅ Cultural adaptation

### 2. Interactive Demo

Try the interactive demo:

```bash
python demo_echo.py
```

Choose from:
1. **Style Morphing** - Transform any text between 8 communication styles
2. **Multilingual** - See phrases in 12 languages
3. **Cultural Adaptation** - Experience culturally-aware responses

### 3. Run the Full Stack (With API Keys)

#### Backend Setup:
```bash
cd echo-backend

# Edit .env file and add your API keys:
# OPENAI_API_KEY=your_key_here
# or
# ANTHROPIC_API_KEY=your_key_here

# Run the backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup (in new terminal):
```bash
cd echo-frontend
npm install
npm run dev
```

Visit: http://localhost:5173

### 4. Test API Endpoints

The backend runs at http://localhost:8000

#### Test endpoints without API keys:
```bash
# List supported languages
curl http://localhost:8000/api/i18n/languages

# Get time-based greeting
curl http://localhost:8000/api/i18n/greeting/es

# Get available styles
curl http://localhost:8000/api/style/styles

# Get available moods
curl http://localhost:8000/api/style/moods
```

## Key Features to Try

### Style Morphing
Transform text between styles while preserving meaning:
- Professional → Casual
- Casual → Formal  
- Any style → Any mood

### Multi-Language Support
ECHO speaks 12 languages with cultural awareness:
- Adjusts formality based on cultural norms
- Time-appropriate greetings
- Maintains communication style across languages

### Autonomous Response System
(Requires API keys)
- 4 autonomy levels: Learn → Suggest → Draft → Auto-Send
- Platform-specific settings
- VIP contact handling

## Example Code

```python
# Basic style morphing
from services.style_morph_engine import StyleMorphEngine, CommunicationStyle, Mood

engine = StyleMorphEngine()
morphed = engine.morph_style(
    "hey what's up",
    CommunicationStyle.PROFESSIONAL,
    Mood.ENTHUSIASTIC
)
# Output: "Hello! How are you doing?"

# Multi-language
from services.i18n import i18n, Language

greeting = i18n.get("greeting.hello", Language.SPANISH)
# Output: "Hola"
```

## Troubleshooting

1. **Import errors**: Make sure you're in the `/workspaces/agentic-persona` directory
2. **Missing dependencies**: Run `pip install -r echo-backend/requirements.txt`
3. **Port conflicts**: Change ports in the startup commands if needed

## Next Steps

1. Add your API keys to enable full AI capabilities
2. Explore the agent system for autonomous responses
3. Try the evolution engine to see how ECHO learns
4. Customize the AI head appearance

Happy echoing! 🔊