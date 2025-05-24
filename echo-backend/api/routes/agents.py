"""
Agent API routes
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel

from services.agent_manager import AgentManager

router = APIRouter()

class AgentConfig(BaseModel):
    """Agent configuration model"""
    autonomy_level: str = None
    preferences: Dict[str, Any] = None
    platform_overrides: Dict[str, str] = None

class AgentTask(BaseModel):
    """Agent task model"""
    agent_name: str
    task: str
    context: Dict[str, Any] = {}
    priority: str = "medium"

@router.get("/")
async def list_agents():
    """List all available agents"""
    # This would be injected via dependency
    agent_manager = AgentManager()
    return await agent_manager.get_agent_status()

@router.get("/{agent_name}")
async def get_agent(agent_name: str):
    """Get specific agent details"""
    agent_manager = AgentManager()
    agents = await agent_manager.get_agent_status()
    
    for agent in agents:
        if agent["name"] == agent_name:
            return agent
    
    raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")

@router.put("/{agent_name}/config")
async def update_agent_config(agent_name: str, config: AgentConfig):
    """Update agent configuration"""
    agent_manager = AgentManager()
    result = await agent_manager.update_agent_config(agent_name, config.dict(exclude_none=True))
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.post("/{agent_name}/task")
async def execute_agent_task(agent_name: str, task: AgentTask):
    """Execute a specific task with an agent"""
    agent_manager = AgentManager()
    
    # Process the task
    result = await agent_manager.process_message(
        message=task.task,
        platform="api",
        context={
            "agent": agent_name,
            "priority": task.priority,
            **task.context
        }
    )
    
    return result

@router.get("/{agent_name}/stats")
async def get_agent_stats(agent_name: str):
    """Get agent statistics"""
    agent_manager = AgentManager()
    
    if agent_name == "responder":
        # Special handling for responder stats
        agents = agent_manager.agents
        if "responder" in agents:
            return agents["responder"].get_statistics()
    
    return {
        "agent": agent_name,
        "stats": "Statistics not available for this agent"
    }

@router.post("/{agent_name}/learn")
async def submit_learning_feedback(
    agent_name: str,
    feedback: Dict[str, Any]
):
    """Submit learning feedback for an agent"""
    agent_manager = AgentManager()
    
    if agent_name == "responder" and "responder" in agent_manager.agents:
        agent = agent_manager.agents["responder"]
        agent.learn_from_feedback(
            draft_id=feedback.get("draft_id"),
            action=feedback.get("action"),
            edited_response=feedback.get("edited_response")
        )
        return {"success": True, "message": "Feedback recorded"}
    
    return {"success": False, "message": "Learning not available for this agent"}

@router.get("/{agent_name}/evolution")
async def get_agent_evolution(agent_name: str):
    """Get agent evolution history"""
    from pathlib import Path
    import json
    
    evolution_file = Path(f"evolution/{agent_name}_evolution.json")
    
    if evolution_file.exists():
        with open(evolution_file, 'r') as f:
            return json.load(f)
    
    return {
        "agent": agent_name,
        "evolutions": [],
        "message": "No evolution history found"
    }