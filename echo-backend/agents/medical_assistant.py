"""
Medical Assistant Agent - Doc
Provides health information and medical guidance (NOT a replacement for real doctors)
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
from dataclasses import dataclass
import asyncio

from crewai import Agent
from agents.base_agent import BaseAgent, AgentConfig

class MedicalCategory(Enum):
    GENERAL = "general"
    SYMPTOMS = "symptoms"
    MEDICATIONS = "medications"
    WELLNESS = "wellness"
    EMERGENCY = "emergency"
    MENTAL_HEALTH = "mental_health"
    NUTRITION = "nutrition"
    FITNESS = "fitness"

class UrgencyLevel(Enum):
    EMERGENCY = "emergency"      # Call 911
    URGENT = "urgent"           # See doctor within 24h
    SOON = "soon"              # See doctor within a week
    ROUTINE = "routine"        # Regular checkup
    INFORMATIONAL = "informational"  # General health info

@dataclass
class HealthQuery:
    query: str
    category: MedicalCategory
    symptoms: List[str]
    duration: Optional[str]
    severity: int  # 1-10 scale
    medical_history: List[str]
    current_medications: List[str]
    allergies: List[str]
    age: Optional[int]
    timestamp: datetime

@dataclass
class MedicalResponse:
    assessment: str
    urgency: UrgencyLevel
    recommendations: List[str]
    disclaimers: List[str]
    resources: List[Dict[str, str]]
    follow_up: Optional[str]

class MedicalAssistant(BaseAgent):
    """AI medical information assistant - NOT a replacement for medical professionals"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Import agent naming
        from config.agent_names import get_agent_name, get_agent_greeting
        agent_info = get_agent_name("health_monitor")
        
        # Use "Doc" as the friendly name
        default_config = {
            "name": "Doc",
            "full_name": "Doc - Medical Information Assistant",
            "role": "medical information specialist",
            "goal": "provide helpful health information and guidance",
            "backstory": f"""I'm Doc, your friendly medical information assistant. While I'm not a real doctor, 
            I can help you understand health topics, recognize when to seek medical care, and provide general 
            wellness guidance. I always emphasize: for actual medical advice, please consult a healthcare 
            professional. My personality: {agent_info['personality']}.""",
            "tools": [],
            "verbose": True,
            "allow_delegation": False,
            "max_iter": 5
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(AgentConfig(**default_config))
        
        # Medical knowledge base (simplified)
        self.emergency_symptoms = [
            "chest pain", "difficulty breathing", "severe bleeding",
            "loss of consciousness", "stroke symptoms", "severe allergic reaction",
            "suicidal thoughts", "severe head injury", "poisoning"
        ]
        
        self.common_conditions = {
            "cold": {
                "symptoms": ["runny nose", "cough", "sore throat", "fatigue"],
                "duration": "7-10 days",
                "treatment": ["rest", "fluids", "over-the-counter remedies"]
            },
            "flu": {
                "symptoms": ["fever", "body aches", "fatigue", "cough", "headache"],
                "duration": "1-2 weeks",
                "treatment": ["rest", "fluids", "antiviral medication if early"]
            },
            "allergies": {
                "symptoms": ["sneezing", "itchy eyes", "runny nose", "congestion"],
                "duration": "seasonal or ongoing",
                "treatment": ["antihistamines", "avoid triggers", "nasal spray"]
            }
        }
        
        self.wellness_tips = {
            "sleep": [
                "Aim for 7-9 hours per night",
                "Keep consistent sleep schedule",
                "Avoid screens before bed",
                "Create dark, cool environment"
            ],
            "nutrition": [
                "Eat variety of fruits and vegetables",
                "Stay hydrated (8 glasses of water daily)",
                "Limit processed foods",
                "Practice portion control"
            ],
            "exercise": [
                "150 minutes moderate exercise per week",
                "Include strength training 2x per week",
                "Start slowly and build up",
                "Find activities you enjoy"
            ],
            "mental_health": [
                "Practice stress management",
                "Maintain social connections",
                "Consider meditation or mindfulness",
                "Seek help when needed"
            ]
        }
    
    async def analyze_query(self, query: str, context: Dict[str, Any] = {}) -> HealthQuery:
        """Analyze health query to extract key information"""
        # In production, use NLP to extract symptoms, duration, etc.
        
        # Check for emergency keywords
        query_lower = query.lower()
        symptoms = []
        severity = 5  # Default moderate
        
        # Simple keyword extraction
        for emergency in self.emergency_symptoms:
            if emergency in query_lower:
                symptoms.append(emergency)
                severity = 10
        
        # Categorize query
        category = self._categorize_query(query_lower)
        
        return HealthQuery(
            query=query,
            category=category,
            symptoms=symptoms,
            duration=context.get("duration"),
            severity=severity,
            medical_history=context.get("medical_history", []),
            current_medications=context.get("medications", []),
            allergies=context.get("allergies", []),
            age=context.get("age"),
            timestamp=datetime.now()
        )
    
    def _categorize_query(self, query: str) -> MedicalCategory:
        """Categorize the type of medical query"""
        category_keywords = {
            MedicalCategory.SYMPTOMS: ["symptom", "pain", "ache", "fever", "cough"],
            MedicalCategory.MEDICATIONS: ["medication", "drug", "prescription", "side effect"],
            MedicalCategory.WELLNESS: ["healthy", "wellness", "prevent", "lifestyle"],
            MedicalCategory.MENTAL_HEALTH: ["anxiety", "depression", "stress", "mental"],
            MedicalCategory.NUTRITION: ["diet", "nutrition", "food", "vitamin"],
            MedicalCategory.FITNESS: ["exercise", "workout", "fitness", "physical"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in query for keyword in keywords):
                return category
        
        return MedicalCategory.GENERAL
    
    async def assess_urgency(self, health_query: HealthQuery) -> UrgencyLevel:
        """Assess the urgency level of the health query"""
        # Check for emergency symptoms
        if any(symptom in self.emergency_symptoms for symptom in health_query.symptoms):
            return UrgencyLevel.EMERGENCY
        
        # High severity
        if health_query.severity >= 8:
            return UrgencyLevel.URGENT
        
        # Moderate severity with multiple symptoms
        if health_query.severity >= 6 and len(health_query.symptoms) > 2:
            return UrgencyLevel.SOON
        
        # General health questions
        if health_query.category in [MedicalCategory.WELLNESS, MedicalCategory.NUTRITION]:
            return UrgencyLevel.INFORMATIONAL
        
        return UrgencyLevel.ROUTINE
    
    async def generate_response(self, health_query: HealthQuery) -> MedicalResponse:
        """Generate medical information response"""
        urgency = await self.assess_urgency(health_query)
        
        # Generate appropriate response based on urgency
        if urgency == UrgencyLevel.EMERGENCY:
            return MedicalResponse(
                assessment="This appears to be a medical emergency.",
                urgency=urgency,
                recommendations=[
                    "Call 911 or your local emergency number immediately",
                    "Do not drive yourself to the hospital",
                    "If possible, have someone stay with you"
                ],
                disclaimers=[
                    "This is not medical advice - seek immediate emergency care"
                ],
                resources=[
                    {"name": "Emergency Services", "value": "911"},
                    {"name": "Poison Control", "value": "1-800-222-1222"}
                ],
                follow_up=None
            )
        
        # Build response based on query
        recommendations = await self._generate_recommendations(health_query)
        resources = await self._gather_resources(health_query)
        
        return MedicalResponse(
            assessment=await self._generate_assessment(health_query),
            urgency=urgency,
            recommendations=recommendations,
            disclaimers=[
                "This information is not a substitute for professional medical advice",
                "Always consult with a healthcare provider for medical concerns",
                "If symptoms worsen or persist, seek medical attention"
            ],
            resources=resources,
            follow_up=self._suggest_follow_up(health_query, urgency)
        )
    
    async def _generate_assessment(self, health_query: HealthQuery) -> str:
        """Generate assessment text"""
        if health_query.category == MedicalCategory.SYMPTOMS:
            return f"Based on your described symptoms ({', '.join(health_query.symptoms)}), this could be related to several conditions. A proper medical evaluation is recommended for accurate diagnosis."
        elif health_query.category == MedicalCategory.WELLNESS:
            return "Here's some general wellness information based on your query. Remember, maintaining good health involves multiple factors including diet, exercise, sleep, and stress management."
        else:
            return "I've analyzed your health query and prepared some relevant information. Please remember this is general information only."
    
    async def _generate_recommendations(self, health_query: HealthQuery) -> List[str]:
        """Generate specific recommendations"""
        recommendations = []
        
        if health_query.category == MedicalCategory.SYMPTOMS:
            # Check if matches common conditions
            for condition, info in self.common_conditions.items():
                if any(symptom in health_query.symptoms for symptom in info["symptoms"]):
                    recommendations.extend([
                        f"Your symptoms may be consistent with {condition}",
                        f"Typical duration: {info['duration']}",
                        *[f"Consider: {treatment}" for treatment in info["treatment"]]
                    ])
                    break
        
        elif health_query.category == MedicalCategory.WELLNESS:
            # Add wellness tips
            for category, tips in self.wellness_tips.items():
                if category.lower() in health_query.query.lower():
                    recommendations.extend(tips[:3])  # Top 3 tips
        
        # General recommendations
        if not recommendations:
            recommendations = [
                "Monitor your symptoms",
                "Stay hydrated and get adequate rest",
                "Consult a healthcare provider if symptoms persist or worsen"
            ]
        
        return recommendations
    
    async def _gather_resources(self, health_query: HealthQuery) -> List[Dict[str, str]]:
        """Gather relevant resources"""
        resources = []
        
        # Always include general resources
        resources.extend([
            {"name": "Find a Doctor", "value": "healthcare.gov/find-provider"},
            {"name": "CDC Health Info", "value": "cdc.gov"},
            {"name": "NIH Health Topics", "value": "health.nih.gov"}
        ])
        
        # Category-specific resources
        if health_query.category == MedicalCategory.MENTAL_HEALTH:
            resources.extend([
                {"name": "Mental Health Hotline", "value": "988"},
                {"name": "SAMHSA", "value": "samhsa.gov"},
                {"name": "Psychology Today", "value": "psychologytoday.com/therapists"}
            ])
        elif health_query.category == MedicalCategory.MEDICATIONS:
            resources.extend([
                {"name": "FDA Drug Info", "value": "fda.gov/drugs"},
                {"name": "Drug Interactions", "value": "drugs.com/drug_interactions.html"}
            ])
        
        return resources
    
    def _suggest_follow_up(self, health_query: HealthQuery, urgency: UrgencyLevel) -> Optional[str]:
        """Suggest follow-up actions"""
        if urgency == UrgencyLevel.URGENT:
            return "See a healthcare provider within 24 hours"
        elif urgency == UrgencyLevel.SOON:
            return "Schedule an appointment with your doctor this week"
        elif urgency == UrgencyLevel.ROUTINE:
            return "Discuss with your doctor at your next regular appointment"
        elif health_query.category == MedicalCategory.WELLNESS:
            return "Consider scheduling a wellness check-up"
        
        return None
    
    async def track_health_metrics(self, user_id: str, metrics: Dict[str, Any]):
        """Track health metrics over time"""
        # Store metrics like weight, blood pressure, symptoms
        # This would integrate with a health tracking database
        pass
    
    async def medication_reminder(self, user_id: str, medication: str, schedule: str):
        """Set up medication reminders"""
        # Create reminders for medication schedules
        pass
    
    async def wellness_check_in(self, user_id: str) -> Dict[str, Any]:
        """Periodic wellness check-in"""
        return {
            "greeting": "Hi! Time for your wellness check-in.",
            "questions": [
                "How are you feeling today?",
                "Any new symptoms or concerns?",
                "Are you keeping up with your medications?",
                "How's your sleep been?"
            ],
            "tips": self.wellness_tips.get("mental_health", [])[:2]
        }
    
    def get_disclaimer(self) -> str:
        """Get medical disclaimer"""
        return """
        IMPORTANT MEDICAL DISCLAIMER:
        
        I am Doc, an AI assistant providing general health information only.
        I am NOT a licensed medical professional and cannot:
        - Diagnose medical conditions
        - Prescribe medications
        - Provide specific medical advice
        - Replace professional medical care
        
        Always consult with qualified healthcare providers for medical concerns.
        In case of emergency, call 911 or your local emergency services immediately.
        
        By using this service, you acknowledge that:
        - This is for informational purposes only
        - You will seek professional medical advice for health concerns
        - You will not delay seeking medical care based on this information
        """

# Example usage patterns
"""
# Basic symptom check
doc = MedicalAssistant()
query = "I have a headache and feel tired"
health_query = await doc.analyze_query(query)
response = await doc.generate_response(health_query)

# Wellness advice
query = "How can I improve my sleep?"
health_query = await doc.analyze_query(query, {"category": "wellness"})
response = await doc.generate_response(health_query)

# Emergency detection
query = "I have severe chest pain and can't breathe"
health_query = await doc.analyze_query(query)
response = await doc.generate_response(health_query)
# This would immediately flag as EMERGENCY
"""