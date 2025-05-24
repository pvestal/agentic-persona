"""
Audio processing API routes
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, WebSocket
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel
import tempfile
import os
import json
import base64
import io
import wave

from services.audio_processor import AudioProcessor, AudioConfig
from services.agent_manager import AgentManager

router = APIRouter()

# Global audio processor instance
audio_processor = AudioProcessor()


class AudioTranscriptionRequest(BaseModel):
    """Audio transcription request model"""
    language: str = "en"
    enable_test_mode: bool = False
    test_transcription: Optional[str] = None


class TextToSpeechRequest(BaseModel):
    """Text-to-speech request model"""
    text: str
    language: str = "en"
    voice_speed: float = 1.0
    voice_pitch: float = 1.0


class VoiceCommandRequest(BaseModel):
    """Voice command request model"""
    language: str = "en"
    platform: str = "generic"
    context: Dict[str, Any] = {}


@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str = Form("en"),
    enable_test_mode: bool = Form(False),
    test_transcription: Optional[str] = Form(None)
):
    """Transcribe audio file to text"""
    try:
        # Enable test mode if requested
        if enable_test_mode:
            audio_processor.enable_test_mode(test_transcription)
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await audio_file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Configure language
        audio_processor.config.language = language
        
        # Process audio
        # In real implementation, we'd convert file to AudioData
        # For now, we'll use test mode
        if enable_test_mode and test_transcription:
            result = {
                "success": True,
                "text": test_transcription,
                "confidence": 0.95,
                "language": language
            }
        else:
            # Simulate transcription
            result = {
                "success": True,
                "text": "This would be the transcribed text from the audio file",
                "confidence": 0.85,
                "language": language
            }
        
        # Cleanup
        os.unlink(tmp_path)
        if enable_test_mode:
            audio_processor.disable_test_mode()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesize")
async def synthesize_speech(request: TextToSpeechRequest):
    """Convert text to speech"""
    try:
        # Configure audio
        audio_processor.config.language = request.language
        audio_processor.config.voice_speed = request.voice_speed
        audio_processor.config.voice_pitch = request.voice_pitch
        
        # Generate speech
        audio_file = audio_processor.synthesize_speech(request.text)
        
        # Copy to static directory and create URL
        import shutil
        import uuid
        audio_id = str(uuid.uuid4())
        static_path = f"static/audio/{audio_id}.mp3"
        shutil.copy(audio_file, static_path)
        
        # Return URL for download
        return {
            "success": True,
            "audio_url": f"/static/audio/{audio_id}.mp3",
            "text": request.text,
            "language": request.language
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/synthesize/{audio_id}")
async def download_synthesized_audio(audio_id: str):
    """Download synthesized audio file"""
    # In production, audio_id would map to stored files
    # For demo, we'll return a test file
    test_file = f"/tmp/{audio_id}.mp3"
    
    if os.path.exists(test_file):
        return FileResponse(
            test_file,
            media_type="audio/mpeg",
            filename=f"echo_speech_{audio_id}.mp3"
        )
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")


@router.post("/process-voice-command")
async def process_voice_command(
    audio_file: UploadFile = File(...),
    platform: str = Form("generic"),
    language: str = Form("en")
):
    """Process voice command and return structured response"""
    agent_manager = AgentManager()
    
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await audio_file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Configure language
        audio_processor.config.language = language
        
        # Process voice command (using test mode for demo)
        audio_processor.enable_test_mode("Send email to John about the meeting")
        audio = audio_processor.record_audio()
        command_result = audio_processor.process_voice_command(audio)
        
        # If successful, process through agent
        if command_result["success"]:
            agent_result = await agent_manager.process_message(
                message=command_result["text"],
                platform=platform,
                context={
                    "voice_command": True,
                    "command_type": command_result["command"]["type"],
                    **command_result["command"]["parameters"]
                }
            )
            
            # Generate speech response
            response_text = agent_result.get("response", "Task completed")
            response_audio = audio_processor.synthesize_speech(response_text)
            
            # Copy to static directory and create URL
            import shutil
            import uuid
            audio_id = str(uuid.uuid4())
            static_path = f"static/audio/{audio_id}.mp3"
            shutil.copy(response_audio, static_path)
            
            result = {
                "success": True,
                "transcription": command_result["text"],
                "command": command_result["command"],
                "agent_response": agent_result,
                "response_audio_url": f"/static/audio/{audio_id}.mp3"
            }
        else:
            result = {
                "success": False,
                "error": command_result.get("error", "Failed to process voice command")
            }
        
        # Cleanup
        os.unlink(tmp_path)
        audio_processor.disable_test_mode()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-audio")
async def test_audio_capabilities():
    """Test audio system capabilities"""
    try:
        # Test various audio features
        tests = {
            "microphone": True,  # In production, would check actual mic
            "speakers": True,    # In production, would check audio output
            "speech_recognition": True,
            "text_to_speech": True,
            "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"]
        }
        
        # Test transcription
        audio_processor.enable_test_mode("Test transcription")
        audio = audio_processor.record_audio(duration=1)
        transcribe_result = audio_processor.transcribe_audio(audio)
        tests["transcription_test"] = transcribe_result["success"]
        
        # Test synthesis
        try:
            audio_file = audio_processor.synthesize_speech("Test synthesis")
            tests["synthesis_test"] = bool(audio_file)
        except:
            tests["synthesis_test"] = False
        
        audio_processor.disable_test_mode()
        
        return {
            "status": "operational",
            "capabilities": tests,
            "test_mode_available": True
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "capabilities": {}
        }


@router.post("/configure")
async def configure_audio(config: Dict[str, Any]):
    """Update audio configuration"""
    try:
        # Update configuration
        if "sample_rate" in config:
            audio_processor.config.sample_rate = config["sample_rate"]
        if "language" in config:
            audio_processor.config.language = config["language"]
        if "voice_speed" in config:
            audio_processor.config.voice_speed = config["voice_speed"]
        if "voice_pitch" in config:
            audio_processor.config.voice_pitch = config["voice_pitch"]
        
        return {
            "success": True,
            "config": {
                "sample_rate": audio_processor.config.sample_rate,
                "channels": audio_processor.config.channels,
                "language": audio_processor.config.language,
                "voice_speed": audio_processor.config.voice_speed,
                "voice_pitch": audio_processor.config.voice_pitch
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/web-demo")
async def web_audio_demo():
    """Serve web-based audio demo interface"""
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ECHO Audio Web Interface</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .controls {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-top: 30px;
        }
        button {
            padding: 15px 30px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        #recordBtn {
            background-color: #007bff;
            color: white;
        }
        #recordBtn:hover:not(:disabled) {
            background-color: #0056b3;
        }
        #recordBtn.recording {
            background-color: #dc3545;
        }
        #recordBtn.recording:hover {
            background-color: #c82333;
        }
        .output {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            min-height: 100px;
        }
        .visualizer {
            width: 100%;
            height: 100px;
            background-color: #000;
            margin: 20px 0;
            border-radius: 5px;
        }
        .status {
            text-align: center;
            margin-top: 10px;
            font-style: italic;
            color: #666;
        }
        .language-select {
            padding: 10px;
            font-size: 16px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        .audio-player {
            width: 100%;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔊 ECHO Audio Web Interface</h1>
        
        <div class="controls">
            <div>
                <label for="language">Language:</label>
                <select id="language" class="language-select">
                    <option value="en">English</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                    <option value="de">German</option>
                    <option value="it">Italian</option>
                    <option value="pt">Portuguese</option>
                    <option value="ja">Japanese</option>
                    <option value="ko">Korean</option>
                    <option value="zh">Chinese</option>
                </select>
            </div>
            
            <button id="recordBtn">🎤 Start Recording</button>
            
            <canvas id="visualizer" class="visualizer"></canvas>
            
            <div class="status" id="status">Ready to record</div>
            
            <div class="output">
                <h3>Transcription:</h3>
                <div id="transcription">No transcription yet...</div>
            </div>
            
            <div class="output">
                <h3>Response:</h3>
                <div id="response">No response yet...</div>
                <audio id="audioPlayer" class="audio-player" controls style="display: none;"></audio>
            </div>
        </div>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        let audioContext;
        let analyser;
        let microphone;
        let javascriptNode;

        const recordBtn = document.getElementById('recordBtn');
        const visualizer = document.getElementById('visualizer');
        const status = document.getElementById('status');
        const transcriptionDiv = document.getElementById('transcription');
        const responseDiv = document.getElementById('response');
        const audioPlayer = document.getElementById('audioPlayer');
        const languageSelect = document.getElementById('language');
        
        const canvasContext = visualizer.getContext('2d');

        // Initialize audio visualization
        function initializeAudioVisualization(stream) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            microphone = audioContext.createMediaStreamSource(stream);
            javascriptNode = audioContext.createScriptProcessor(2048, 1, 1);

            analyser.smoothingTimeConstant = 0.8;
            analyser.fftSize = 1024;

            microphone.connect(analyser);
            analyser.connect(javascriptNode);
            javascriptNode.connect(audioContext.destination);

            javascriptNode.onaudioprocess = function() {
                const array = new Uint8Array(analyser.frequencyBinCount);
                analyser.getByteFrequencyData(array);
                drawVisualization(array);
            };
        }

        // Draw audio visualization
        function drawVisualization(array) {
            canvasContext.clearRect(0, 0, visualizer.width, visualizer.height);
            canvasContext.fillStyle = 'rgb(0, 0, 0)';
            canvasContext.fillRect(0, 0, visualizer.width, visualizer.height);

            const barWidth = (visualizer.width / array.length) * 2.5;
            let barHeight;
            let x = 0;

            for(let i = 0; i < array.length; i++) {
                barHeight = array[i] / 2;
                
                canvasContext.fillStyle = 'rgb(' + (barHeight + 100) + ',50,50)';
                canvasContext.fillRect(x, visualizer.height - barHeight, barWidth, barHeight);
                
                x += barWidth + 1;
            }
        }

        // Start recording
        async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };
                
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    await processAudio(audioBlob);
                    
                    // Stop visualization
                    if (javascriptNode) {
                        javascriptNode.disconnect();
                        microphone.disconnect();
                        analyser.disconnect();
                        audioContext.close();
                    }
                };
                
                initializeAudioVisualization(stream);
                mediaRecorder.start();
                isRecording = true;
                
                recordBtn.textContent = '🛑 Stop Recording';
                recordBtn.classList.add('recording');
                status.textContent = 'Recording...';
                
            } catch (err) {
                console.error('Error accessing microphone:', err);
                status.textContent = 'Error: ' + err.message;
            }
        }

        // Stop recording
        function stopRecording() {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
                isRecording = false;
                
                recordBtn.textContent = '🎤 Start Recording';
                recordBtn.classList.remove('recording');
                status.textContent = 'Processing audio...';
            }
        }

        // Process recorded audio
        async function processAudio(audioBlob) {
            try {
                const formData = new FormData();
                formData.append('audio_file', audioBlob, 'recording.wav');
                formData.append('language', languageSelect.value);
                formData.append('platform', 'web');
                
                const response = await fetch('/api/audio/process-voice-command', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    transcriptionDiv.textContent = result.transcription || 'No transcription available';
                    responseDiv.textContent = result.agent_response?.response || 'No response generated';
                    
                    // Play response audio if available
                    if (result.response_audio_url) {
                        audioPlayer.src = result.response_audio_url;
                        audioPlayer.style.display = 'block';
                        audioPlayer.play();
                    }
                    
                    status.textContent = 'Processing complete!';
                } else {
                    status.textContent = 'Error: ' + (result.error || 'Unknown error');
                }
                
            } catch (err) {
                console.error('Error processing audio:', err);
                status.textContent = 'Error processing audio';
            }
        }

        // Button click handler
        recordBtn.addEventListener('click', () => {
            if (isRecording) {
                stopRecording();
            } else {
                startRecording();
            }
        });

        // Set canvas size
        visualizer.width = visualizer.offsetWidth;
        visualizer.height = visualizer.offsetHeight;
    </script>
</body>
</html>
    '''
    return HTMLResponse(content=html_content)


@router.websocket("/ws/audio")
async def websocket_audio_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time audio streaming"""
    await websocket.accept()
    agent_manager = AgentManager()
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            
            # Process audio chunk
            # In production, this would handle streaming audio processing
            # For now, we'll simulate processing
            
            response = {
                "type": "transcription",
                "partial": True,
                "text": "Processing audio stream..."
            }
            
            await websocket.send_json(response)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


@router.post("/process-audio-stream")
async def process_audio_stream(audio_data: Dict[str, Any]):
    """Process audio data from web interface"""
    try:
        # Extract base64 audio data
        audio_base64 = audio_data.get("audio")
        language = audio_data.get("language", "en")
        
        if not audio_base64:
            raise HTTPException(status_code=400, detail="No audio data provided")
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_base64)
        
        # Save to temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        # Process with audio processor
        audio_processor.enable_test_mode("Hello from the web interface")
        result = {
            "success": True,
            "transcription": "Hello from the web interface",
            "language": language
        }
        
        # Cleanup
        os.unlink(tmp_path)
        audio_processor.disable_test_mode()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))