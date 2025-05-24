"""
Agent Manager - Handles all agent orchestration and routing
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from crewai import Crew, Agent, Task
from agents.autonomous_responder import AutonomousResponder, MessageContext, MessagePlatform
from agents.evolution_engine import SelfReflectionAgent
from config.settings import settings
from services.reactive_behaviors import ReactiveBehaviorEngine, create_default_behaviors

class AgentManager:
    """Manages all agents and their interactions"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.crews: Dict[str, Crew] = {}
        self.websockets = []
        self.message_queue = asyncio.Queue()
        self.processing_stats = {
            "total_messages": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "average_response_time": 0
        }
        # Initialize reactive behavior engine
        self.behavior_engine = ReactiveBehaviorEngine()
        self._setup_reactive_behaviors()
        
    async def initialize_agents(self):
        """Initialize all agents from configuration"""
        print("Initializing agents...")
        
        # Load user profile
        user_profile = self._load_user_profile()
        
        # Initialize core agents
        self.agents["responder"] = AutonomousResponder(user_profile)
        self.agents["reflection"] = SelfReflectionAgent()
        
        # Load agent configurations
        agent_configs = self._load_agent_configs()
        
        for agent_name, config in agent_configs.items():
            self.agents[agent_name] = self._create_agent_from_config(config)
        
        # Create crews for multi-agent tasks
        self._create_crews()
        
        print(f"✅ Initialized {len(self.agents)} agents")
    
    def _load_user_profile(self) -> Dict[str, Any]:
        """Load user profile from file or database"""
        profile_path = Path("user-preferences.json")
        if profile_path.exists():
            with open(profile_path, 'r') as f:
                return json.load(f)
        return {
            "name": "User",
            "communication_style": "balanced",
            "vip_contacts": [],
            "preferences": {}
        }
    
    def _load_agent_configs(self) -> Dict[str, Dict]:
        """Load agent configurations"""
        configs = {}
        agents_path = Path("agents")
        
        if agents_path.exists():
            for config_file in agents_path.glob("*.json"):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    configs[config["name"]] = config
                    
        return configs
    
    def _create_agent_from_config(self, config: Dict) -> Agent:
        """Create agent from configuration"""
        return Agent(
            role=config.get("role", "Assistant"),
            goal=config.get("goal", "Help the user"),
            backstory=config.get("backstory", "I am a helpful assistant"),
            memory=config.get("memory", {}).get("long_term", True),
            verbose=settings.debug,
            allow_delegation=True
        )
    
    def _create_crews(self):
        """Create crews for multi-agent collaboration"""
        # Documentation crew
        if "documentation_automator" in self.agents:
            self.crews["documentation"] = Crew(
                agents=[
                    self.agents["documentation_automator"],
                    self.agents["reflection"]
                ],
                verbose=settings.debug
            )
        
        # Response crew - using the internal agent from AutonomousResponder
        if hasattr(self.agents["responder"], 'agent'):
            self.crews["response"] = Crew(
                agents=[
                    self.agents["responder"].agent,
                    self.agents["reflection"]
                ],
                verbose=settings.debug
            )
    
    async def process_message(
        self, 
        message: str, 
        platform: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process message through appropriate agent"""
        start_time = datetime.now()
        
        try:
            # Create message context
            msg_context = MessageContext(
                platform=MessagePlatform(platform),
                sender=context.get("sender", "unknown"),
                recipient=context.get("recipient", "user"),
                subject=context.get("subject"),
                thread_id=context.get("thread_id"),
                timestamp=datetime.now(),
                urgency=context.get("urgency", 0.5),
                sentiment=context.get("sentiment", "neutral"),
                category=context.get("category", "general")
            )
            
            # Route to responder agent
            result = await self.agents["responder"].process_message(message, msg_context)
            
            # Update statistics
            self.processing_stats["total_messages"] += 1
            self.processing_stats["successful_responses"] += 1
            
            # Calculate response time
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._update_average_response_time(duration_ms)
            
            # Add metadata
            result["id"] = f"msg_{datetime.now().timestamp()}"
            result["duration_ms"] = duration_ms
            result["success"] = True
            
            # Broadcast to websockets
            await self._broadcast_update({
                "type": "message_processed",
                "result": result
            })
            
            return result
            
        except Exception as e:
            self.processing_stats["failed_responses"] += 1
            return {
                "success": False,
                "error": str(e),
                "duration_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
    
    async def process_realtime(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process real-time message from WebSocket"""
        return await self.process_message(
            message=data.get("message", ""),
            platform=data.get("platform", "generic"),
            context=data.get("context", {})
        )
    
    def add_websocket(self, websocket):
        """Add WebSocket connection"""
        self.websockets.append(websocket)
    
    def remove_websocket(self, websocket):
        """Remove WebSocket connection"""
        if websocket in self.websockets:
            self.websockets.remove(websocket)
    
    async def _broadcast_update(self, update: Dict[str, Any]):
        """Broadcast update to all connected WebSockets"""
        disconnected = []
        
        for ws in self.websockets:
            try:
                await ws.send_json(update)
            except:
                disconnected.append(ws)
        
        # Remove disconnected sockets
        for ws in disconnected:
            self.remove_websocket(ws)
    
    def _update_average_response_time(self, new_time: float):
        """Update average response time"""
        total = self.processing_stats["total_messages"]
        current_avg = self.processing_stats["average_response_time"]
        
        if total == 1:
            self.processing_stats["average_response_time"] = new_time
        else:
            # Calculate new average
            self.processing_stats["average_response_time"] = (
                (current_avg * (total - 1) + new_time) / total
            )
    
    async def get_agent_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        status = []
        
        for name, agent in self.agents.items():
            # Handle custom agents differently
            if name == "responder" and hasattr(agent, 'agent'):
                agent_status = {
                    "name": name,
                    "role": agent.agent.role,
                    "active": True,
                    "memory_enabled": True
                }
                if hasattr(agent, 'get_statistics'):
                    agent_status["statistics"] = agent.get_statistics()
            elif hasattr(agent, 'role'):
                agent_status = {
                    "name": name,
                    "role": agent.role,
                    "active": True,
                    "memory_enabled": hasattr(agent, 'memory') and agent.memory
                }
            else:
                # Fallback for custom agents
                agent_status = {
                    "name": name,
                    "role": getattr(agent, 'role', 'Custom Agent'),
                    "active": True,
                    "memory_enabled": False
                }
            
            status.append(agent_status)
        
        return status
    
    async def get_total_messages(self) -> int:
        """Get total messages processed"""
        return self.processing_stats["total_messages"]
    
    async def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        if "responder" in self.agents:
            return self.agents["responder"].get_statistics().get("learning_progress", {})
        return {}
    
    async def update_agent_config(self, agent_name: str, config: Dict[str, Any]):
        """Update agent configuration"""
        if agent_name in self.agents:
            # Update agent properties
            agent = self.agents[agent_name]
            
            if "autonomy_level" in config:
                agent.config.autonomy_level = config["autonomy_level"]
            
            if "preferences" in config:
                agent.config.update(config["preferences"])
            
            return {"success": True, "message": f"Updated {agent_name}"}
        
        return {"success": False, "message": f"Agent {agent_name} not found"}
    
    async def shutdown(self):
        """Shutdown all agents gracefully"""
        print("Shutting down agents...")
        
        # Save statistics
        stats_path = Path("evolution/shutdown_stats.json")
        stats_path.parent.mkdir(exist_ok=True)
        
        with open(stats_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "processing_stats": self.processing_stats,
                "agent_count": len(self.agents)
            }, f, indent=2)
        
        # Close WebSocket connections
        for ws in self.websockets:
            try:
                await ws.close()
            except:
                pass
        
        print("✅ Agents shutdown complete")
    
    def _setup_reactive_behaviors(self):
        """Set up reactive behaviors for the agent system"""
        # Load default behaviors
        default_behaviors = create_default_behaviors()
        for behavior in default_behaviors:
            self.behavior_engine.register_behavior(behavior)
        
        # Add custom behavior for WebSocket notifications
        async def websocket_notification_action(context):
            """Send notifications through WebSocket"""
            notification = context.get("last_notification")
            if notification and self.websockets:
                await self._broadcast_update({
                    "type": "reactive_notification",
                    "notification": notification
                })
            return notification
        
        # Override default behavior actions to include WebSocket notifications
        for name, behavior in self.behavior_engine.behaviors.items():
            original_action = behavior.action
            
            async def wrapped_action(context, orig_action=original_action):
                result = await orig_action(context)
                if result:
                    context["last_notification"] = result
                    await websocket_notification_action(context)
                return result
            
            behavior.action = wrapped_action
    
    async def start_reactive_behaviors(self):
        """Start the reactive behavior engine"""
        await self.behavior_engine.start()
        print("✅ Reactive behaviors started")
    
    async def stop_reactive_behaviors(self):
        """Stop the reactive behavior engine"""
        await self.behavior_engine.stop()
        print("✅ Reactive behaviors stopped")
    
    async def update_behavior_context(self, updates: Dict[str, Any]):
        """Update the behavior engine context"""
        self.behavior_engine.update_context(updates)
        
        # Special handling for message queue updates
        if "message" in updates:
            message_queue = self.behavior_engine.context.get("message_queue", [])
            message_queue.append(updates["message"])
            self.behavior_engine.context["message_queue"] = message_queue[-50:]  # Keep last 50
    
    async def trigger_behavior(self, behavior_name: str) -> Optional[Dict[str, Any]]:
        """Manually trigger a specific behavior"""
        if behavior_name in self.behavior_engine.behaviors:
            behavior = self.behavior_engine.behaviors[behavior_name]
            return await self.behavior_engine._execute_behavior(behavior)
        return None