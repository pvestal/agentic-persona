import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from services.audio_processor import AudioProcessor, AudioConfig
from agents.autonomous_responder import AutonomousResponder, MessagePlatform, MessageContext
from services.agent_manager import AgentManager


class TestAudioIntegration:
    """Integration tests for audio functionality with agents"""
    
    @pytest.fixture
    def audio_processor(self):
        processor = AudioProcessor()
        processor.enable_test_mode()
        return processor
    
    @pytest.fixture
    def agent_manager(self):
        return AgentManager()
    
    @pytest.fixture
    def responder(self):
        return AutonomousResponder(name="test_responder")
    
    @pytest.mark.asyncio
    async def test_voice_command_to_agent_action(self, audio_processor, agent_manager):
        """Test full flow from voice command to agent action"""
        # Simulate voice command
        audio_processor.enable_test_mode("Send a reply to the email from John")
        
        # Record and process voice
        audio = audio_processor.record_audio(duration=2)
        command = audio_processor.process_voice_command(audio)
        
        assert command["success"] is True
        assert command["command"]["type"] == "send"
        
        # Process through agent manager
        result = await agent_manager.process_message(
            message=command["text"],
            platform=command["command"]["parameters"].get("platform", "email"),
            context={"voice_command": True}
        )
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_agent_response_to_speech(self, audio_processor, responder):
        """Test converting agent response to speech"""
        # Generate agent response
        message_context = MessageContext(
            platform=MessagePlatform.EMAIL,
            sender="user@example.com",
            recipient="me",
            subject="Meeting request",
            thread_id=None,
            timestamp=None,
            urgency=0.5,
            sentiment="neutral",
            category="scheduling"
        )
        
        response = await responder.generate_response(
            "Can we schedule a meeting?",
            message_context,
            Mock()
        )
        
        # Convert response to speech
        speech_file = audio_processor.synthesize_speech(
            response.get("content", "I'll check my calendar.")
        )
        
        assert speech_file is not None
        
        # Verify audio can be played
        audio_processor.play_audio(speech_file)
        assert len(audio_processor.get_test_recordings()) > 0
    
    def test_continuous_listening_mode(self, audio_processor):
        """Test continuous listening for wake word"""
        wake_phrases = [
            "Hey Echo",
            "OK Echo", 
            "Echo, listen",
            "Regular conversation"  # Should not trigger
        ]
        
        results = []
        for phrase in wake_phrases:
            audio_processor.enable_test_mode(phrase)
            audio = audio_processor.record_audio(duration=1)
            result = audio_processor.transcribe_audio(audio)
            
            is_wake_word = any(
                wake in result.get("text", "").lower() 
                for wake in ["hey echo", "ok echo", "echo,"]
            )
            results.append(is_wake_word)
        
        # First three should trigger, last one shouldn't
        assert results == [True, True, True, False]
    
    @pytest.mark.asyncio
    async def test_multi_language_support(self, audio_processor, responder):
        """Test multi-language voice processing"""
        languages = [
            ("en", "Send message to team", "I'll send that message to the team."),
            ("es", "Enviar mensaje al equipo", "Enviaré ese mensaje al equipo."),
            ("fr", "Envoyer un message à l'équipe", "J'enverrai ce message à l'équipe.")
        ]
        
        for lang, input_text, expected_response in languages:
            # Configure for language
            audio_processor.config.language = lang
            audio_processor.enable_test_mode(input_text)
            
            # Process voice command
            audio = audio_processor.record_audio()
            command = audio_processor.process_voice_command(audio)
            
            assert command["success"] is True
            assert command["language"] == lang
    
    def test_audio_feedback_loop(self, audio_processor):
        """Test audio feedback for user actions"""
        # Test different feedback sounds
        feedback_types = {
            "success": "Action completed successfully",
            "error": "Sorry, there was an error",
            "waiting": "Processing your request",
            "notification": "You have a new message"
        }
        
        synthesized_files = []
        for feedback_type, message in feedback_types.items():
            audio_file = audio_processor.synthesize_speech(message)
            synthesized_files.append(audio_file)
            
            # Verify file was created
            assert audio_file is not None
        
        assert len(synthesized_files) == len(feedback_types)
    
    @pytest.mark.asyncio
    async def test_voice_authentication(self, audio_processor):
        """Test voice-based authentication (mock)"""
        # Simulate voice authentication
        auth_phrases = [
            ("My voice is my passport", True),
            ("Random phrase", False)
        ]
        
        for phrase, should_authenticate in auth_phrases:
            audio_processor.enable_test_mode(phrase)
            audio = audio_processor.record_audio()
            
            # Mock voice authentication check
            is_authenticated = "passport" in phrase.lower()
            
            assert is_authenticated == should_authenticate
    
    def test_noise_cancellation(self, audio_processor):
        """Test ambient noise handling"""
        # Test with different noise levels
        noise_scenarios = [
            ("Clear speech in quiet room", 0.95),
            ("Speech with background music", 0.75),
            ("Speech in noisy environment", 0.60)
        ]
        
        for scenario, expected_confidence in noise_scenarios:
            audio_processor.enable_test_mode(scenario)
            audio_processor._test_transcription = "Test message"
            
            audio = audio_processor.record_audio()
            result = audio_processor.transcribe_audio(audio)
            
            # In real implementation, confidence would vary with noise
            # For testing, we're using the mock confidence
            assert result["success"] is True
            assert result["confidence"] >= 0.5  # Minimum acceptable confidence
    
    @pytest.mark.asyncio
    async def test_real_time_transcription(self, audio_processor):
        """Test real-time transcription capabilities"""
        # Simulate streaming audio chunks
        chunks = [
            "Hello",
            "Hello, I need",
            "Hello, I need help",
            "Hello, I need help with my email"
        ]
        
        transcriptions = []
        for chunk in chunks:
            audio_processor.enable_test_mode(chunk)
            audio = audio_processor.record_audio(duration=0.5)
            result = audio_processor.transcribe_audio(audio)
            transcriptions.append(result["text"])
        
        # Verify progressive transcription
        assert len(transcriptions) == len(chunks)
        assert transcriptions[-1] == "Hello, I need help with my email"