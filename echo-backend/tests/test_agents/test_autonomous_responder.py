import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from agents.autonomous_responder import (
    AutonomyLevel, MessagePlatform, MessageContext, ResponseConfig,
    AutonomousResponder
)


class TestAutonomousResponder:
    
    @pytest.fixture
    def responder(self):
        return AutonomousResponder(name="test_responder")
    
    @pytest.fixture
    def message_context(self):
        return MessageContext(
            platform=MessagePlatform.EMAIL,
            sender="sender@example.com",
            recipient="user@example.com",
            subject="Test Subject",
            thread_id="thread123",
            timestamp=datetime.now(),
            urgency=0.5,
            sentiment="neutral",
            category="inquiry"
        )
    
    @pytest.fixture
    def response_config(self):
        return ResponseConfig(
            autonomy_level=AutonomyLevel.DRAFT,
            tone="professional",
            length="concise",
            response_time="immediate"
        )
    
    def test_initialization(self, responder):
        assert responder.name == "test_responder"
        assert responder.autonomy_rules == {}
        assert responder.response_templates == {}
        assert responder.learning_history == []
    
    def test_set_autonomy_level(self, responder):
        responder.set_autonomy_level(MessagePlatform.EMAIL, AutonomyLevel.AUTO_SEND)
        assert responder.autonomy_rules[MessagePlatform.EMAIL] == AutonomyLevel.AUTO_SEND
        
        responder.set_autonomy_level(MessagePlatform.SLACK, AutonomyLevel.SUGGEST)
        assert responder.autonomy_rules[MessagePlatform.SLACK] == AutonomyLevel.SUGGEST
    
    @pytest.mark.asyncio
    async def test_analyze_message(self, responder, message_context):
        message = "Can you send me the report by tomorrow?"
        
        analysis = await responder.analyze_message(message, message_context)
        
        assert "intent" in analysis
        assert "urgency" in analysis
        assert "suggested_response" in analysis
        assert "confidence" in analysis
    
    @pytest.mark.asyncio
    async def test_generate_response_draft_mode(self, responder, message_context, response_config):
        message = "When is the meeting scheduled?"
        response_config.autonomy_level = AutonomyLevel.DRAFT
        
        response = await responder.generate_response(
            message, message_context, response_config
        )
        
        assert response["status"] == "draft"
        assert "content" in response
        assert response["requires_approval"] is True
    
    @pytest.mark.asyncio
    async def test_generate_response_auto_send_mode(self, responder, message_context, response_config):
        message = "Thank you for your help"
        response_config.autonomy_level = AutonomyLevel.AUTO_SEND
        
        response = await responder.generate_response(
            message, message_context, response_config
        )
        
        assert response["status"] == "sent"
        assert response["requires_approval"] is False
    
    @pytest.mark.asyncio
    async def test_process_feedback(self, responder):
        feedback = {
            "message_id": "msg123",
            "action": "approved",
            "edits": None,
            "timestamp": datetime.now().isoformat()
        }
        
        result = await responder.process_feedback(feedback)
        
        assert result["success"] is True
        assert len(responder.learning_history) == 1
    
    def test_get_platform_config(self, responder):
        responder.set_autonomy_level(MessagePlatform.EMAIL, AutonomyLevel.AUTO_SEND)
        
        config = responder.get_platform_config(MessagePlatform.EMAIL)
        assert config["autonomy_level"] == AutonomyLevel.AUTO_SEND
        
        # Test default config for unconfigured platform
        default_config = responder.get_platform_config(MessagePlatform.SLACK)
        assert default_config["autonomy_level"] == AutonomyLevel.SUGGEST
    
    @pytest.mark.asyncio
    async def test_batch_process_messages(self, responder, message_context):
        messages = [
            {"content": "Message 1", "context": message_context},
            {"content": "Message 2", "context": message_context},
            {"content": "Message 3", "context": message_context}
        ]
        
        results = await responder.batch_process_messages(messages)
        
        assert len(results) == 3
        assert all("response" in result for result in results)
    
    def test_add_response_template(self, responder):
        template = {
            "category": "meeting_request",
            "template": "I'll check my calendar and get back to you.",
            "variables": ["date", "time"]
        }
        
        responder.add_response_template("meeting_request", template)
        assert "meeting_request" in responder.response_templates
    
    @pytest.mark.asyncio
    async def test_emergency_response_handling(self, responder, message_context):
        message = "URGENT: Server is down!"
        message_context.urgency = 0.9
        
        response = await responder.generate_response(
            message,
            message_context,
            ResponseConfig(autonomy_level=AutonomyLevel.SUGGEST)
        )
        
        # Should escalate urgency handling
        assert response.get("escalated", False) is True
    
    def test_learning_patterns_extraction(self, responder):
        # Add multiple feedback entries
        for i in range(5):
            responder.learning_history.append({
                "platform": "email",
                "category": "inquiry",
                "action": "approved",
                "timestamp": datetime.now().isoformat()
            })
        
        patterns = responder.extract_learning_patterns()
        assert "email" in patterns
        assert patterns["email"]["inquiry"]["approval_rate"] == 1.0