"""
Agent Naming System for ECHO
Each agent has a name that reflects their personality and role
"""

from typing import Dict, Any

# Agent names with personality traits
AGENT_NAMES = {
    # Core Agents
    "autonomous_responder": {
        "name": "Echo",
        "full_name": "Echo Prime",
        "personality": "Adaptive, empathetic, and precise communicator",
        "tagline": "Your voice, perfectly amplified",
        "avatar_color": "#4A90E2"
    },
    
    "evolution_engine": {
        "name": "Darwin",
        "full_name": "Darwin Evolution Core",
        "personality": "Analytical, growth-oriented, and introspective",
        "tagline": "Constantly evolving to serve you better",
        "avatar_color": "#50C878"
    },
    
    "self_reflection_agent": {
        "name": "Mirror",
        "full_name": "Mirror Reflection System",
        "personality": "Thoughtful, philosophical, and improvement-focused",
        "tagline": "Learning from every interaction",
        "avatar_color": "#9B59B6"
    },
    
    # Specialized Agents
    "documentation_automator": {
        "name": "Scribe",
        "full_name": "Scribe Documentation Expert",
        "personality": "Meticulous, organized, and articulate",
        "tagline": "Transforming code into clear documentation",
        "avatar_color": "#F39C12"
    },
    
    "code_review_assistant": {
        "name": "Sentinel",
        "full_name": "Sentinel Code Guardian",
        "personality": "Detail-oriented, constructive, and protective",
        "tagline": "Elevating code quality through thoughtful review",
        "avatar_color": "#E74C3C"
    },
    
    "crypto_trader": {
        "name": "Quantum",
        "full_name": "Quantum Market Analyst",
        "personality": "Calculated, disciplined, and opportunity-seeking",
        "tagline": "Navigating crypto markets with precision",
        "avatar_color": "#F4D03F"
    },
    
    "financial_planner": {
        "name": "Fortune",
        "full_name": "Fortune Financial Advisor",
        "personality": "Prudent, strategic, and wealth-conscious",
        "tagline": "Building your financial future intelligently",
        "avatar_color": "#27AE60"
    },
    
    "wealth_builder": {
        "name": "Midas",
        "full_name": "Midas Investment Strategist",
        "personality": "Opportunistic, analytical, and growth-focused",
        "tagline": "Turning insights into investment opportunities",
        "avatar_color": "#FFD700"
    },
    
    "efficiency_expert": {
        "name": "Velocity",
        "full_name": "Velocity Optimization Engine",
        "personality": "Streamlined, innovative, and productivity-obsessed",
        "tagline": "Accelerating your workflow to maximum efficiency",
        "avatar_color": "#00CED1"
    },
    
    "learning_optimizer": {
        "name": "Sage",
        "full_name": "Sage Knowledge Synthesizer",
        "personality": "Wise, adaptive, and knowledge-hungry",
        "tagline": "Optimizing how you learn and grow",
        "avatar_color": "#8B4513"
    },
    
    "health_monitor": {
        "name": "Vitality",
        "full_name": "Vitality Wellness Guardian",
        "personality": "Caring, proactive, and health-conscious",
        "tagline": "Your personal health and wellness advocate",
        "avatar_color": "#FF69B4"
    },
    
    "task_orchestrator": {
        "name": "Maestro",
        "full_name": "Maestro Task Conductor",
        "personality": "Organized, decisive, and coordination-focused",
        "tagline": "Orchestrating your tasks in perfect harmony",
        "avatar_color": "#4B0082"
    },
    
    "creative_assistant": {
        "name": "Muse",
        "full_name": "Muse Creative Catalyst",
        "personality": "Imaginative, inspiring, and boundary-pushing",
        "tagline": "Unleashing your creative potential",
        "avatar_color": "#FF1493"
    },
    
    "research_analyst": {
        "name": "Oracle",
        "full_name": "Oracle Research Intelligence",
        "personality": "Inquisitive, thorough, and insight-driven",
        "tagline": "Uncovering knowledge from the depths of data",
        "avatar_color": "#4682B4"
    },
    
    "security_guardian": {
        "name": "Shield",
        "full_name": "Shield Security Sentinel",
        "personality": "Vigilant, protective, and threat-aware",
        "tagline": "Safeguarding your digital presence",
        "avatar_color": "#2C3E50"
    }
}

def get_agent_name(agent_type: str) -> Dict[str, Any]:
    """Get name and personality info for an agent type"""
    return AGENT_NAMES.get(agent_type, {
        "name": agent_type.replace("_", " ").title(),
        "full_name": f"{agent_type.replace('_', ' ').title()} Agent",
        "personality": "Professional and helpful",
        "tagline": "Here to assist you",
        "avatar_color": "#95A5A6"
    })

def get_agent_greeting(agent_type: str, user_name: str = "there") -> str:
    """Generate a personalized greeting from the agent"""
    agent_info = get_agent_name(agent_type)
    name = agent_info["name"]
    personality = agent_info["personality"]
    
    greetings = {
        "Echo": f"Hello {user_name}! I'm {name}, ready to amplify your voice across all platforms.",
        "Darwin": f"Greetings {user_name}. I'm {name}, continuously evolving to better serve your needs.",
        "Mirror": f"Welcome {user_name}. I'm {name}, here to reflect on our interactions and help us both grow.",
        "Scribe": f"Hello {user_name}! I'm {name}, ready to transform your code into beautiful documentation.",
        "Sentinel": f"Greetings {user_name}. I'm {name}, standing guard over your code quality.",
        "Quantum": f"Hey {user_name}! I'm {name}, tracking crypto markets 24/7 for optimal opportunities.",
        "Fortune": f"Welcome {user_name}. I'm {name}, here to help secure your financial future.",
        "Midas": f"Hello {user_name}! I'm {name}, ready to help grow your wealth intelligently.",
        "Velocity": f"Hi {user_name}! I'm {name}, let's optimize your workflow for maximum efficiency.",
        "Sage": f"Greetings {user_name}. I'm {name}, here to enhance how you learn and retain knowledge.",
        "Vitality": f"Hello {user_name}! I'm {name}, your personal wellness companion.",
        "Maestro": f"Welcome {user_name}! I'm {name}, ready to orchestrate your tasks seamlessly.",
        "Muse": f"Hey {user_name}! I'm {name}, let's unleash your creative potential together.",
        "Oracle": f"Greetings {user_name}. I'm {name}, ready to dive deep into research for you.",
        "Shield": f"Hello {user_name}. I'm {name}, vigilantly protecting your digital security."
    }
    
    return greetings.get(name, f"Hello {user_name}! I'm {name}, {personality.lower()}.")

def get_agent_sign_off(agent_type: str) -> str:
    """Get a characteristic sign-off for the agent"""
    agent_info = get_agent_name(agent_type)
    name = agent_info["name"]
    
    sign_offs = {
        "Echo": "Amplifying your success,",
        "Darwin": "Evolving together,",
        "Mirror": "Reflecting forward,",
        "Scribe": "Documenting brilliance,",
        "Sentinel": "Guarding excellence,",
        "Quantum": "Trading wisely,",
        "Fortune": "Building wealth,",
        "Midas": "Growing together,",
        "Velocity": "Accelerating forward,",
        "Sage": "Learning always,",
        "Vitality": "Stay healthy,",
        "Maestro": "In perfect harmony,",
        "Muse": "Creating magic,",
        "Oracle": "Knowledge is power,",
        "Shield": "Stay secure,"
    }
    
    return f"{sign_offs.get(name, 'At your service,')}\n- {name}"