#!/usr/bin/env python3
"""
Interactive audio demo for ECHO system
Tests voice input/output capabilities
"""

import asyncio
import sys
from datetime import datetime
from typing import Optional

from services.audio_processor import AudioProcessor, AudioConfig
from services.agent_manager import AgentManager
from agents.autonomous_responder import MessagePlatform, MessageContext


class AudioDemo:
    """Interactive audio demonstration"""
    
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.agent_manager = AgentManager()
        
        # Initialize audio processor with test mode awareness
        if test_mode:
            # In test mode, we'll need to modify AudioProcessor to handle initialization better
            import os
            os.environ['SDL_AUDIODRIVER'] = 'dummy'  # Use dummy audio driver for testing
            
        self.audio_processor = AudioProcessor()
        
        if test_mode:
            self.audio_processor.enable_test_mode()
            print("🧪 Running in TEST MODE - using simulated audio")
        else:
            print("🎤 Running in LIVE MODE - using real microphone")
    
    async def run(self):
        """Run the interactive demo"""
        print("\n🔊 ECHO Audio Demo")
        print("=" * 50)
        
        while True:
            print("\n📋 Options:")
            print("1. Test voice command")
            print("2. Test text-to-speech")
            print("3. Test continuous listening")
            print("4. Test voice-to-agent flow")
            print("5. Test multi-language")
            print("6. Run all tests")
            print("0. Exit")
            
            choice = input("\nSelect option: ")
            
            if choice == "0":
                break
            elif choice == "1":
                await self.test_voice_command()
            elif choice == "2":
                await self.test_text_to_speech()
            elif choice == "3":
                await self.test_continuous_listening()
            elif choice == "4":
                await self.test_voice_to_agent()
            elif choice == "5":
                await self.test_multi_language()
            elif choice == "6":
                await self.run_all_tests()
            else:
                print("❌ Invalid option")
    
    async def test_voice_command(self):
        """Test voice command recognition"""
        print("\n🎤 Voice Command Test")
        print("-" * 30)
        
        if self.test_mode:
            test_commands = [
                "Send email to John about the meeting",
                "Draft a slack message for the team",
                "Read my latest messages",
                "Approve the pending response"
            ]
            
            for cmd in test_commands:
                print(f"\n📢 Simulating: '{cmd}'")
                self.audio_processor.enable_test_mode(cmd)
                
                audio = self.audio_processor.record_audio(duration=2)
                result = self.audio_processor.process_voice_command(audio)
                
                self._print_command_result(result)
        else:
            print("🎤 Say a command (e.g., 'Send email to John')...")
            print("Listening for 5 seconds...")
            
            audio = self.audio_processor.record_audio(duration=5)
            result = self.audio_processor.process_voice_command(audio)
            
            self._print_command_result(result)
    
    async def test_text_to_speech(self):
        """Test text-to-speech synthesis"""
        print("\n🔊 Text-to-Speech Test")
        print("-" * 30)
        
        test_phrases = [
            "Hello! I'm ECHO, your AI assistant.",
            "I've processed your email and drafted a response.",
            "The meeting has been scheduled for tomorrow at 2 PM.",
            "Warning: High priority message requires your attention."
        ]
        
        for phrase in test_phrases:
            print(f"\n📝 Text: '{phrase}'")
            
            audio_file = self.audio_processor.synthesize_speech(phrase)
            print(f"✅ Generated audio: {audio_file}")
            
            if not self.test_mode:
                print("🔊 Playing audio...")
                self.audio_processor.play_audio(audio_file)
                await asyncio.sleep(2)
    
    async def test_continuous_listening(self):
        """Test continuous listening mode"""
        print("\n👂 Continuous Listening Test")
        print("-" * 30)
        
        if self.test_mode:
            # Simulate wake word detection
            test_inputs = [
                ("Background noise", False),
                ("Hey Echo", True),
                ("More background talking", False),
                ("OK Echo, send message", True),
                ("Just chatting", False)
            ]
            
            for text, is_wake in test_inputs:
                self.audio_processor.enable_test_mode(text)
                audio = self.audio_processor.record_audio(duration=1)
                result = self.audio_processor.transcribe_audio(audio)
                
                detected = self._detect_wake_word(result.get("text", ""))
                print(f"\n🎤 Heard: '{text}'")
                print(f"🔍 Wake word detected: {detected}")
                
                if detected:
                    print("✅ ECHO is listening...")
        else:
            print("👂 Listening for wake word ('Hey Echo' or 'OK Echo')...")
            print("Press Ctrl+C to stop")
            
            try:
                while True:
                    audio = self.audio_processor.record_audio(duration=3)
                    result = self.audio_processor.transcribe_audio(audio)
                    
                    if result["success"]:
                        text = result["text"]
                        if self._detect_wake_word(text):
                            print(f"\n✅ Wake word detected! Heard: '{text}'")
                            print("🎤 Listening for command...")
                            
                            # Listen for actual command
                            audio = self.audio_processor.record_audio(duration=5)
                            command = self.audio_processor.process_voice_command(audio)
                            self._print_command_result(command)
                            break
            except KeyboardInterrupt:
                print("\n⏹️  Stopped listening")
    
    async def test_voice_to_agent(self):
        """Test complete voice to agent workflow"""
        print("\n🤖 Voice-to-Agent Test")
        print("-" * 30)
        
        if self.test_mode:
            test_scenarios = [
                {
                    "voice": "Reply to John's email saying I'll be there",
                    "platform": "email",
                    "expected_action": "send"
                },
                {
                    "voice": "Draft a message for the slack team channel",
                    "platform": "slack", 
                    "expected_action": "draft"
                }
            ]
            
            for scenario in test_scenarios:
                print(f"\n🎤 Voice: '{scenario['voice']}'")
                
                # Process voice command
                self.audio_processor.enable_test_mode(scenario['voice'])
                audio = self.audio_processor.record_audio()
                command = self.audio_processor.process_voice_command(audio)
                
                print(f"📋 Detected command: {command['command']['type']}")
                print(f"📱 Platform: {command['command']['parameters'].get('platform', 'unknown')}")
                
                # Send to agent
                result = await self.agent_manager.process_message(
                    message=command['text'],
                    platform=command['command']['parameters'].get('platform', 'generic'),
                    context={"voice_command": True}
                )
                
                print(f"✅ Agent response: {result.get('action', 'processed')}")
                
                # Convert response to speech
                response_text = result.get('response', 'Task completed')
                audio_file = self.audio_processor.synthesize_speech(response_text)
                print(f"🔊 Response audio: {audio_file}")
    
    async def test_multi_language(self):
        """Test multi-language support"""
        print("\n🌍 Multi-Language Test")
        print("-" * 30)
        
        languages = [
            ("en", "Send message to team", "Message sent to team"),
            ("es", "Enviar mensaje al equipo", "Mensaje enviado al equipo"),
            ("fr", "Envoyer message à l'équipe", "Message envoyé à l'équipe")
        ]
        
        for lang, input_text, response_text in languages:
            print(f"\n🌐 Language: {lang}")
            
            # Configure language
            self.audio_processor.config.language = lang
            
            if self.test_mode:
                self.audio_processor.enable_test_mode(input_text)
            
            print(f"🎤 Input: '{input_text}'")
            
            # Process voice
            audio = self.audio_processor.record_audio(duration=2)
            result = self.audio_processor.transcribe_audio(audio)
            
            if result["success"]:
                print(f"✅ Transcribed: '{result['text']}'")
                
                # Generate response in same language
                audio_file = self.audio_processor.synthesize_speech(response_text)
                print(f"🔊 Response: '{response_text}'")
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n🚀 Running All Tests")
        print("=" * 50)
        
        tests = [
            ("Voice Command", self.test_voice_command),
            ("Text-to-Speech", self.test_text_to_speech),
            ("Voice-to-Agent", self.test_voice_to_agent),
            ("Multi-Language", self.test_multi_language)
        ]
        
        for name, test_func in tests:
            print(f"\n▶️  Running: {name}")
            await test_func()
            print(f"✅ Completed: {name}")
            await asyncio.sleep(1)
        
        print("\n✨ All tests completed!")
    
    def _print_command_result(self, result: dict):
        """Print command processing result"""
        if result["success"]:
            print(f"✅ Transcription: '{result['text']}'")
            print(f"📋 Command Type: {result['command']['type']}")
            print(f"🎯 Confidence: {result['confidence']:.2%}")
            
            params = result['command']['parameters']
            if params:
                print(f"📊 Parameters: {params}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    def _detect_wake_word(self, text: str) -> bool:
        """Detect wake word in text"""
        wake_words = ["hey echo", "ok echo", "echo listen", "echo,"]
        text_lower = text.lower()
        return any(wake in text_lower for wake in wake_words)


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ECHO Audio Demo")
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Run in test mode with simulated audio"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick test suite"
    )
    
    args = parser.parse_args()
    
    demo = AudioDemo(test_mode=args.test)
    
    if args.quick:
        # Run quick automated tests
        await demo.run_all_tests()
    else:
        # Run interactive demo
        await demo.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)