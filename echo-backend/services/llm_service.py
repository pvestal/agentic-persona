"""LLM Service for generating intelligent responses."""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None
    
try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"  # For future local model support


class LLMService:
    """Service for managing LLM interactions and response generation."""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.default_provider = LLMProvider.OPENAI
        
        # Initialize clients based on available API keys
        if settings.openai_api_key and AsyncOpenAI:
            try:
                self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
            
        if settings.anthropic_api_key and AsyncAnthropic:
            try:
                self.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
                self.default_provider = LLMProvider.ANTHROPIC
                logger.info("Anthropic client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
            
        if not self.openai_client and not self.anthropic_client:
            logger.warning("No LLM API keys configured. Response generation will be limited.")
    
    async def generate_response(
        self,
        message: str,
        context: Optional[List[Dict[str, str]]] = None,
        agent_persona: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        provider: Optional[LLMProvider] = None
    ) -> str:
        """
        Generate a response using the configured LLM.
        
        Args:
            message: The input message to respond to
            context: Previous conversation context
            agent_persona: Description of the agent's persona/role
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0-1)
            provider: Specific LLM provider to use
            
        Returns:
            Generated response text
        """
        provider = provider or self.default_provider
        
        # Build the conversation history
        messages = []
        
        # Add system message with persona if provided
        if agent_persona:
            messages.append({
                "role": "system",
                "content": agent_persona
            })
        
        # Add conversation context
        if context:
            messages.extend(context)
        
        # Add the current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        try:
            if provider == LLMProvider.OPENAI and self.openai_client:
                return await self._generate_openai_response(
                    messages, max_tokens, temperature
                )
            elif provider == LLMProvider.ANTHROPIC and self.anthropic_client:
                return await self._generate_anthropic_response(
                    messages, max_tokens, temperature
                )
            else:
                # Fallback to template response
                return self._generate_fallback_response(message)
                
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self._generate_fallback_response(message)
    
    async def _generate_openai_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate response using OpenAI."""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _generate_anthropic_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate response using Anthropic."""
        try:
            # Convert messages to Anthropic format
            system_message = None
            anthropic_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            response = await self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=anthropic_messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate a fallback response when no LLM is available."""
        responses = [
            "I understand your message. Let me process that for you.",
            "Thank you for your message. I'll handle this appropriately.",
            "I've received your message and will respond accordingly.",
            "Message noted. I'll take care of this for you."
        ]
        # Simple selection based on message length
        import random
        return random.choice(responses)
    
    async def analyze_message_intent(
        self,
        message: str,
        provider: Optional[LLMProvider] = None
    ) -> Dict[str, Any]:
        """
        Analyze the intent and key information from a message.
        
        Returns:
            Dict containing intent, urgency, categories, and entities
        """
        prompt = f"""Analyze this message and extract:
1. Primary intent (question, request, information, complaint, etc.)
2. Urgency level (low, medium, high, critical)
3. Categories (technical, personal, business, etc.)
4. Key entities (names, dates, products, etc.)
5. Sentiment (positive, neutral, negative)

Message: {message}

Respond in JSON format."""

        try:
            response = await self.generate_response(
                prompt,
                agent_persona="You are a message analysis assistant. Respond only with valid JSON.",
                temperature=0.3,
                provider=provider
            )
            
            # Try to parse the JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback analysis
                return {
                    "intent": "unknown",
                    "urgency": "medium",
                    "categories": ["general"],
                    "entities": [],
                    "sentiment": "neutral"
                }
        except Exception as e:
            logger.error(f"Error analyzing message: {e}")
            return {
                "intent": "unknown",
                "urgency": "medium",
                "categories": ["general"],
                "entities": [],
                "sentiment": "neutral"
            }
    
    async def enhance_response_with_context(
        self,
        base_response: str,
        user_preferences: Dict[str, Any],
        message_history: List[Dict[str, str]],
        provider: Optional[LLMProvider] = None
    ) -> str:
        """
        Enhance a response based on user preferences and history.
        
        Args:
            base_response: The initial response to enhance
            user_preferences: User's communication preferences
            message_history: Recent message history
            
        Returns:
            Enhanced response text
        """
        style = user_preferences.get("communication_style", "professional")
        tone = user_preferences.get("preferred_tone", "friendly")
        
        prompt = f"""Enhance this response to match the user's preferences:
        
Original response: {base_response}

User preferences:
- Communication style: {style}
- Preferred tone: {tone}
- Formality level: {user_preferences.get('formality', 'medium')}

Recent conversation context shows the user prefers {tone} communication.

Provide an enhanced version that maintains the same meaning but matches their preferences."""

        try:
            return await self.generate_response(
                prompt,
                agent_persona="You are a communication style expert.",
                temperature=0.5,
                provider=provider
            )
        except Exception as e:
            logger.error(f"Error enhancing response: {e}")
            return base_response
    
    async def generate_summary(
        self,
        messages: List[Dict[str, Any]],
        summary_type: str = "daily",
        provider: Optional[LLMProvider] = None
    ) -> str:
        """
        Generate a summary of messages.
        
        Args:
            messages: List of messages to summarize
            summary_type: Type of summary (daily, weekly, topic-based)
            
        Returns:
            Summary text
        """
        # Format messages for summary
        formatted_messages = []
        for msg in messages[:50]:  # Limit to last 50 messages
            formatted_messages.append(
                f"[{msg.get('timestamp', 'Unknown time')}] "
                f"{msg.get('sender', 'Unknown')}: {msg.get('content', '')}"
            )
        
        messages_text = "\n".join(formatted_messages)
        
        prompt = f"""Create a {summary_type} summary of these messages:

{messages_text}

Include:
1. Key topics discussed
2. Important decisions or action items
3. Notable patterns or trends
4. Recommendations for follow-up

Keep it concise and actionable."""

        try:
            return await self.generate_response(
                prompt,
                agent_persona="You are an expert at creating concise, actionable summaries.",
                max_tokens=800,
                temperature=0.4,
                provider=provider
            )
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Unable to generate {summary_type} summary at this time."


# Singleton instance
llm_service = LLMService()