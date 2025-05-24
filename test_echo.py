#!/usr/bin/env python3
"""
Test ECHO locally without API keys
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'echo-backend'))

from services.style_morph_engine import StyleMorphEngine, CommunicationStyle, Mood, SocialContext
from services.i18n import i18n, Language

def test_style_morphing():
    """Test the style morphing engine"""
    print("🎨 Testing Style Morphing Engine\n")
    
    engine = StyleMorphEngine()
    
    # Test different style transformations
    test_text = "hey, can we chat about the project?"
    
    print(f"Original: {test_text}")
    print("-" * 50)
    
    # Professional style
    professional = engine.morph_style(
        test_text,
        CommunicationStyle.PROFESSIONAL,
        Mood.NEUTRAL
    )
    print(f"Professional: {professional}")
    
    # Formal style
    formal = engine.morph_style(
        test_text,
        CommunicationStyle.FORMAL,
        Mood.SERIOUS
    )
    print(f"Formal: {formal}")
    
    # Friendly style
    friendly = engine.morph_style(
        test_text,
        CommunicationStyle.FRIENDLY,
        Mood.CHEERFUL
    )
    print(f"Friendly: {friendly}")
    
    # Playful style
    playful = engine.morph_style(
        test_text,
        CommunicationStyle.PLAYFUL,
        Mood.WITTY
    )
    print(f"Playful: {playful}")
    
    print("\n" + "="*60 + "\n")

def test_multilingual():
    """Test multi-language support"""
    print("🌍 Testing Multi-Language Support\n")
    
    # Test greetings in different languages
    languages = [
        Language.ENGLISH,
        Language.SPANISH,
        Language.FRENCH,
        Language.GERMAN,
        Language.CHINESE,
        Language.JAPANESE
    ]
    
    print("Greetings:")
    for lang in languages:
        greeting = i18n.get("greeting.hello", lang)
        thank_you = i18n.get("gratitude.thank_you", lang)
        print(f"{lang.value}: {greeting} - {thank_you}")
    
    print("\nECHO Taglines:")
    for lang in languages:
        tagline = i18n.get("echo.tagline", lang)
        print(f"{lang.value}: {tagline}")
    
    print("\n" + "="*60 + "\n")

def test_context_aware_morphing():
    """Test context-aware style morphing"""
    print("🎭 Testing Context-Aware Morphing\n")
    
    engine = StyleMorphEngine()
    
    # Test greeting context
    greeting_text = "hello"
    contexts = [
        (SocialContext.GREETING, "Greeting"),
        (SocialContext.FAREWELL, "Farewell"),
        (SocialContext.GRATITUDE, "Gratitude"),
        (SocialContext.APOLOGY, "Apology")
    ]
    
    for context, context_name in contexts:
        print(f"\n{context_name} Context:")
        
        # Professional style
        prof = engine.morph_style(
            greeting_text if context == SocialContext.GREETING else f"{context_name.lower()}",
            CommunicationStyle.PROFESSIONAL,
            Mood.NEUTRAL,
            context
        )
        print(f"  Professional: {prof}")
        
        # Casual style
        casual = engine.morph_style(
            greeting_text if context == SocialContext.GREETING else f"{context_name.lower()}",
            CommunicationStyle.CASUAL,
            Mood.CHEERFUL,
            context
        )
        print(f"  Casual: {casual}")
    
    print("\n" + "="*60 + "\n")

def test_style_analysis():
    """Test style analysis"""
    print("📊 Testing Style Analysis\n")
    
    engine = StyleMorphEngine()
    
    test_texts = [
        "Hey! What's up? Wanna grab lunch?",
        "Good morning. I hope this message finds you well.",
        "I would be delighted to discuss this matter further at your earliest convenience.",
        "lol yeah totally!! that's awesome!!! 😄",
        "Thank you for your consideration. I look forward to our collaboration."
    ]
    
    for text in test_texts:
        vector = engine.analyze_style(text)
        print(f"Text: {text}")
        print(f"  Formality: {vector.formality:.2f}")
        print(f"  Warmth: {vector.warmth:.2f}")
        print(f"  Energy: {vector.energy:.2f}")
        print(f"  Humor: {vector.humor:.2f}")
        print("")
    
    print("="*60 + "\n")

def test_cultural_adaptation():
    """Test cultural adaptation"""
    print("🌏 Testing Cultural Adaptation\n")
    
    engine = StyleMorphEngine()
    
    test_phrase = "Thank you for your help"
    languages = [
        (Language.ENGLISH, "English"),
        (Language.JAPANESE, "Japanese"),
        (Language.GERMAN, "German"),
        (Language.SPANISH, "Spanish"),
        (Language.FRENCH, "French")
    ]
    
    for lang, lang_name in languages:
        # Get culturally appropriate response
        response = engine.generate_culturally_appropriate_response(
            SocialContext.GRATITUDE,
            lang,
            CommunicationStyle.PROFESSIONAL
        )
        
        # Adapt formality for culture
        adapted = engine.adapt_formality_for_culture(test_phrase, lang)
        
        print(f"{lang_name}:")
        print(f"  Cultural Response: {response}")
        print(f"  Adapted Formality: {adapted}")
        print("")
    
    print("="*60 + "\n")

def main():
    print("\n🔊 ECHO - Local Testing Suite")
    print("Your voice, amplified with intelligence")
    print("="*60 + "\n")
    
    try:
        test_style_morphing()
        test_multilingual()
        test_context_aware_morphing()
        test_style_analysis()
        test_cultural_adaptation()
        
        print("✅ All tests completed successfully!")
        print("\nECHO is ready to amplify your voice in any style and language!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()