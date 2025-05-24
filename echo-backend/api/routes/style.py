"""
Style morphing API routes
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

from services.style_morph_engine import (
    StyleMorphEngine, 
    CommunicationStyle, 
    Mood, 
    SocialContext,
    StyleVector
)

router = APIRouter()

# Initialize the style morph engine
style_engine = StyleMorphEngine()

class StyleMorphRequest(BaseModel):
    """Request model for style morphing"""
    text: str
    target_style: str
    mood: Optional[str] = "neutral"
    context: Optional[str] = None
    transition_speed: float = 0.5
    audience: Optional[str] = None

class StyleAnalysisRequest(BaseModel):
    """Request model for style analysis"""
    text: str
    compare_to: Optional[str] = None

class BatchMorphRequest(BaseModel):
    """Request model for batch morphing"""
    texts: List[str]
    target_style: str
    mood: Optional[str] = "neutral"
    maintain_consistency: bool = True

@router.post("/morph")
async def morph_text(request: StyleMorphRequest):
    """Morph text to target style"""
    try:
        # Parse enums
        target_style = CommunicationStyle(request.target_style)
        mood = Mood(request.mood)
        context = SocialContext(request.context) if request.context else None
        
        # Apply morphing
        morphed_text = style_engine.morph_style(
            text=request.text,
            target_style=target_style,
            mood=mood,
            context=context,
            transition_speed=request.transition_speed
        )
        
        # Get style analysis
        original_vector = style_engine.analyze_style(request.text)
        morphed_vector = style_engine.analyze_style(morphed_text)
        
        return {
            "original": request.text,
            "morphed": morphed_text,
            "style_change": {
                "from": original_vector.__dict__,
                "to": morphed_vector.__dict__,
                "distance": style_engine.get_style_distance(original_vector, morphed_vector)
            },
            "metadata": {
                "target_style": request.target_style,
                "mood": request.mood,
                "context": request.context,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid style parameter: {str(e)}")

@router.post("/analyze")
async def analyze_style(request: StyleAnalysisRequest):
    """Analyze communication style of text"""
    # Analyze the provided text
    style_vector = style_engine.analyze_style(request.text)
    
    # Find closest matching style
    closest_style = None
    min_distance = float('inf')
    
    for style, vector in style_engine.style_vectors.items():
        distance = style_engine.get_style_distance(style_vector, vector)
        if distance < min_distance:
            min_distance = distance
            closest_style = style
    
    result = {
        "text": request.text,
        "style_vector": style_vector.__dict__,
        "closest_style": closest_style.value,
        "confidence": max(0, 1 - min_distance / 2),  # Rough confidence score
        "characteristics": _describe_style_vector(style_vector)
    }
    
    # Compare to another text if provided
    if request.compare_to:
        compare_vector = style_engine.analyze_style(request.compare_to)
        result["comparison"] = {
            "text": request.compare_to,
            "style_vector": compare_vector.__dict__,
            "distance": style_engine.get_style_distance(style_vector, compare_vector),
            "similarity": max(0, 1 - style_engine.get_style_distance(style_vector, compare_vector) / 2)
        }
    
    return result

@router.post("/batch")
async def batch_morph(request: BatchMorphRequest):
    """Morph multiple texts maintaining consistency"""
    try:
        target_style = CommunicationStyle(request.target_style)
        mood = Mood(request.mood)
        
        results = []
        
        # Save current vector if maintaining consistency
        if request.maintain_consistency:
            saved_vector = style_engine.current_vector
        
        for text in request.texts:
            morphed = style_engine.morph_style(
                text=text,
                target_style=target_style,
                mood=mood,
                transition_speed=0.8 if request.maintain_consistency else 0.5
            )
            results.append({
                "original": text,
                "morphed": morphed
            })
        
        # Restore vector if needed
        if request.maintain_consistency:
            style_engine.current_vector = saved_vector
        
        return {
            "results": results,
            "count": len(results),
            "style": request.target_style,
            "mood": request.mood
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")

@router.get("/styles")
async def list_styles():
    """List available communication styles"""
    return {
        "styles": [
            {
                "name": style.value,
                "vector": vector.__dict__,
                "description": _get_style_description(style)
            }
            for style, vector in style_engine.style_vectors.items()
        ]
    }

@router.get("/moods")
async def list_moods():
    """List available moods"""
    return {
        "moods": [
            {
                "name": mood.value,
                "description": _get_mood_description(mood)
            }
            for mood in Mood
        ]
    }

@router.get("/contexts")
async def list_contexts():
    """List available social contexts"""
    return {
        "contexts": [
            {
                "name": context.value,
                "description": _get_context_description(context)
            }
            for context in SocialContext
        ]
    }

@router.post("/suggest")
async def suggest_style(audience: str, current_text: Optional[str] = None):
    """Suggest appropriate style for audience"""
    suggested_style, suggested_mood = style_engine.suggest_style_transition(
        current_text or "",
        audience
    )
    
    return {
        "audience": audience,
        "suggested_style": suggested_style.value,
        "suggested_mood": suggested_mood.value,
        "reasoning": _get_audience_reasoning(audience)
    }

@router.get("/history")
async def get_style_history(limit: int = 50):
    """Get recent style morphing history"""
    history = style_engine.style_history[-limit:]
    
    return {
        "history": [
            {
                "timestamp": h["timestamp"].isoformat(),
                "original": h["original"][:100] + "..." if len(h["original"]) > 100 else h["original"],
                "morphed": h["morphed"][:100] + "..." if len(h["morphed"]) > 100 else h["morphed"],
                "style": h["style"].value,
                "mood": h["mood"].value
            }
            for h in history
        ],
        "total": len(style_engine.style_history)
    }

# Helper functions

def _describe_style_vector(vector: StyleVector) -> Dict[str, str]:
    """Generate human-readable descriptions of style characteristics"""
    descriptions = {}
    
    if vector.formality > 0.7:
        descriptions["formality"] = "Very formal"
    elif vector.formality > 0.5:
        descriptions["formality"] = "Moderately formal"
    elif vector.formality > 0.3:
        descriptions["formality"] = "Slightly informal"
    else:
        descriptions["formality"] = "Very casual"
    
    if vector.warmth > 0.7:
        descriptions["warmth"] = "Very warm and friendly"
    elif vector.warmth > 0.5:
        descriptions["warmth"] = "Friendly"
    elif vector.warmth > 0.3:
        descriptions["warmth"] = "Neutral"
    else:
        descriptions["warmth"] = "Professional distance"
    
    if vector.energy > 0.7:
        descriptions["energy"] = "High energy"
    elif vector.energy > 0.5:
        descriptions["energy"] = "Moderate energy"
    else:
        descriptions["energy"] = "Calm and measured"
    
    if vector.verbosity > 0.7:
        descriptions["verbosity"] = "Elaborate"
    elif vector.verbosity > 0.5:
        descriptions["verbosity"] = "Detailed"
    else:
        descriptions["verbosity"] = "Concise"
    
    if vector.humor > 0.5:
        descriptions["humor"] = "Playful"
    else:
        descriptions["humor"] = "Serious"
    
    if vector.empathy > 0.7:
        descriptions["empathy"] = "Highly empathetic"
    elif vector.empathy > 0.5:
        descriptions["empathy"] = "Empathetic"
    else:
        descriptions["empathy"] = "Task-focused"
    
    return descriptions

def _get_style_description(style: CommunicationStyle) -> str:
    """Get description for communication style"""
    descriptions = {
        CommunicationStyle.PROFESSIONAL: "Balanced, workplace-appropriate communication",
        CommunicationStyle.CASUAL: "Relaxed, informal communication",
        CommunicationStyle.FORMAL: "Highly formal, traditional communication",
        CommunicationStyle.FRIENDLY: "Warm, approachable communication",
        CommunicationStyle.EMPATHETIC: "Understanding, emotionally aware communication",
        CommunicationStyle.ASSERTIVE: "Direct, confident communication",
        CommunicationStyle.PLAYFUL: "Light-hearted, fun communication",
        CommunicationStyle.SCHOLARLY: "Academic, intellectual communication"
    }
    return descriptions.get(style, "Standard communication style")

def _get_mood_description(mood: Mood) -> str:
    """Get description for mood"""
    descriptions = {
        Mood.NEUTRAL: "Balanced emotional tone",
        Mood.ENTHUSIASTIC: "Excited and energetic",
        Mood.CONTEMPLATIVE: "Thoughtful and reflective",
        Mood.CONCERNED: "Worried or caring",
        Mood.CHEERFUL: "Happy and positive",
        Mood.SERIOUS: "Focused and grave",
        Mood.WITTY: "Clever and humorous",
        Mood.SUPPORTIVE: "Encouraging and helpful"
    }
    return descriptions.get(mood, "Standard mood")

def _get_context_description(context: SocialContext) -> str:
    """Get description for social context"""
    descriptions = {
        SocialContext.GREETING: "Initial meeting or hello",
        SocialContext.FAREWELL: "Saying goodbye",
        SocialContext.GRATITUDE: "Expressing thanks",
        SocialContext.APOLOGY: "Expressing regret",
        SocialContext.CONGRATULATION: "Celebrating achievement",
        SocialContext.SYMPATHY: "Expressing condolences",
        SocialContext.INQUIRY: "Asking questions",
        SocialContext.RESPONSE: "Answering questions",
        SocialContext.SMALL_TALK: "Casual conversation",
        SocialContext.CONFLICT_RESOLUTION: "Resolving disagreements"
    }
    return descriptions.get(context, "General conversation")

def _get_audience_reasoning(audience: str) -> str:
    """Get reasoning for audience-based suggestions"""
    reasoning = {
        "boss": "Professional tone with clear communication for hierarchical relationship",
        "colleague": "Friendly but professional for peer collaboration",
        "client": "Professional with enthusiasm to build confidence",
        "friend": "Casual and warm for personal connection",
        "support_request": "Empathetic to acknowledge concerns",
        "academic": "Scholarly for intellectual discourse",
        "child": "Simple and playful for engagement",
        "elderly": "Respectful and clear for understanding"
    }
    return reasoning.get(audience.lower(), "Balanced approach for general audience")