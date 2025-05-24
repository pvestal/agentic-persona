import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from api.routes.messages import router


class TestMessagesAPI:
    
    @pytest.fixture
    def mock_agent_manager(self):
        with patch('api.routes.messages.AgentManager') as mock:
            manager_instance = Mock()
            mock.return_value = manager_instance
            yield manager_instance
    
    @pytest.fixture
    def mock_message_queue(self):
        with patch('api.routes.messages.MessageQueue') as mock:
            queue_instance = Mock()
            mock.return_value = queue_instance
            yield queue_instance
    
    def test_process_single_message(self, client, mock_agent_manager):
        mock_agent_manager.process_message = AsyncMock(return_value={
            "id": "msg_123",
            "response": "I'll help you with that.",
            "action": "auto_response",
            "confidence": 0.85
        })
        
        message_data = {
            "content": "Can you help me?",
            "platform": "email",
            "sender": "user@example.com",
            "urgency": 0.7
        }
        
        response = client.post("/api/messages/process", json=message_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_message"] == "Can you help me?"
        assert data["suggested_response"] == "I'll help you with that."
        assert data["action_taken"] == "auto_response"
        assert data["confidence"] == 0.85
    
    def test_process_bulk_messages_sync(self, client, mock_agent_manager):
        mock_agent_manager.process_message = AsyncMock(side_effect=[
            {"response": "Response 1", "action": "processed"},
            {"response": "Response 2", "action": "processed"}
        ])
        
        bulk_data = {
            "messages": [
                {
                    "content": "Message 1",
                    "platform": "slack",
                    "sender": "user1"
                },
                {
                    "content": "Message 2",
                    "platform": "slack",
                    "sender": "user2"
                }
            ],
            "process_async": False
        }
        
        response = client.post("/api/messages/bulk", json=bulk_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        assert data["message_count"] == 2
        assert len(data["results"]) == 2
    
    def test_process_bulk_messages_async(self, client, mock_agent_manager, mock_message_queue):
        mock_message_queue.enqueue = AsyncMock()
        mock_message_queue.is_empty.return_value = True
        
        bulk_data = {
            "messages": [
                {
                    "content": "Async message",
                    "platform": "email",
                    "sender": "async@example.com"
                }
            ],
            "process_async": True
        }
        
        response = client.post("/api/messages/bulk", json=bulk_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert data["message_count"] == 1
        assert "queue_id" in data
        mock_message_queue.enqueue.assert_called_once()
    
    def test_get_message_history(self, client):
        response = client.get("/api/messages/history?platform=email&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert data["filters"]["platform"] == "email"
        assert data["filters"]["limit"] == 10
    
    def test_get_pending_drafts(self, client):
        response = client.get("/api/messages/drafts")
        
        assert response.status_code == 200
        data = response.json()
        assert "drafts" in data
        assert data["total"] == 1
        assert data["drafts"][0]["id"] == "draft_123"
    
    def test_approve_draft_without_edit(self, client, mock_agent_manager):
        mock_responder = Mock()
        mock_responder.learn_from_feedback = Mock()
        mock_agent_manager.agents = {"responder": mock_responder}
        
        response = client.post("/api/messages/drafts/draft_123/approve")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert data["response_sent"] is True
        
        mock_responder.learn_from_feedback.assert_called_once_with(
            draft_id="draft_123",
            action="approved",
            edited_response=None
        )
    
    def test_approve_draft_with_edit(self, client, mock_agent_manager):
        mock_responder = Mock()
        mock_responder.learn_from_feedback = Mock()
        mock_agent_manager.agents = {"responder": mock_responder}
        
        response = client.post(
            "/api/messages/drafts/draft_123/approve",
            params={"edited_response": "Modified response"}
        )
        
        assert response.status_code == 200
        mock_responder.learn_from_feedback.assert_called_once_with(
            draft_id="draft_123",
            action="edited",
            edited_response="Modified response"
        )
    
    def test_reject_draft(self, client, mock_agent_manager):
        mock_responder = Mock()
        mock_responder.learn_from_feedback = Mock()
        mock_agent_manager.agents = {"responder": mock_responder}
        
        response = client.post(
            "/api/messages/drafts/draft_123/reject",
            params={"reason": "Inappropriate tone"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["reason"] == "Inappropriate tone"
        
        mock_responder.learn_from_feedback.assert_called_once_with(
            draft_id="draft_123",
            action="rejected"
        )
    
    def test_get_response_templates_all(self, client):
        response = client.get("/api/messages/templates")
        
        assert response.status_code == 200
        data = response.json()
        assert "greeting" in data
        assert "acknowledgment" in data
        assert "scheduling" in data
        assert isinstance(data["greeting"], list)
    
    def test_get_response_templates_by_category(self, client):
        response = client.get("/api/messages/templates?category=greeting")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "Hello" in data[0]
    
    def test_get_response_templates_invalid_category(self, client):
        response = client.get("/api/messages/templates?category=invalid")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []