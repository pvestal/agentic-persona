"""
Learning system API routes
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from services.learning_system import learning_system, FeedbackType

router = APIRouter()


class FeedbackRequest(BaseModel):
    """Feedback submission model"""
    message_id: str
    feedback_type: str  # approved, rejected, edited, rating
    original_response: str
    edited_response: Optional[str] = None
    rating: Optional[float] = None
    context: Optional[Dict[str, Any]] = None


class PreferencesResponse(BaseModel):
    """User preferences response"""
    communication_style: str
    response_length: str
    tone_preferences: Dict[str, float]
    platform_preferences: Dict[str, Any]


@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback on a response"""
    try:
        # Convert string to enum
        feedback_type = FeedbackType(feedback.feedback_type)
        
        result = await learning_system.record_feedback(
            message_id=feedback.message_id,
            feedback_type=feedback_type,
            original_response=feedback.original_response,
            edited_response=feedback.edited_response,
            rating=feedback.rating,
            context=feedback.context
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid feedback type: {feedback.feedback_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/improve-response")
async def improve_response(
    message: str,
    initial_response: str,
    context: Optional[Dict[str, Any]] = None
):
    """Get improvements for a response based on learning data"""
    try:
        improvements = await learning_system.get_response_improvements(
            message=message,
            initial_response=initial_response,
            context=context or {}
        )
        
        return improvements
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """Get learned preferences for a user"""
    try:
        preferences = await learning_system.get_user_preferences(user_id)
        
        return PreferencesResponse(
            communication_style=preferences.get("communication_style", "balanced"),
            response_length=preferences.get("response_length", "concise"),
            tone_preferences=preferences.get("tone_preferences", {}),
            platform_preferences=preferences.get("platform_preferences", {})
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_learning_trends(days: int = 30):
    """Get learning trends and analytics"""
    try:
        time_range = timedelta(days=days)
        trends = await learning_system.analyze_learning_trends(time_range)
        
        return {
            "time_range_days": days,
            "trends": trends,
            "last_analysis": learning_system.last_analysis.isoformat() if learning_system.last_analysis else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights")
async def get_learning_insights():
    """Get current learning insights"""
    try:
        return {
            "insights": learning_system.insight_cache,
            "pattern_count": len(learning_system.pattern_cache),
            "total_feedback_entries": sum(
                len(data["features"]) for data in learning_system.pattern_cache.values()
            )
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply-learning")
async def apply_learning_to_message(
    message: str,
    platform: str = "generic",
    sender: Optional[str] = None
):
    """Apply learning to generate an optimized response"""
    try:
        # Get learned preferences
        preferences = {}
        if sender:
            preferences = await learning_system.get_user_preferences(sender)
        
        context = {
            "platform": platform,
            "sender": sender or "unknown",
            "preferences": preferences
        }
        
        # Generate initial response (simplified for demo)
        initial_response = f"Thank you for your message. I'll help you with that."
        
        # Apply improvements
        improvements = await learning_system.get_response_improvements(
            message=message,
            initial_response=initial_response,
            context=context
        )
        
        return {
            "initial_response": initial_response,
            "improved_response": improvements.get("improved_response", initial_response),
            "improvements_applied": improvements,
            "confidence": improvements.get("confidence", 0.0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))