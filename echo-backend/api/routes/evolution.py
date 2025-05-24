"""
Evolution API routes
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime

from agents.evolution_engine import EvolutionEngine

router = APIRouter()

class EvolutionTrigger(BaseModel):
    """Manual evolution trigger"""
    agent_name: str
    reason: str
    force: bool = False

@router.get("/status")
async def get_evolution_status():
    """Get current evolution system status"""
    engine = EvolutionEngine()
    return {
        "enabled": True,
        "last_cycle": datetime.now().isoformat(),
        "statistics": engine.generate_evolution_report()
    }

@router.post("/trigger")
async def trigger_evolution(trigger: EvolutionTrigger):
    """Manually trigger evolution for an agent"""
    engine = EvolutionEngine()
    
    # Analyze recent interactions
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "agent": trigger.agent_name,
        "reason": trigger.reason,
        "patterns_found": ["manual_trigger"],
        "improvements_suggested": [
            {
                "type": "capability",
                "description": f"User-requested evolution: {trigger.reason}",
                "priority": "high"
            }
        ],
        "success_metrics": {
            "trigger_type": "manual",
            "confidence": 1.0
        }
    }
    
    # Evolve the agent
    engine.evolve_agent(trigger.agent_name, analysis)
    
    return {
        "success": True,
        "agent": trigger.agent_name,
        "message": f"Evolution triggered for {trigger.agent_name}"
    }

@router.get("/history")
async def get_evolution_history(agent_name: str = None):
    """Get evolution history"""
    from pathlib import Path
    import json
    
    if agent_name:
        # Get specific agent history
        evolution_file = Path(f"evolution/{agent_name}_evolution.json")
        if evolution_file.exists():
            with open(evolution_file, 'r') as f:
                return json.load(f)
        else:
            return {"agent": agent_name, "evolutions": []}
    else:
        # Get all evolution history
        evolution_path = Path("evolution")
        history = {}
        
        if evolution_path.exists():
            for file in evolution_path.glob("*_evolution.json"):
                agent_name = file.stem.replace("_evolution", "")
                with open(file, 'r') as f:
                    history[agent_name] = json.load(f)
        
        return history

@router.get("/report")
async def generate_evolution_report():
    """Generate comprehensive evolution report"""
    engine = EvolutionEngine()
    return engine.generate_evolution_report()

@router.post("/learn")
async def submit_learning_data(data: Dict[str, Any]):
    """Submit data for system learning"""
    engine = EvolutionEngine()
    
    # Analyze the interaction
    analysis = engine.analyze_interaction(data)
    
    # Determine which agents should evolve
    agents_to_evolve = []
    
    if "agent" in data:
        agents_to_evolve.append(data["agent"])
    
    if data.get("type") == "message_response":
        agents_to_evolve.append("responder")
    
    # Evolve relevant agents
    for agent_name in agents_to_evolve:
        engine.evolve_agent(agent_name, analysis)
    
    return {
        "success": True,
        "analysis": analysis,
        "evolved_agents": agents_to_evolve
    }

@router.get("/metrics")
async def get_evolution_metrics():
    """Get evolution system metrics"""
    from pathlib import Path
    import json
    
    metrics = {
        "total_evolutions": 0,
        "agents_evolved": {},
        "capability_additions": 0,
        "performance_improvements": 0
    }
    
    evolution_path = Path("evolution")
    if evolution_path.exists():
        for file in evolution_path.glob("*_evolution.json"):
            with open(file, 'r') as f:
                data = json.load(f)
                evolutions = data.get("evolutions", [])
                
                agent_name = file.stem.replace("_evolution", "")
                metrics["agents_evolved"][agent_name] = len(evolutions)
                metrics["total_evolutions"] += len(evolutions)
                
                # Count improvements
                for evolution in evolutions:
                    changes = evolution.get("changes", {})
                    suggestions = changes.get("improvements_suggested", [])
                    
                    for suggestion in suggestions:
                        if suggestion.get("type") == "capability":
                            metrics["capability_additions"] += 1
                        elif suggestion.get("type") == "performance":
                            metrics["performance_improvements"] += 1
    
    return metrics

@router.post("/rollback")
async def rollback_evolution(agent_name: str, version: str):
    """Rollback an agent to a previous version"""
    # This would implement version rollback functionality
    return {
        "success": False,
        "message": "Rollback functionality not yet implemented",
        "agent": agent_name,
        "target_version": version
    }