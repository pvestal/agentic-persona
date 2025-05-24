"""
Audio processing service for voice input/output
"""

import io
import wave
import json
import numpy as np
from typing import Optional, Dict, Any, Union, BinaryIO
from dataclasses import dataclass
import speech_recognition as sr
from gtts import gTTS
import pygame
import tempfile
from pathlib import Path


@dataclass
class AudioConfig:
    """Audio configuration settings"""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    format: str = "wav"
    language: str = "en"
    voice_speed: float = 1.0
    voice_pitch: float = 1.0


class AudioProcessor:
    """Handles audio input/output processing"""
    
    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        self.recognizer = sr.Recognizer()
        
        # Try to initialize pygame mixer, but don't fail if no audio device
        try:
            pygame.mixer.init()
        except pygame.error:
            # Running in environment without audio hardware
            import os
            os.environ['SDL_AUDIODRIVER'] = 'dummy'
            try:
                pygame.mixer.init()
            except:
                pass  # Will work in test mode only
        
        # For testing
        self._test_mode = False
        self._test_transcription = None
        self._recorded_audio = []
    
    def enable_test_mode(self, transcription: Optional[str] = None):
        """Enable test mode with optional mock transcription"""
        self._test_mode = True
        self._test_transcription = transcription
        self._recorded_audio = []
    
    def disable_test_mode(self):
        """Disable test mode"""
        self._test_mode = False
        self._test_transcription = None
        self._recorded_audio = []
    
    def record_audio(self, duration: Optional[int] = None) -> Union[sr.AudioData, bytes]:
        """Record audio from microphone or return test data"""
        if self._test_mode:
            # Generate test audio data
            test_audio = self._generate_test_audio(duration or 3)
            self._recorded_audio.append(test_audio)
            return test_audio
        
        with sr.Microphone(sample_rate=self.config.sample_rate) as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            if duration:
                audio = self.recognizer.record(source, duration=duration)
            else:
                audio = self.recognizer.listen(source)
            
            return audio
    
    def transcribe_audio(self, audio: Union[sr.AudioData, bytes]) -> Dict[str, Any]:
        """Transcribe audio to text"""
        if self._test_mode and self._test_transcription:
            return {
                "success": True,
                "text": self._test_transcription,
                "confidence": 0.95,
                "language": self.config.language
            }
        
        try:
            # Try multiple recognition engines
            text = None
            confidence = 0.0
            
            # Try Google Speech Recognition first
            try:
                text = self.recognizer.recognize_google(
                    audio, 
                    language=self._get_language_code()
                )
                confidence = 0.9  # Google doesn't provide confidence scores
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                if not self._test_mode:
                    raise e
            
            if text:
                return {
                    "success": True,
                    "text": text,
                    "confidence": confidence,
                    "language": self.config.language
                }
            else:
                return {
                    "success": False,
                    "text": "",
                    "confidence": 0.0,
                    "error": "Could not understand audio"
                }
                
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def synthesize_speech(self, text: str, output_file: Optional[str] = None) -> Union[str, bytes]:
        """Convert text to speech"""
        if self._test_mode:
            # Return mock audio data
            audio_data = self._generate_test_audio(len(text) * 0.1)  # Rough estimate
            if output_file:
                self._save_test_audio(audio_data, output_file)
                return output_file
            return audio_data
        
        # Use gTTS for text-to-speech
        tts = gTTS(text=text, lang=self.config.language, slow=False)
        
        if output_file:
            tts.save(output_file)
            return output_file
        else:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tts.save(tmp_file.name)
                return tmp_file.name
    
    def play_audio(self, audio_file: str):
        """Play audio file"""
        if self._test_mode:
            # In test mode, just track that play was called
            self._recorded_audio.append(f"PLAYED: {audio_file}")
            return
        
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        # Wait for audio to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    
    def process_voice_command(self, audio: Union[sr.AudioData, bytes]) -> Dict[str, Any]:
        """Process a voice command and return structured data"""
        # Transcribe audio
        transcription = self.transcribe_audio(audio)
        
        if not transcription["success"]:
            return {
                "success": False,
                "command": None,
                "confidence": 0.0,
                "error": transcription.get("error", "Transcription failed")
            }
        
        # Extract command intent (simplified for testing)
        text = transcription["text"].lower()
        command = self._extract_command(text)
        
        return {
            "success": True,
            "text": transcription["text"],
            "command": command,
            "confidence": transcription["confidence"],
            "language": self.config.language
        }
    
    def _extract_command(self, text: str) -> Dict[str, Any]:
        """Extract command intent from text"""
        # Simple keyword-based command extraction
        commands = {
            "send": ["send", "reply", "respond"],
            "draft": ["draft", "compose", "write"],
            "read": ["read", "show", "display"],
            "approve": ["approve", "yes", "confirm"],
            "reject": ["reject", "no", "cancel"]
        }
        
        for cmd_type, keywords in commands.items():
            if any(keyword in text for keyword in keywords):
                return {
                    "type": cmd_type,
                    "raw_text": text,
                    "parameters": self._extract_parameters(text, cmd_type)
                }
        
        return {
            "type": "unknown",
            "raw_text": text,
            "parameters": {}
        }
    
    def _extract_parameters(self, text: str, command_type: str) -> Dict[str, Any]:
        """Extract parameters from command text"""
        params = {}
        
        # Extract platform mentions
        platforms = ["email", "slack", "discord", "teams"]
        for platform in platforms:
            if platform in text:
                params["platform"] = platform
                break
        
        # Extract urgency indicators
        if any(word in text for word in ["urgent", "asap", "immediately"]):
            params["urgency"] = "high"
        elif any(word in text for word in ["later", "tomorrow", "next week"]):
            params["urgency"] = "low"
        
        return params
    
    def _generate_test_audio(self, duration: float) -> bytes:
        """Generate test audio data"""
        sample_rate = self.config.sample_rate
        samples = int(sample_rate * duration)
        
        # Generate a simple sine wave
        frequency = 440  # A4 note
        t = np.linspace(0, duration, samples)
        wave_data = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Convert to 16-bit PCM
        audio_data = (wave_data * 32767).astype(np.int16)
        
        # Create WAV format in memory
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(self.config.channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        return buffer.getvalue()
    
    def _save_test_audio(self, audio_data: bytes, filename: str):
        """Save test audio data to file"""
        with open(filename, 'wb') as f:
            f.write(audio_data)
    
    def _get_language_code(self) -> str:
        """Get language code for speech recognition"""
        lang_map = {
            "en": "en-US",
            "es": "es-ES",
            "fr": "fr-FR",
            "de": "de-DE",
            "it": "it-IT",
            "pt": "pt-BR",
            "ja": "ja-JP",
            "ko": "ko-KR",
            "zh": "zh-CN"
        }
        return lang_map.get(self.config.language, "en-US")
    
    def get_test_recordings(self) -> list:
        """Get list of test recordings (for testing)"""
        return self._recorded_audio