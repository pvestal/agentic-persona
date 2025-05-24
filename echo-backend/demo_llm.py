#!/usr/bin/env python3
"""
Demo script to test LLM integration
"""

import asyncio
import json
from datetime import datetime
from services.llm_service import llm_service

async def test_response_generation():
    """Test basic response generation"""
    print("\n=== Testing Response Generation ===")
    
    test_messages = [
        "Can we schedule a meeting next week?",
        "I need help with my project deadline",
        "Thank you for your help yesterday!",
        "What's the status of the report?",
        "I'm having technical issues with the system"
    ]
    
    for message in test_messages:
        print(f"\nMessage: {message}")
        
        # Generate response
        response = await llm_service.generate_response(
            message=message,
            agent_persona="You are a helpful assistant responding professionally.",
            temperature=0.7
        )
        
        print(f"Response: {response}")

async def test_message_analysis():
    """Test message intent analysis"""
    print("\n=== Testing Message Analysis ===")
    
    test_messages = [
        "Can we reschedule our 3pm meeting to 4pm?",
        "The server is down and customers are complaining!",
        "Great job on the presentation!",
        "When is the deadline for the Q4 report?",
        "I'm out sick today"
    ]
    
    for message in test_messages:
        print(f"\nMessage: {message}")
        
        # Analyze message
        analysis = await llm_service.analyze_message_intent(message)
        
        print(f"Analysis: {json.dumps(analysis, indent=2)}")

async def test_response_enhancement():
    """Test response enhancement with user preferences"""
    print("\n=== Testing Response Enhancement ===")
    
    base_response = "I'll schedule the meeting for next Tuesday at 2pm."
    
    preferences_list = [
        {
            "communication_style": "casual",
            "preferred_tone": "friendly",
            "formality": "low"
        },
        {
            "communication_style": "professional",
            "preferred_tone": "formal",
            "formality": "high"
        },
        {
            "communication_style": "technical",
            "preferred_tone": "direct",
            "formality": "medium"
        }
    ]
    
    for prefs in preferences_list:
        print(f"\nPreferences: {json.dumps(prefs, indent=2)}")
        print(f"Base response: {base_response}")
        
        enhanced = await llm_service.enhance_response_with_context(
            base_response=base_response,
            user_preferences=prefs,
            message_history=[]
        )
        
        print(f"Enhanced: {enhanced}")

async def test_summary_generation():
    """Test message summary generation"""
    print("\n=== Testing Summary Generation ===")
    
    messages = [
        {"timestamp": "2024-01-23 09:00", "sender": "john@example.com", "content": "Can we meet to discuss the Q1 budget?"},
        {"timestamp": "2024-01-23 09:15", "sender": "me", "content": "Sure, how about Tuesday at 2pm?"},
        {"timestamp": "2024-01-23 09:30", "sender": "john@example.com", "content": "Perfect, I'll send a calendar invite"},
        {"timestamp": "2024-01-23 10:00", "sender": "sarah@example.com", "content": "The marketing report is ready for review"},
        {"timestamp": "2024-01-23 10:30", "sender": "me", "content": "Thanks, I'll look at it this afternoon"},
        {"timestamp": "2024-01-23 11:00", "sender": "mike@example.com", "content": "Server maintenance scheduled for tonight"},
        {"timestamp": "2024-01-23 11:15", "sender": "me", "content": "Got it, I'll notify the team"}
    ]
    
    summary = await llm_service.generate_summary(
        messages=messages,
        summary_type="daily"
    )
    
    print(f"Daily Summary:\n{summary}")

async def main():
    """Run all tests"""
    print("LLM Service Demo")
    print("================")
    
    # Check if LLM is configured
    if not llm_service.openai_client and not llm_service.anthropic_client:
        print("\n⚠️  Warning: No LLM API keys configured!")
        print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        print("Responses will use fallback templates.\n")
    else:
        provider = "OpenAI" if llm_service.openai_client else "Anthropic"
        print(f"\n✓ Using {provider} for LLM generation\n")
    
    # Run tests
    await test_response_generation()
    await test_message_analysis()
    await test_response_enhancement()
    await test_summary_generation()
    
    print("\n\nDemo complete!")

if __name__ == "__main__":
    asyncio.run(main())