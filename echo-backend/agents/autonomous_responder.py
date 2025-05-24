"""
Autonomous Response System
Handles reading and responding to messages on behalf of the user
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass
import asyncio
from crewai import Agent, Task

try:
    from services.llm_service import llm_service
except ImportError:
    llm_service = None

try:
    from services.learning_system import learning_system, FeedbackType
except ImportError:
    learning_system = None
    FeedbackType = None

class AutonomyLevel(Enum):
    """Levels of autonomous operation"""
    SUGGEST = "suggest"      # Only suggest responses
    DRAFT = "draft"          # Draft but require approval
    AUTO_SEND = "auto_send"  # Send automatically
    LEARN = "learn"          # Learn from user behavior only

class MessagePlatform(Enum):
    """Supported messaging platforms"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"
    TEAMS = "teams"
    GENERIC = "generic"

@dataclass
class MessageContext:
    """Context for a message"""
    platform: MessagePlatform
    sender: str
    recipient: str
    subject: Optional[str]
    thread_id: Optional[str]
    timestamp: datetime
    urgency: float  # 0-1 scale
    sentiment: str
    category: str
    
@dataclass
class ResponseConfig:
    """Configuration for response generation"""
    autonomy_level: AutonomyLevel
    tone: str = "professional"  # professional, casual, formal, friendly
    length: str = "concise"     # concise, detailed, brief
    response_time: str = "immediate"  # immediate, batched, scheduled
    include_signature: bool = True
    max_length: int = 500
    language: str = "en"
    
class AutonomousResponder:
    """Agent that reads and responds to messages autonomously"""
    
    def __init__(self, user_profile: Dict[str, Any]):
        # Import agent naming
        from config.agent_names import get_agent_name, get_agent_greeting
        agent_info = get_agent_name("autonomous_responder")
        
        # Store user profile
        self._user_profile = user_profile
        
        # Initialize CrewAI agent
        self.agent = Agent(
            role=f"{agent_info['name']} - Personal Communication Assistant",
            goal="Read, understand, and respond to messages on behalf of the user",
            backstory=f"""I am {agent_info['name']}, {user_profile.get('name', 'User')}'s personal communication assistant. 
            {agent_info['personality']}. I understand their communication style, preferences, and priorities. 
            I can read incoming messages, draft appropriate responses, and handle routine communications 
            autonomously based on their preferences. {agent_info['tagline']}""",
            memory=True,
            verbose=True
        )
        
        self.response_history = []
        self.learning_data = {
            "approved_responses": [],
            "rejected_responses": [],
            "edited_responses": [],
            "communication_patterns": {}
        }
        
        # Default configurations per platform
        self.platform_configs = {
            MessagePlatform.EMAIL: ResponseConfig(
                autonomy_level=AutonomyLevel.DRAFT,
                tone="professional",
                length="detailed"
            ),
            MessagePlatform.SMS: ResponseConfig(
                autonomy_level=AutonomyLevel.SUGGEST,
                tone="casual",
                length="brief"
            ),
            MessagePlatform.SLACK: ResponseConfig(
                autonomy_level=AutonomyLevel.AUTO_SEND,
                tone="casual",
                length="concise"
            )
        }
        
    async def process_message(self, message: str, context: MessageContext) -> Dict[str, Any]:
        """Process an incoming message and generate response"""
        
        # Analyze message
        analysis = await self._analyze_message(message, context)
        
        # Get configuration for this platform/context
        config = self._get_response_config(context, analysis)
        
        # Generate response based on autonomy level
        if config.autonomy_level == AutonomyLevel.LEARN:
            return {
                "action": "observe",
                "analysis": analysis,
                "learning": True
            }
        
        # Generate response
        response = await self._generate_response(message, context, analysis, config)
        
        # Take action based on autonomy level
        if config.autonomy_level == AutonomyLevel.AUTO_SEND:
            return await self._auto_send_response(response, context)
        elif config.autonomy_level == AutonomyLevel.DRAFT:
            return await self._draft_response(response, context)
        else:  # SUGGEST
            return await self._suggest_response(response, context)
    
    async def _analyze_message(self, message: str, context: MessageContext) -> Dict[str, Any]:
        """Analyze incoming message for intent, urgency, etc."""
        return {
            "intent": self._detect_intent(message),
            "urgency": self._calculate_urgency(message, context),
            "sentiment": self._analyze_sentiment(message),
            "category": self._categorize_message(message, context),
            "key_points": self._extract_key_points(message),
            "requires_action": self._check_action_required(message),
            "is_question": self._is_question(message),
            "mentioned_topics": self._extract_topics(message)
        }
    
    def _get_response_config(self, context: MessageContext, analysis: Dict) -> ResponseConfig:
        """Get response configuration based on context and analysis"""
        # Start with platform default
        config = self.platform_configs.get(
            context.platform, 
            ResponseConfig(autonomy_level=AutonomyLevel.SUGGEST)
        )
        
        # Override based on analysis
        if analysis["urgency"] > 0.8:
            config.response_time = "immediate"
        
        if "personal" in analysis["category"]:
            config.autonomy_level = AutonomyLevel.SUGGEST
            
        if context.sender in self._user_profile.get("vip_contacts", []):
            config.autonomy_level = AutonomyLevel.DRAFT
            config.tone = "friendly"
        
        return config
    
    async def _generate_response(
        self, 
        message: str, 
        context: MessageContext, 
        analysis: Dict, 
        config: ResponseConfig
    ) -> str:
        """Generate appropriate response"""
        
        # Build prompt based on context
        prompt = f"""
        Message from {context.sender}: {message}
        
        Context:
        - Platform: {context.platform.value}
        - Category: {analysis['category']}
        - Sentiment: {analysis['sentiment']}
        - Urgency: {analysis['urgency']}
        
        User preferences:
        - Tone: {config.tone}
        - Length: {config.length}
        - Style: {self._user_profile.get('communication_style', 'balanced')}
        
        Generate an appropriate response that:
        1. Addresses all key points
        2. Maintains the requested tone
        3. Is {config.length} in length
        4. Reflects the user's communication style
        """
        
        # Generate initial response using LLM if available
        if llm_service:
            try:
                response = await self._generate_llm_response(message, analysis, config, context)
            except Exception as e:
                # Fallback to template if LLM fails
                response = self._generate_template_response(analysis, config)
        else:
            response = self._generate_template_response(analysis, config)
        
        # Apply learning improvements if available
        if learning_system and llm_service:
            try:
                improvements = await learning_system.get_response_improvements(
                    message=message,
                    initial_response=response,
                    context={
                        "platform": context.platform.value,
                        "sender": context.sender,
                        "urgency": analysis.get("urgency", "normal"),
                        "category": analysis.get("category", "general")
                    }
                )
                
                if improvements.get("improved_response"):
                    response = improvements["improved_response"]
            except Exception as e:
                # Log but don't fail on learning errors
                pass
        
        # Learn from patterns
        self._update_patterns(message, response, context)
        
        return response
    
    async def _generate_llm_response(
        self,
        message: str,
        analysis: Dict,
        config: ResponseConfig,
        context: MessageContext
    ) -> str:
        """Generate response using LLM service"""
        # Build agent persona based on configuration
        persona = f"""
        You are an intelligent assistant responding to messages on behalf of {self._user_profile.get('name', 'the user')}.
        Communication style: {config.tone}
        Response length: {config.length}
        Platform: {context.platform.value}
        
        User's communication preferences:
        - Tone: {config.tone}
        - Style: {self._user_profile.get('communication_style', 'balanced')}
        - Formality: {self._user_profile.get('formality_level', 'medium')}
        
        Key requirements:
        - Be {config.tone} in your communication
        - Keep responses {config.length} (brief: 1-2 sentences, concise: 3-4 sentences, detailed: full paragraph)
        - Address all key points identified in the message
        - Match the user's typical communication patterns
        - Be helpful and professional while maintaining the requested tone
        """
        
        # Prepare conversation context
        conversation_context = []
        if hasattr(context, 'history') and context.history:
            # Add recent conversation history
            for msg in context.history[-5:]:  # Last 5 messages
                conversation_context.append({
                    "role": "user" if msg.get('from_sender') else "assistant",
                    "content": msg.get('content', '')
                })
        
        # Add analysis insights to the prompt
        analysis_prompt = f"""
        Message analysis:
        - Intent: {analysis.get('intent', 'unknown')}
        - Urgency: {analysis.get('urgency', 'normal')}
        - Sentiment: {analysis.get('sentiment', 'neutral')}
        - Category: {analysis.get('category', 'general')}
        - Is question: {analysis.get('is_question', False)}
        - Requires action: {analysis.get('requires_action', False)}
        
        Original message: {message}
        
        Please generate an appropriate response following the guidelines above.
        """
        
        # Generate response
        response = await llm_service.generate_response(
            message=analysis_prompt,
            context=conversation_context,
            agent_persona=persona,
            temperature=0.7 if config.tone == "casual" else 0.5,
            max_tokens=150 if config.length == "brief" else 300 if config.length == "concise" else 500
        )
        
        return response
    
    def _generate_template_response(self, analysis: Dict, config: ResponseConfig) -> str:
        """Generate template response (placeholder for LLM)"""
        templates = {
            "question": {
                "brief": "Thanks for your question. The answer is [ANSWER].",
                "concise": "Thank you for reaching out. Regarding your question, [DETAILED_ANSWER].",
                "detailed": "Thank you for your message. I appreciate your question about [TOPIC]. [COMPREHENSIVE_ANSWER]."
            },
            "request": {
                "brief": "Got it, will do.",
                "concise": "I'll take care of that for you. [ACTION_CONFIRMATION].",
                "detailed": "Thank you for your request. I'll [SPECIFIC_ACTIONS]. [TIMELINE]."
            },
            "information": {
                "brief": "Thanks for the update.",
                "concise": "Thank you for the information. [ACKNOWLEDGMENT].",
                "detailed": "Thank you for sharing this information. [DETAILED_ACKNOWLEDGMENT]. [FOLLOW_UP]."
            }
        }
        
        intent = "information"  # Default
        if analysis.get("is_question"):
            intent = "question"
        elif analysis.get("requires_action"):
            intent = "request"
            
        return templates.get(intent, {}).get(config.length, "Thank you for your message.")
    
    async def _auto_send_response(self, response: str, context: MessageContext) -> Dict[str, Any]:
        """Automatically send response"""
        # Log the action
        self.response_history.append({
            "timestamp": datetime.now(),
            "context": context,
            "response": response,
            "action": "auto_sent"
        })
        
        return {
            "action": "sent",
            "response": response,
            "timestamp": datetime.now(),
            "confidence": 0.95
        }
    
    async def _draft_response(self, response: str, context: MessageContext) -> Dict[str, Any]:
        """Draft response for approval"""
        draft_id = f"draft_{datetime.now().timestamp()}"
        
        return {
            "action": "draft",
            "draft_id": draft_id,
            "response": response,
            "context": context,
            "suggestions": self._generate_alternatives(response, context),
            "confidence": 0.8
        }
    
    async def _suggest_response(self, response: str, context: MessageContext) -> Dict[str, Any]:
        """Suggest response options"""
        suggestions = [response] + self._generate_alternatives(response, context)
        
        return {
            "action": "suggest",
            "suggestions": suggestions,
            "context": context,
            "analysis": {
                "best_option": 0,
                "confidence": 0.7
            }
        }
    
    def _generate_alternatives(self, primary: str, context: MessageContext) -> List[str]:
        """Generate alternative responses"""
        # This would use LLM to generate variations
        return [
            primary + " Let me know if you need anything else.",
            "I'll get back to you on this shortly.",
            "Thanks for reaching out. I'll look into this."
        ]
    
    def learn_from_feedback(self, draft_id: str, action: str, edited_response: str = None):
        """Learn from user feedback on responses"""
        if action == "approved":
            self.learning_data["approved_responses"].append({
                "id": draft_id,
                "timestamp": datetime.now()
            })
        elif action == "rejected":
            self.learning_data["rejected_responses"].append({
                "id": draft_id,
                "timestamp": datetime.now()
            })
        elif action == "edited" and edited_response:
            self.learning_data["edited_responses"].append({
                "id": draft_id,
                "original": draft_id,  # Would lookup original
                "edited": edited_response,
                "timestamp": datetime.now()
            })
            
        # Update patterns based on feedback
        self._update_learning_model()
    
    def _update_learning_model(self):
        """Update internal learning model based on feedback"""
        # Analyze patterns in approved vs rejected responses
        # Adjust response generation accordingly
        pass
    
    def _detect_intent(self, message: str) -> str:
        """Detect the intent of the message"""
        # Simple keyword-based detection (would use NLP)
        message_lower = message.lower()
        if any(q in message_lower for q in ["?", "what", "how", "why", "when"]):
            return "question"
        elif any(r in message_lower for r in ["please", "could you", "can you", "need"]):
            return "request"
        elif any(i in message_lower for q in ["fyi", "update", "letting you know"]):
            return "information"
        return "general"
    
    def _calculate_urgency(self, message: str, context: MessageContext) -> float:
        """Calculate message urgency (0-1)"""
        urgency = 0.5  # Default
        
        # Check for urgency indicators
        urgent_keywords = ["urgent", "asap", "immediately", "critical", "emergency"]
        if any(keyword in message.lower() for keyword in urgent_keywords):
            urgency = 0.9
            
        # Check sender importance
        if context.sender in self._user_profile.get("vip_contacts", []):
            urgency = max(urgency, 0.7)
            
        return urgency
    
    def _analyze_sentiment(self, message: str) -> str:
        """Analyze message sentiment"""
        # Placeholder - would use sentiment analysis
        return "neutral"
    
    def _categorize_message(self, message: str, context: MessageContext) -> str:
        """Categorize the message"""
        # Simple categorization - would use ML
        categories = {
            "work": ["project", "meeting", "deadline", "report"],
            "personal": ["family", "friend", "weekend", "dinner"],
            "finance": ["payment", "invoice", "budget", "expense"],
            "scheduling": ["calendar", "appointment", "schedule", "time"]
        }
        
        message_lower = message.lower()
        for category, keywords in categories.items():
            if any(keyword in message_lower for keyword in keywords):
                return category
                
        return "general"
    
    def _extract_key_points(self, message: str) -> List[str]:
        """Extract key points from message"""
        # Placeholder - would use NLP
        return [message[:50] + "..."] if len(message) > 50 else [message]
    
    def _check_action_required(self, message: str) -> bool:
        """Check if message requires action"""
        action_keywords = ["please", "could you", "can you", "need", "required", "must"]
        return any(keyword in message.lower() for keyword in action_keywords)
    
    def _is_question(self, message: str) -> bool:
        """Check if message is a question"""
        return "?" in message or any(
            q in message.lower() for q in ["what", "how", "why", "when", "where"]
        )
    
    def _extract_topics(self, message: str) -> List[str]:
        """Extract main topics from message"""
        # Placeholder - would use NLP/entity extraction
        return []
    
    def _update_patterns(self, message: str, response: str, context: MessageContext):
        """Update communication patterns"""
        pattern_key = f"{context.platform.value}_{context.sender}"
        if pattern_key not in self.learning_data["communication_patterns"]:
            self.learning_data["communication_patterns"][pattern_key] = []
            
        self.learning_data["communication_patterns"][pattern_key].append({
            "message_preview": message[:100],
            "response_preview": response[:100],
            "timestamp": datetime.now().isoformat()
        })
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get responder statistics"""
        return {
            "total_responses": len(self.response_history),
            "approval_rate": len(self.learning_data["approved_responses"]) / max(len(self.response_history), 1),
            "platforms_active": list(set(r["context"].platform.value for r in self.response_history)),
            "average_response_length": sum(len(r["response"]) for r in self.response_history) / max(len(self.response_history), 1),
            "most_common_category": "work",  # Would calculate from history
            "learning_progress": {
                "patterns_learned": len(self.learning_data["communication_patterns"]),
                "responses_improved": len(self.learning_data["edited_responses"])
            }
        }
    
    async def learn_from_feedback(
        self,
        draft_id: str,
        action: str,
        edited_response: Optional[str] = None,
        rating: Optional[float] = None
    ):
        """Learn from user feedback on responses"""
        if not learning_system:
            return
        
        # Find the draft in response history
        draft = None
        for response in self.response_history:
            if response.get("id") == draft_id:
                draft = response
                break
        
        if not draft:
            return
        
        # Determine feedback type
        if action == "approved":
            feedback_type = FeedbackType.APPROVED
        elif action == "rejected":
            feedback_type = FeedbackType.REJECTED
        elif action == "edited":
            feedback_type = FeedbackType.EDITED
        else:
            return
        
        # Record the feedback
        await learning_system.record_feedback(
            message_id=draft_id,
            feedback_type=feedback_type,
            original_response=draft["response"],
            edited_response=edited_response,
            rating=rating,
            context={
                "platform": draft["context"].platform.value,
                "sender": draft["context"].sender,
                "message": draft["message"]
            }
        )
        
        # Update internal learning data
        if action == "approved":
            self.learning_data["approved_responses"].append(draft)
        elif action == "rejected":
            self.learning_data["rejected_responses"].append(draft)
        elif action == "edited" and edited_response:
            self.learning_data["edited_responses"].append({
                **draft,
                "edited_response": edited_response,
                "edit_diff": self._calculate_edit_diff(draft["response"], edited_response)
            })
    
    def _calculate_edit_diff(self, original: str, edited: str) -> Dict[str, Any]:
        """Calculate the difference between original and edited response"""
        return {
            "length_change": len(edited) - len(original),
            "word_count_change": len(edited.split()) - len(original.split()),
            "similarity": self._calculate_similarity(original, edited)
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)