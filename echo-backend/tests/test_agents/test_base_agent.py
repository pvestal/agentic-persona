import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from agents.base_agent import BaseAgent


class TestAgent(BaseAgent):
    """Concrete implementation for testing"""
    
    async def process_task(self, task: str, context: dict) -> dict:
        if "error" in task:
            raise ValueError("Test error")
        return {"processed": task, "context": context}


class TestBaseAgent:
    
    @pytest.fixture
    def test_agent(self):
        return TestAgent(
            name="test_agent",
            role="Test Role",
            goal="Test Goal",
            backstory="Test Backstory"
        )
    
    def test_initialization_defaults(self):
        agent = TestAgent()
        assert agent.name == "unnamed_agent"
        assert agent.version == "0.1.0"
        assert agent.role == "Assistant"
        assert agent.goal == "Help the user"
        assert agent.state["active"] is True
        assert agent.state["interaction_count"] == 0
    
    def test_initialization_with_config(self):
        agent = TestAgent(
            name="custom_agent",
            role="Custom Role",
            version="1.0.0",
            capabilities=["capability1", "capability2"]
        )
        assert agent.name == "custom_agent"
        assert agent.role == "Custom Role"
        assert agent.version == "1.0.0"
        assert len(agent.capabilities) == 2
    
    def test_load_config_file(self, tmp_path):
        config_file = tmp_path / "test_config.json"
        config_data = {
            "name": "file_agent",
            "role": "File Role",
            "goal": "File Goal"
        }
        config_file.write_text(json.dumps(config_data))
        
        agent = TestAgent(config_path=str(config_file))
        assert agent.name == "file_agent"
        assert agent.role == "File Role"
        assert agent.goal == "File Goal"
    
    def test_save_config(self, test_agent, tmp_path):
        config_path = tmp_path / "saved_config.json"
        test_agent.save_config(str(config_path))
        
        assert config_path.exists()
        
        with open(config_path) as f:
            saved_config = json.load(f)
        
        assert saved_config["name"] == "test_agent"
        assert saved_config["role"] == "Test Role"
        assert saved_config["version"] == "0.1.0"
    
    @pytest.mark.asyncio
    async def test_execute_success(self, test_agent):
        result = await test_agent.execute("test task", {"key": "value"})
        
        assert result["success"] is True
        assert result["agent"] == "test_agent"
        assert "duration_ms" in result
        assert result["result"]["processed"] == "test task"
        assert test_agent.state["interaction_count"] == 1
        assert test_agent.state["success_rate"] == 1.0
    
    @pytest.mark.asyncio
    async def test_execute_failure(self, test_agent):
        result = await test_agent.execute("error task", {})
        
        assert result["success"] is False
        assert "error" in result
        assert result["error"] == "Test error"
        assert test_agent.state["interaction_count"] == 1
        assert test_agent.state["success_rate"] == 0.0
    
    @pytest.mark.asyncio
    async def test_multiple_executions_metrics(self, test_agent):
        await test_agent.execute("task1", {})
        await test_agent.execute("task2", {})
        await test_agent.execute("error task", {})
        await test_agent.execute("task3", {})
        
        assert test_agent.state["interaction_count"] == 4
        assert test_agent.state["success_rate"] == 0.75
        assert "average_response_time" in test_agent.performance_metrics
    
    @pytest.mark.asyncio
    async def test_learning_from_interaction(self, test_agent):
        test_agent.learning_enabled = True
        
        await test_agent.execute("learning task", {"type": "documentation"})
        
        assert hasattr(test_agent, 'learning_patterns')
        assert "documentation" in test_agent.learning_patterns
        assert len(test_agent.learning_patterns["documentation"]) == 1
        assert test_agent.learning_patterns["documentation"][0]["task_preview"] == "learning task"
    
    def test_evolve(self, test_agent):
        initial_version = test_agent.version
        evolution_data = {
            "improvements_suggested": [
                {
                    "type": "capability",
                    "description": "New capability"
                }
            ]
        }
        
        test_agent.evolve(evolution_data)
        
        assert test_agent.version != initial_version
        assert test_agent.version == "0.1.1"
        assert len(test_agent.evolution_log) == 1
        assert len(test_agent.capabilities) == 1
    
    def test_get_status(self, test_agent):
        status = test_agent.get_status()
        
        assert status["name"] == "test_agent"
        assert status["version"] == "0.1.0"
        assert status["role"] == "Test Role"
        assert "state" in status
        assert "performance" in status
        assert status["performance"]["total_interactions"] == 0
    
    def test_reset_metrics(self, test_agent):
        test_agent.state["interaction_count"] = 10
        test_agent.state["success_rate"] = 0.8
        test_agent.performance_metrics["average_response_time"] = 100
        
        test_agent.reset_metrics()
        
        assert test_agent.state["interaction_count"] == 0
        assert test_agent.state["success_rate"] == 0.0
        assert test_agent.performance_metrics == {}
    
    def test_repr(self, test_agent):
        repr_str = repr(test_agent)
        assert "TestAgent" in repr_str
        assert "test_agent" in repr_str
        assert "0.1.0" in repr_str