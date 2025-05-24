"""
Base Agent class implementing CrewAI integration
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from crewai import Agent as CrewAIAgent
from abc import ABC, abstractmethod
import json
from pathlib import Path

class BaseAgent(CrewAIAgent, ABC):
    """Base class for all Agentic Persona agents"""
    
    def __init__(self, config_path: Optional[str] = None, **kwargs):
        """Initialize agent from configuration"""
        
        # Load configuration if path provided
        if config_path:
            config = self._load_config(config_path)
            kwargs.update(config)
        
        # Set default values
        self.name = kwargs.get("name", "unnamed_agent")
        self.version = kwargs.get("version", "0.1.0")
        self.created_at = kwargs.get("created", datetime.now().isoformat())
        
        # Initialize CrewAI Agent
        super().__init__(
            role=kwargs.get("role", "Assistant"),
            goal=kwargs.get("goal", "Help the user"),
            backstory=kwargs.get("backstory", "I am a helpful AI assistant"),
            memory=kwargs.get("memory", {}).get("long_term", True),
            verbose=kwargs.get("verbose", False),
            allow_delegation=kwargs.get("allow_delegation", True),
            tools=kwargs.get("tools", [])
        )
        
        # Additional attributes
        self.capabilities = kwargs.get("capabilities", [])
        self.learning_enabled = kwargs.get("learning_enabled", True)
        self.evolution_log = kwargs.get("evolution_log", [])
        self.performance_metrics = kwargs.get("performance_metrics", {})
        
        # Initialize state
        self.state = {
            "active": True,
            "last_interaction": None,
            "interaction_count": 0,
            "success_rate": 0.0
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load agent configuration from file"""
        path = Path(config_path)
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self, config_path: Optional[str] = None):
        """Save current configuration to file"""
        if not config_path:
            config_path = f"agents/{self.name}.json"
        
        config = {
            "name": self.name,
            "version": self.version,
            "created": self.created_at,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "capabilities": self.capabilities,
            "memory": {
                "short_term": True,
                "long_term": self.memory,
                "entity": True,
                "contextual": True
            },
            "tools": [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in self.tools],
            "evolution_log": self.evolution_log,
            "learning_patterns": getattr(self, 'learning_patterns', {}),
            "performance_metrics": self.performance_metrics
        }
        
        path = Path(config_path)
        path.parent.mkdir(exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
    
    @abstractmethod
    async def process_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a specific task - must be implemented by subclasses"""
        pass
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task with tracking and error handling"""
        start_time = datetime.now()
        context = context or {}
        
        try:
            # Update state
            self.state["last_interaction"] = start_time.isoformat()
            self.state["interaction_count"] += 1
            
            # Process the task
            result = await self.process_task(task, context)
            
            # Track success
            self._update_metrics(True, start_time)
            
            # Learn from interaction if enabled
            if self.learning_enabled:
                await self._learn_from_interaction(task, result, context)
            
            return {
                "success": True,
                "result": result,
                "agent": self.name,
                "duration_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
            
        except Exception as e:
            # Track failure
            self._update_metrics(False, start_time)
            
            return {
                "success": False,
                "error": str(e),
                "agent": self.name,
                "duration_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
    
    def _update_metrics(self, success: bool, start_time: datetime):
        """Update performance metrics"""
        # Update success rate
        total = self.state["interaction_count"]
        if success:
            current_successes = self.state["success_rate"] * (total - 1)
            self.state["success_rate"] = (current_successes + 1) / total
        else:
            current_successes = self.state["success_rate"] * (total - 1)
            self.state["success_rate"] = current_successes / total
        
        # Update performance metrics
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        if "average_response_time" not in self.performance_metrics:
            self.performance_metrics["average_response_time"] = duration
        else:
            # Calculate new average
            avg = self.performance_metrics["average_response_time"]
            self.performance_metrics["average_response_time"] = (
                (avg * (total - 1) + duration) / total
            )
    
    async def _learn_from_interaction(
        self, 
        task: str, 
        result: Dict[str, Any], 
        context: Dict[str, Any]
    ):
        """Learn from the interaction - can be overridden by subclasses"""
        # Default learning: just log the interaction
        if not hasattr(self, 'learning_patterns'):
            self.learning_patterns = {}
        
        # Extract patterns (simplified)
        task_type = context.get("type", "general")
        if task_type not in self.learning_patterns:
            self.learning_patterns[task_type] = []
        
        self.learning_patterns[task_type].append({
            "task_preview": task[:100],
            "success": result.get("success", True),
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent patterns
        self.learning_patterns[task_type] = self.learning_patterns[task_type][-100:]
    
    def evolve(self, evolution_data: Dict[str, Any]):
        """Evolve the agent based on analysis"""
        # Increment version
        parts = self.version.split('.')
        parts[-1] = str(int(parts[-1]) + 1)
        self.version = '.'.join(parts)
        
        # Log evolution
        self.evolution_log.append({
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
            "changes": evolution_data
        })
        
        # Apply improvements
        for improvement in evolution_data.get("improvements_suggested", []):
            if improvement["type"] == "capability":
                self.capabilities.append({
                    "name": f"capability_{len(self.capabilities)}",
                    "description": improvement["description"],
                    "added_on": datetime.now().isoformat()
                })
        
        # Save updated configuration
        self.save_config()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "version": self.version,
            "role": self.role,
            "state": self.state,
            "capabilities_count": len(self.capabilities),
            "performance": {
                "success_rate": self.state["success_rate"],
                "average_response_time": self.performance_metrics.get("average_response_time", 0),
                "total_interactions": self.state["interaction_count"]
            }
        }
    
    def reset_metrics(self):
        """Reset performance metrics"""
        self.state["interaction_count"] = 0
        self.state["success_rate"] = 0.0
        self.performance_metrics = {}
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', version='{self.version}', role='{self.role}')"