"""
Evolution Engine - Continuous Improvement System

This module handles the self-improvement cycle:
1. Monitors all agent interactions
2. Analyzes patterns and performance
3. Updates agent configurations
4. Commits improvements to version control
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import git
from crewai import Agent, Task, Crew

class EvolutionEngine:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.evolution_log_path = self.repo_path / "evolution"
        self.agents_path = self.repo_path / "agents"
        self.evolution_log_path.mkdir(exist_ok=True)
        
        # Initialize git repo
        try:
            self.repo = git.Repo(self.repo_path)
        except:
            self.repo = git.Repo.init(self.repo_path)
    
    def analyze_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a user interaction for improvement opportunities"""
        return {
            "timestamp": datetime.now().isoformat(),
            "interaction_id": interaction.get("id"),
            "patterns_found": self._detect_patterns(interaction),
            "improvements_suggested": self._suggest_improvements(interaction),
            "success_metrics": self._calculate_metrics(interaction)
        }
    
    def _detect_patterns(self, interaction: Dict) -> List[str]:
        """Detect patterns in user interactions"""
        patterns = []
        
        # Check for repeated requests
        if "request_type" in interaction:
            patterns.append(f"request_type:{interaction['request_type']}")
        
        # Check for common phrases
        if "user_input" in interaction:
            # Simple pattern detection (expand with NLP)
            common_phrases = ["help me", "can you", "I need", "please"]
            for phrase in common_phrases:
                if phrase in interaction["user_input"].lower():
                    patterns.append(f"phrase:{phrase}")
        
        return patterns
    
    def _suggest_improvements(self, interaction: Dict) -> List[Dict]:
        """Suggest improvements based on interaction"""
        suggestions = []
        
        # If interaction failed, suggest capability addition
        if interaction.get("success") == False:
            suggestions.append({
                "type": "capability",
                "description": "Add handling for this request type",
                "priority": "high"
            })
        
        # If interaction was slow, suggest optimization
        if interaction.get("duration_ms", 0) > 5000:
            suggestions.append({
                "type": "performance",
                "description": "Optimize response time",
                "priority": "medium"
            })
        
        return suggestions
    
    def _calculate_metrics(self, interaction: Dict) -> Dict[str, float]:
        """Calculate success metrics"""
        return {
            "success_rate": 1.0 if interaction.get("success", True) else 0.0,
            "response_time": interaction.get("duration_ms", 0) / 1000.0,
            "user_satisfaction": interaction.get("rating", 5) / 5.0
        }
    
    def evolve_agent(self, agent_name: str, evolution_data: Dict):
        """Evolve an agent based on analysis"""
        agent_file = self.agents_path / f"{agent_name}.json"
        
        # Load current agent configuration
        if agent_file.exists():
            with open(agent_file, 'r') as f:
                agent_config = json.load(f)
        else:
            agent_config = self._create_default_agent_config(agent_name)
        
        # Update agent based on evolution data
        agent_config["version"] = self._increment_version(agent_config.get("version", "0.1.0"))
        agent_config["last_evolved"] = datetime.now().isoformat()
        agent_config["evolution_count"] = agent_config.get("evolution_count", 0) + 1
        
        # Add new capabilities if suggested
        for suggestion in evolution_data.get("improvements_suggested", []):
            if suggestion["type"] == "capability":
                agent_config["capabilities"].append({
                    "name": f"capability_{len(agent_config.get('capabilities', []))}",
                    "added_on": datetime.now().isoformat(),
                    "reason": suggestion["description"]
                })
        
        # Save updated configuration
        with open(agent_file, 'w') as f:
            json.dump(agent_config, f, indent=2)
        
        # Log evolution
        self._log_evolution(agent_name, evolution_data, agent_config["version"])
        
        # Commit changes
        self._commit_evolution(agent_name, agent_config["version"])
    
    def _create_default_agent_config(self, agent_name: str) -> Dict:
        """Create default agent configuration"""
        return {
            "name": agent_name,
            "version": "0.1.0",
            "created": datetime.now().isoformat(),
            "role": f"{agent_name} specialist",
            "goal": f"Assist with {agent_name} tasks",
            "backstory": f"Created to help with {agent_name}",
            "capabilities": [],
            "memory": {
                "short_term": True,
                "long_term": True,
                "entity": True,
                "contextual": True
            },
            "tools": [],
            "evolution_log": []
        }
    
    def _increment_version(self, version: str) -> str:
        """Increment semantic version"""
        major, minor, patch = map(int, version.split('.'))
        return f"{major}.{minor}.{patch + 1}"
    
    def _log_evolution(self, agent_name: str, evolution_data: Dict, new_version: str):
        """Log evolution details"""
        log_file = self.evolution_log_path / f"{agent_name}_evolution.json"
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = {"evolutions": []}
        
        log_data["evolutions"].append({
            "timestamp": datetime.now().isoformat(),
            "version": new_version,
            "changes": evolution_data,
            "trigger": "automatic"
        })
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def _commit_evolution(self, agent_name: str, version: str):
        """Commit evolution changes to git"""
        try:
            self.repo.index.add([
                str(self.agents_path / f"{agent_name}.json"),
                str(self.evolution_log_path / f"{agent_name}_evolution.json")
            ])
            
            commit_message = f"feat(evolution): {agent_name} evolved to v{version}\n\n🤖 Automatic evolution based on usage patterns"
            self.repo.index.commit(commit_message)
        except Exception as e:
            print(f"Git commit failed: {e}")
    
    def generate_evolution_report(self) -> Dict:
        """Generate comprehensive evolution report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_evolutions": 0,
            "agents": {}
        }
        
        # Analyze each agent's evolution
        for log_file in self.evolution_log_path.glob("*_evolution.json"):
            agent_name = log_file.stem.replace("_evolution", "")
            with open(log_file, 'r') as f:
                log_data = json.load(f)
            
            evolutions = log_data.get("evolutions", [])
            report["total_evolutions"] += len(evolutions)
            report["agents"][agent_name] = {
                "evolution_count": len(evolutions),
                "latest_version": evolutions[-1]["version"] if evolutions else "0.1.0",
                "last_evolved": evolutions[-1]["timestamp"] if evolutions else "Never"
            }
        
        return report


class SelfReflectionAgent(Agent):
    """Agent that reflects on system performance and suggests improvements"""
    
    def __init__(self):
        super().__init__(
            role="System Self-Reflection Specialist",
            goal="Analyze system performance and suggest improvements",
            backstory="""I am a meta-cognitive agent designed to observe, analyze, and improve 
            the entire system. I monitor all interactions, identify patterns, and continuously 
            evolve our collective capabilities.""",
            memory=True,
            verbose=True
        )
    
    def reflect_on_interaction(self, interaction: Dict) -> str:
        """Reflect on a specific interaction"""
        reflection = f"""
        Interaction Analysis:
        - Type: {interaction.get('type', 'unknown')}
        - Success: {interaction.get('success', 'unknown')}
        - Duration: {interaction.get('duration_ms', 0)}ms
        
        Observations:
        - User intent was {'clear' if interaction.get('intent_clarity', 0) > 0.7 else 'unclear'}
        - Response was {'satisfactory' if interaction.get('success') else 'needs improvement'}
        
        Recommendations:
        - {'Optimize response time' if interaction.get('duration_ms', 0) > 3000 else 'Performance is acceptable'}
        - {'Clarify capabilities' if not interaction.get('success') else 'Continue current approach'}
        """
        return reflection