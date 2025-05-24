"""
Internationalization API routes
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Optional, List
from pydantic import BaseModel

from services.i18n import i18n, Language
from services.style_morph_engine import StyleMorphEngine, CommunicationStyle, Mood, SocialContext

router = APIRouter()
style_engine = StyleMorphEngine()

class TranslationRequest(BaseModel):
    """Translation request model"""
    text: str
    target_language: str
    source_language: Optional[str] = None
    maintain_style: bool = True

class MultilingualMorphRequest(BaseModel):
    """Multilingual style morphing request"""
    text: str
    target_style: str
    mood: Optional[str] = "neutral"
    context: Optional[str] = None
    source_language: Optional[str] = None
    target_language: str = "en"
    transition_speed: float = 0.5

class LanguageDetectionRequest(BaseModel):
    """Language detection request"""
    text: str

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": i18n.get_available_languages(),
        "default": i18n.default_language.value,
        "current": i18n.current_language.value
    }

@router.post("/set-language")
async def set_current_language(language_code: str):
    """Set current language for the session"""
    try:
        language = Language(language_code)
        i18n.set_language(language)
        return {
            "success": True,
            "language": language.value,
            "name": language.name.title()
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language_code}")

@router.post("/translate")
async def translate_text(request: TranslationRequest):
    """Translate text to target language"""
    try:
        # Parse languages
        target_lang = Language(request.target_language)
        source_lang = Language(request.source_language) if request.source_language else None
        
        # Detect source language if not provided
        if not source_lang:
            source_lang = i18n.detect_language(request.text)
        
        # Translate
        translated = i18n.translate_style_morphing(
            request.text,
            source_lang,
            target_lang,
            request.maintain_style
        )
        
        return {
            "original": request.text,
            "translated": translated,
            "source_language": source_lang.value,
            "target_language": target_lang.value
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/detect")
async def detect_language(request: LanguageDetectionRequest):
    """Detect language of text"""
    detected = i18n.detect_language(request.text)
    
    return {
        "text": request.text,
        "detected_language": detected.value,
        "language_name": detected.name.title(),
        "confidence": 0.95  # Placeholder - would use actual confidence from detection
    }

@router.post("/morph-multilingual")
async def morph_multilingual(request: MultilingualMorphRequest):
    """Morph text style with language translation"""
    try:
        # Parse parameters
        target_style = CommunicationStyle(request.target_style)
        mood = Mood(request.mood)
        context = SocialContext(request.context) if request.context else None
        source_lang = Language(request.source_language) if request.source_language else Language.ENGLISH
        target_lang = Language(request.target_language)
        
        # Perform multilingual morphing
        result = style_engine.morph_style_multilingual(
            text=request.text,
            target_style=target_style,
            mood=mood,
            context=context,
            source_language=source_lang,
            target_language=target_lang,
            transition_speed=request.transition_speed
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")

@router.get("/greeting/{language_code}")
async def get_time_based_greeting(
    language_code: str,
    hour: Optional[int] = None
):
    """Get appropriate greeting based on time and language"""
    try:
        language = Language(language_code)
        
        # Use current hour if not provided
        if hour is None:
            from datetime import datetime
            hour = datetime.now().hour
        
        greeting = i18n.get_greeting_for_time(hour, language)
        
        return {
            "greeting": greeting,
            "language": language.value,
            "hour": hour,
            "time_period": (
                "morning" if 5 <= hour < 12 else
                "afternoon" if 12 <= hour < 17 else
                "evening" if 17 <= hour < 22 else
                "night"
            )
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language_code}")

@router.get("/echo-messages/{language_code}")
async def get_echo_messages(language_code: str):
    """Get ECHO-specific messages in a language"""
    try:
        language = Language(language_code)
        
        return {
            "language": language.value,
            "messages": {
                "tagline": i18n.get("echo.tagline", language),
                "welcome": i18n.get("echo.welcome_message", language),
                "autonomy_levels": {
                    "learn": i18n.get("echo.learning_mode", language),
                    "suggest": i18n.get("echo.suggest_mode", language),
                    "draft": i18n.get("echo.draft_mode", language),
                    "auto": i18n.get("echo.auto_mode", language)
                }
            }
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language_code}")

@router.post("/cultural-response")
async def generate_cultural_response(
    context: str,
    language: str,
    style: str,
    additional_context: Optional[Dict[str, str]] = None
):
    """Generate culturally appropriate response"""
    try:
        # Parse parameters
        social_context = SocialContext(context)
        lang = Language(language)
        comm_style = CommunicationStyle(style)
        
        # Generate response
        response = style_engine.generate_culturally_appropriate_response(
            context=social_context,
            language=lang,
            style=comm_style,
            additional_context=additional_context
        )
        
        return {
            "response": response,
            "context": context,
            "language": language,
            "style": style,
            "cultural_notes": _get_cultural_notes(lang)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

def _get_cultural_notes(language: Language) -> Dict[str, str]:
    """Get cultural communication notes for a language"""
    cultural_notes = {
        Language.JAPANESE: {
            "formality": "High formality expected in most contexts",
            "honorifics": "Use appropriate honorifics (san, sama)",
            "indirectness": "Prefer indirect communication"
        },
        Language.GERMAN: {
            "formality": "Use Sie (formal you) unless invited to use du",
            "punctuality": "Time consciousness is important",
            "directness": "Direct communication is appreciated"
        },
        Language.SPANISH: {
            "warmth": "Warmer, more personal communication style",
            "greetings": "Greetings are important social rituals",
            "formality": "Less formal than English in many contexts"
        },
        Language.FRENCH: {
            "politeness": "Politeness formulas are essential",
            "greetings": "Always greet before any interaction",
            "formality": "Maintain appropriate social distance"
        },
        Language.CHINESE: {
            "face": "Maintaining face is crucial",
            "hierarchy": "Respect hierarchical relationships",
            "indirectness": "Indirect refusals are common"
        }
    }
    
    return cultural_notes.get(language, {
        "general": "Standard communication norms apply"
    })