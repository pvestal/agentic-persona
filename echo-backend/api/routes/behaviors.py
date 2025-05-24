"""
API routes for reactive behavior management
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime

from services.agent_manager import agent_manager

router = APIRouter(
    prefix="/behaviors",
    tags=["behaviors"]
)

@router.get("/")
async def get_behaviors() -> Dict[str, Any]:
    """Get all registered behaviors"""
    behaviors = []
    for name, behavior in agent_manager.behavior_engine.behaviors.items():
        behaviors.append({
            "name": name,
            "type": behavior.trigger_type.value,
            "description": behavior.description,
            "priority": behavior.priority,
            "last_triggered": behavior.last_triggered.isoformat() if behavior.last_triggered else None,
            "trigger_count": behavior.trigger_count
        })
    
    return {
        "behaviors": behaviors,
        "engine_running": agent_manager.behavior_engine.running,
        "context": agent_manager.behavior_engine.context
    }

@router.post("/trigger/{behavior_name}")
async def trigger_behavior(behavior_name: str) -> Dict[str, Any]:
    """Manually trigger a specific behavior"""
    result = await agent_manager.trigger_behavior(behavior_name)
    
    if result is None:
        raise HTTPException(404, f"Behavior '{behavior_name}' not found")
    
    return {
        "success": True,
        "behavior": behavior_name,
        "result": result,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/context")
async def update_context(updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update behavior engine context"""
    await agent_manager.update_behavior_context(updates)
    
    return {
        "success": True,
        "context": agent_manager.behavior_engine.context,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/simulate-event")
async def simulate_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate an event to test reactive behaviors"""
    event_type = event_data.get("type", "generic")
    
    if event_type == "message_received":
        # Simulate receiving an important message
        await agent_manager.update_behavior_context({
            "message": {
                "content": event_data.get("content", "Test message"),
                "priority": event_data.get("priority", "normal"),
                "sender": event_data.get("sender", "test@example.com"),
                "timestamp": datetime.now().isoformat()
            },
            "last_interaction": datetime.now()
        })
    
    elif event_type == "user_inactive":
        # Simulate user inactivity
        from datetime import timedelta
        await agent_manager.update_behavior_context({
            "last_interaction": datetime.now() - timedelta(hours=3),
            "user_state": "idle"
        })
    
    elif event_type == "user_active":
        # Simulate user becoming active
        await agent_manager.update_behavior_context({
            "last_interaction": datetime.now(),
            "user_state": "active"
        })
    
    return {
        "success": True,
        "event_type": event_type,
        "context_updated": True,
        "timestamp": datetime.now().isoformat()
    }