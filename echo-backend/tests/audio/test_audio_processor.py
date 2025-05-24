import pytest
import tempfile
import os
from pathlib import Path
import numpy as np
import wave

from services.audio_processor import AudioProcessor, AudioConfig


class TestAudioProcessor:
    
    @pytest.fixture
    def audio_processor(self):
        processor = AudioProcessor()
        processor.enable_test_mode()
        yield processor
        processor.disable_test_mode()
    
    @pytest.fixture
    def sample_audio_file(self):
        """Create a sample audio file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            # Generate a simple audio file
            sample_rate = 16000
            duration = 1.0
            frequency = 440
            
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
            audio_data = (audio_data * 32767).astype(np.int16)
            
            with wave.open(tmp.name, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            yield tmp.name
            
        # Cleanup
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
    
    def test_initialization(self):
        processor = AudioProcessor()
        assert processor.config.sample_rate == 16000
        assert processor.config.channels == 1
        assert processor.config.language == "en"
    
    def test_custom_config(self):
        config = AudioConfig(
            sample_rate=44100,
            channels=2,
            language="es"
        )
        processor = AudioProcessor(config)
        assert processor.config.sample_rate == 44100
        assert processor.config.channels == 2
        assert processor.config.language == "es"
    
    def test_record_audio_test_mode(self, audio_processor):
        # Record audio in test mode
        audio_data = audio_processor.record_audio(duration=2)
        
        assert isinstance(audio_data, bytes)
        assert len(audio_data) > 0
        assert len(audio_processor.get_test_recordings()) == 1
    
    def test_transcribe_audio_test_mode(self, audio_processor):
        # Set mock transcription
        audio_processor.enable_test_mode("Hello world")
        
        # Record and transcribe
        audio = audio_processor.record_audio(duration=1)
        result = audio_processor.transcribe_audio(audio)
        
        assert result["success"] is True
        assert result["text"] == "Hello world"
        assert result["confidence"] == 0.95
        assert result["language"] == "en"
    
    def test_transcribe_audio_no_mock(self, audio_processor):
        # Test without mock transcription
        audio_processor.enable_test_mode(None)
        
        audio = audio_processor.record_audio(duration=1)
        result = audio_processor.transcribe_audio(audio)
        
        # Should fail since no mock transcription provided
        assert result["success"] is False
        assert result["text"] == ""
        assert "error" in result
    
    def test_synthesize_speech(self, audio_processor):
        text = "Hello, this is a test"
        
        # Test with output file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            output_file = audio_processor.synthesize_speech(text, tmp.name)
            assert output_file == tmp.name
            assert os.path.exists(output_file)
            os.unlink(output_file)
        
        # Test without output file (returns temp file)
        temp_file = audio_processor.synthesize_speech(text)
        assert isinstance(temp_file, (str, bytes))
    
    def test_play_audio_test_mode(self, audio_processor, sample_audio_file):
        # Play audio in test mode
        audio_processor.play_audio(sample_audio_file)
        
        recordings = audio_processor.get_test_recordings()
        assert len(recordings) == 1
        assert f"PLAYED: {sample_audio_file}" in recordings
    
    def test_process_voice_command_send(self, audio_processor):
        audio_processor.enable_test_mode("Send email to John")
        
        audio = audio_processor.record_audio(duration=1)
        result = audio_processor.process_voice_command(audio)
        
        assert result["success"] is True
        assert result["text"] == "Send email to John"
        assert result["command"]["type"] == "send"
        assert result["command"]["parameters"]["platform"] == "email"
    
    def test_process_voice_command_draft(self, audio_processor):
        audio_processor.enable_test_mode("Draft a message for slack urgently")
        
        audio = audio_processor.record_audio(duration=1)
        result = audio_processor.process_voice_command(audio)
        
        assert result["success"] is True
        assert result["command"]["type"] == "draft"
        assert result["command"]["parameters"]["platform"] == "slack"
        assert result["command"]["parameters"]["urgency"] == "high"
    
    def test_process_voice_command_approve(self, audio_processor):
        audio_processor.enable_test_mode("Yes, approve that")
        
        audio = audio_processor.record_audio(duration=1)
        result = audio_processor.process_voice_command(audio)
        
        assert result["success"] is True
        assert result["command"]["type"] == "approve"
    
    def test_process_voice_command_unknown(self, audio_processor):
        audio_processor.enable_test_mode("What's the weather like?")
        
        audio = audio_processor.record_audio(duration=1)
        result = audio_processor.process_voice_command(audio)
        
        assert result["success"] is True
        assert result["command"]["type"] == "unknown"
        assert result["command"]["raw_text"] == "what's the weather like?"
    
    def test_extract_parameters_urgency(self, audio_processor):
        # Test high urgency
        params = audio_processor._extract_parameters("send this urgently", "send")
        assert params.get("urgency") == "high"
        
        # Test low urgency
        params = audio_processor._extract_parameters("reply tomorrow", "send")
        assert params.get("urgency") == "low"
        
        # Test no urgency
        params = audio_processor._extract_parameters("send message", "send")
        assert "urgency" not in params
    
    def test_language_code_mapping(self, audio_processor):
        lang_tests = [
            ("en", "en-US"),
            ("es", "es-ES"),
            ("fr", "fr-FR"),
            ("de", "de-DE"),
            ("ja", "ja-JP"),
            ("unknown", "en-US")  # Default fallback
        ]
        
        for lang, expected_code in lang_tests:
            audio_processor.config.language = lang
            assert audio_processor._get_language_code() == expected_code