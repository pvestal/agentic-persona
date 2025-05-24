# Local Setup Guide (Raspberry Pi)

## Prerequisites
- Raspberry Pi 4 (8GB RAM recommended)
- Python 3.11+
- Node.js 18+
- Git

## Quick Setup

### 1. Clone Repository
```bash
# On your Pi
cd ~
git clone https://github.com/pvestal/agentic-persona.git
cd agentic-persona
```

### 2. Backend Setup
```bash
cd echo-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys (or use MOCK mode)
```

### 3. Frontend Setup
```bash
cd ../echo-frontend
npm install
npm run build  # For production
# OR
npm run dev   # For development
```

### 4. Firebase Functions (Optional)
```bash
cd ../firebase-functions
pip install -r requirements.txt
```

## Environment Variables (IMPORTANT!)

Create `.env` in echo-backend:
```bash
# COST PROTECTION - SET THESE FIRST!
MAX_DAILY_COST=10.00
MAX_MONTHLY_COST=100.00
EMERGENCY_SHUTDOWN_COST=500.00

# For testing without costs
LLM_MODE=mock
MOCK_MODE=true

# When ready for real usage (EXPENSIVE!)
# LLM_MODE=real
# OPENAI_API_KEY=your-key
# ANTHROPIC_API_KEY=your-key
```

## Running Locally

### Development Mode (SAFE - No API costs)
```bash
# Terminal 1 - Backend
cd echo-backend
source venv/bin/activate
export LLM_MODE=mock
python main.py

# Terminal 2 - Frontend
cd echo-frontend
npm run dev
```

### Production Mode (EXPENSIVE!)
```bash
# Only after setting cost limits!
export LLM_MODE=real
python main.py
```

## Cost Monitoring

Always check costs:
```bash
# View current spending
cat echo-backend/costs/usage_tracking.json

# Emergency shutdown if needed
python emergency_shutdown.py
```

## Free Local Alternative

For 100% free operation on Pi:
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download a model
ollama pull llama2

# Use local mode (to be implemented)
export LLM_MODE=local
```

## Systemd Service (Optional)

Create `/etc/systemd/system/echo-backend.service`:
```ini
[Unit]
Description=ECHO Backend
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/agentic-persona/echo-backend
Environment="PATH=/home/pi/agentic-persona/echo-backend/venv/bin"
Environment="LLM_MODE=mock"
Environment="MAX_DAILY_COST=10.00"
ExecStart=/home/pi/agentic-persona/echo-backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable echo-backend
sudo systemctl start echo-backend
```

## Security Notes

1. **NEVER** expose to internet without auth
2. **ALWAYS** use cost limits
3. **MONITOR** daily spending
4. **USE** mock mode for development
5. **KEEP** repository private

## Troubleshooting

### High CPU on Pi
- Use `LLM_MODE=mock`
- Reduce concurrent workers
- Consider Pi 5 or cloud deployment

### Out of Memory
- Increase swap:
  ```bash
  sudo dphys-swapfile swapoff
  sudo nano /etc/dphys-swapfile
  # Set CONF_SWAPSIZE=2048
  sudo dphys-swapfile setup
  sudo dphys-swapfile swapon
  ```

### API Errors
- Check `.env` file
- Verify API keys
- Check cost limits haven't been hit

## Next Steps

1. Make repository private on GitHub
2. Set up local environment
3. Test in mock mode first
4. Monitor costs carefully
5. Consider Ollama for free operation