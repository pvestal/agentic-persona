# ECHO Web Audio Interface

The ECHO backend now includes a web-based audio interface that allows you to use your microphone and camera through your browser!

## How to Access

1. Make sure the backend server is running:
   ```bash
   cd echo-backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:8000/api/audio/web-demo
   ```

## Features

The web interface includes:

- **🎤 Microphone Access**: Click "Start Recording" to record audio through your browser
- **🌍 Multi-language Support**: Select from 9 different languages
- **📊 Real-time Audio Visualization**: See your audio levels as you speak
- **📝 Automatic Transcription**: Your speech is converted to text
- **🤖 AI Response**: The ECHO system processes your message and responds
- **🔊 Text-to-Speech**: Hear the AI's response

## How It Works

1. **Permission Request**: Your browser will ask for microphone permission
2. **Recording**: Click the button to start/stop recording
3. **Processing**: Audio is sent to the backend for processing
4. **Response**: You'll see the transcription and AI response

## API Endpoints

- `GET /api/audio/web-demo` - The web interface
- `POST /api/audio/process-voice-command` - Process audio commands
- `POST /api/audio/transcribe` - Transcribe audio to text
- `POST /api/audio/synthesize` - Convert text to speech
- `WebSocket /api/audio/ws/audio` - Real-time audio streaming

## Technical Details

The web interface uses:
- **Web Audio API** for audio capture and visualization
- **MediaRecorder API** for recording
- **Canvas API** for audio visualization
- **Fetch API** for server communication

The backend is currently running in test mode for demo purposes, but can be configured to use real speech recognition and text-to-speech services.

## Troubleshooting

- **No Microphone Access**: Make sure you're using HTTPS or localhost
- **No Audio**: Check browser permissions and audio settings
- **Server Errors**: Check the server logs in `server.log`

## Next Steps

- Configure real speech recognition (Google, Azure, etc.)
- Add video support for visual context
- Implement real-time streaming with WebRTC
- Add more language models and voices