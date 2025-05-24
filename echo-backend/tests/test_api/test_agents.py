import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from main import app
from services.agent_manager import AgentManager


class TestAgentsAPI:
    
    @pytest.fixture
    def mock_agent_manager(self):
        with patch('api.routes.agents.AgentManager') as mock:
            manager_instance = Mock(spec=AgentManager)
            mock.return_value = manager_instance
            yield manager_instance
    
    def test_list_agents(self, client, mock_agent_manager):
        # Mock agent status
        mock_agent_manager.get_agent_status = AsyncMock(return_value=[
            {"name": "responder", "status": "active", "version": "0.1.0"},
            {"name": "evolution", "status": "active", "version": "0.1.0"}
        ])
        
        response = client.get("/api/agents/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "responder"
        assert data[1]["name"] == "evolution"
    
    def test_get_agent_found(self, client, mock_agent_manager):
        mock_agent_manager.get_agent_status = AsyncMock(return_value=[
            {"name": "responder", "status": "active", "capabilities": ["auto_response"]}
        ])
        
        response = client.get("/api/agents/responder")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "responder"
        assert "auto_response" in data["capabilities"]
    
    def test_get_agent_not_found(self, client, mock_agent_manager):
        mock_agent_manager.get_agent_status = AsyncMock(return_value=[])
        
        response = client.get("/api/agents/nonexistent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_update_agent_config_success(self, client, mock_agent_manager):
        mock_agent_manager.update_agent_config = AsyncMock(
            return_value={"success": True, "message": "Config updated"}
        )
        
        config_data = {
            "autonomy_level": "high",
            "preferences": {"response_time": "fast"}
        }
        
        response = client.put("/api/agents/responder/config", json=config_data)
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_agent_manager.update_agent_config.assert_called_once_with(
            "responder", config_data
        )
    
    def test_update_agent_config_failure(self, client, mock_agent_manager):
        mock_agent_manager.update_agent_config = AsyncMock(
            return_value={"success": False, "message": "Invalid config"}
        )
        
        response = client.put("/api/agents/responder/config", json={})
        
        assert response.status_code == 400
        assert "Invalid config" in response.json()["detail"]
    
    def test_execute_agent_task(self, client, mock_agent_manager):
        mock_agent_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "response": "Task completed",
                "agent": "responder"
            }
        )
        
        task_data = {
            "agent_name": "responder",
            "task": "Process this request",
            "context": {"urgency": "high"},
            "priority": "high"
        }
        
        response = client.post("/api/agents/responder/task", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["response"] == "Task completed"
        
        # Verify process_message was called correctly
        mock_agent_manager.process_message.assert_called_once()
        call_args = mock_agent_manager.process_message.call_args
        assert call_args[1]["message"] == "Process this request"
        assert call_args[1]["platform"] == "api"
        assert call_args[1]["context"]["priority"] == "high"
    
    def test_get_agent_stats_responder(self, client, mock_agent_manager):
        # Mock responder agent with statistics
        mock_responder = Mock()
        mock_responder.get_statistics.return_value = {
            "total_messages": 100,
            "response_rate": 0.95
        }
        mock_agent_manager.agents = {"responder": mock_responder}
        
        response = client.get("/api/agents/responder/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_messages"] == 100
        assert data["response_rate"] == 0.95
    
    def test_get_agent_stats_other(self, client, mock_agent_manager):
        mock_agent_manager.agents = {}
        
        response = client.get("/api/agents/evolution/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "evolution"
        assert "not available" in data["stats"]
    
    def test_submit_learning_feedback_success(self, client, mock_agent_manager):
        mock_responder = Mock()
        mock_responder.learn_from_feedback = Mock()
        mock_agent_manager.agents = {"responder": mock_responder}
        
        feedback_data = {
            "draft_id": "draft123",
            "action": "approved",
            "edited_response": None
        }
        
        response = client.post("/api/agents/responder/learn", json=feedback_data)
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_responder.learn_from_feedback.assert_called_once_with(
            draft_id="draft123",
            action="approved",
            edited_response=None
        )
    
    def test_submit_learning_feedback_not_available(self, client, mock_agent_manager):
        mock_agent_manager.agents = {}
        
        response = client.post("/api/agents/evolution/learn", json={})
        
        assert response.status_code == 200
        assert response.json()["success"] is False
        assert "not available" in response.json()["message"]
    
    @patch('api.routes.agents.Path')
    def test_get_agent_evolution_exists(self, mock_path, client, mock_agent_manager):
        # Mock evolution file exists
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_path.return_value = mock_file
        
        evolution_data = {
            "agent": "responder",
            "evolutions": [{"version": "0.1.1", "changes": ["improved response"]}]
        }
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = \
                '{"agent": "responder", "evolutions": [{"version": "0.1.1", "changes": ["improved response"]}]}'
            
            with patch('json.load', return_value=evolution_data):
                response = client.get("/api/agents/responder/evolution")
        
        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "responder"
        assert len(data["evolutions"]) == 1
    
    @patch('api.routes.agents.Path')
    def test_get_agent_evolution_not_exists(self, mock_path, client, mock_agent_manager):
        # Mock evolution file doesn't exist
        mock_file = Mock()
        mock_file.exists.return_value = False
        mock_path.return_value = mock_file
        
        response = client.get("/api/agents/responder/evolution")
        
        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "responder"
        assert data["evolutions"] == []
        assert "No evolution history" in data["message"]