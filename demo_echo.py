#!/usr/bin/env python3
"""
Interactive ECHO Demo - Test without API keys
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'echo-backend'))

from services.style_morph_engine import StyleMorphEngine, CommunicationStyle, Mood, SocialContext
from services.i18n import i18n, Language

def print_header():
    """Print ECHO header"""
    print("\n" + "="*60)
    print("🔊 ECHO - Interactive Demo")
    print("Your voice, amplified with intelligence")
    print("="*60 + "\n")

def get_user_choice(options, prompt):
    """Get user choice from options"""
    print(prompt)
    for i, (key, value) in enumerate(options.items(), 1):
        print(f"{i}. {value}")
    
    while True:
        try:
            choice = int(input("\nEnter choice (number): "))
            if 1 <= choice <= len(options):
                return list(options.keys())[choice - 1]
        except ValueError:
            pass
        print("Invalid choice. Please try again.")

def demo_style_morphing():
    """Interactive style morphing demo"""
    engine = StyleMorphEngine()
    
    print("\n🎨 Style Morphing Demo")
    print("-" * 40)
    
    # Get user input
    text = input("\nEnter text to morph (or press Enter for default): ").strip()
    if not text:
        text = "hey, can we discuss the new project proposal?"
    
    # Choose style
    styles = {
        CommunicationStyle.PROFESSIONAL: "Professional",
        CommunicationStyle.CASUAL: "Casual",
        CommunicationStyle.FORMAL: "Formal",
        CommunicationStyle.FRIENDLY: "Friendly",
        CommunicationStyle.EMPATHETIC: "Empathetic",
        CommunicationStyle.ASSERTIVE: "Assertive",
        CommunicationStyle.PLAYFUL: "Playful",
        CommunicationStyle.SCHOLARLY: "Scholarly"
    }
    
    style = get_user_choice(styles, "\nChoose communication style:")
    
    # Choose mood
    moods = {
        Mood.NEUTRAL: "Neutral",
        Mood.ENTHUSIASTIC: "Enthusiastic",
        Mood.CONTEMPLATIVE: "Contemplative",
        Mood.CONCERNED: "Concerned",
        Mood.CHEERFUL: "Cheerful",
        Mood.SERIOUS: "Serious",
        Mood.WITTY: "Witty",
        Mood.SUPPORTIVE: "Supportive"
    }
    
    mood = get_user_choice(moods, "\nChoose mood:")
    
    # Morph the text
    morphed = engine.morph_style(text, style, mood)
    
    print(f"\n{'Original:':<15} {text}")
    print(f"{'Style:':<15} {styles[style]}")
    print(f"{'Mood:':<15} {moods[mood]}")
    print(f"{'Morphed:':<15} {morphed}")
    
    # Analyze both texts
    original_vector = engine.analyze_style(text)
    morphed_vector = engine.analyze_style(morphed)
    
    print("\nStyle Analysis:")
    print(f"{'Metric':<15} {'Original':>10} {'Morphed':>10} {'Change':>10}")
    print("-" * 45)
    
    metrics = ['formality', 'warmth', 'energy', 'verbosity', 'humor', 'empathy']
    for metric in metrics:
        orig_val = getattr(original_vector, metric)
        morph_val = getattr(morphed_vector, metric)
        change = morph_val - orig_val
        print(f"{metric.capitalize():<15} {orig_val:>10.2f} {morph_val:>10.2f} {change:>+10.2f}")

def demo_multilingual():
    """Interactive multilingual demo"""
    print("\n🌍 Multilingual Demo")
    print("-" * 40)
    
    # Choose language
    languages = {
        Language.ENGLISH: "English",
        Language.SPANISH: "Spanish",
        Language.FRENCH: "French",
        Language.GERMAN: "German",
        Language.ITALIAN: "Italian",
        Language.PORTUGUESE: "Portuguese",
        Language.CHINESE: "Chinese",
        Language.JAPANESE: "Japanese",
        Language.KOREAN: "Korean",
        Language.RUSSIAN: "Russian",
        Language.ARABIC: "Arabic",
        Language.HINDI: "Hindi"
    }
    
    lang = get_user_choice(languages, "\nChoose language:")
    
    # Display common phrases
    print(f"\nCommon phrases in {languages[lang]}:")
    print("-" * 30)
    
    phrases = [
        ("greeting.hello", "Hello"),
        ("greeting.good_morning", "Good morning"),
        ("greeting.how_are_you", "How are you?"),
        ("farewell.goodbye", "Goodbye"),
        ("farewell.see_you_later", "See you later"),
        ("gratitude.thank_you", "Thank you"),
        ("gratitude.thank_you_very_much", "Thank you very much"),
        ("apology.sorry", "Sorry"),
        ("affirmation.yes", "Yes"),
        ("affirmation.no", "No"),
        ("echo.tagline", "ECHO Tagline")
    ]
    
    for key, english in phrases:
        translation = i18n.get(key, lang)
        print(f"{english:<25} → {translation}")

def demo_cultural_adaptation():
    """Demo cultural adaptation"""
    engine = StyleMorphEngine()
    
    print("\n🌏 Cultural Adaptation Demo")
    print("-" * 40)
    
    # Get greeting for current time
    from datetime import datetime
    hour = datetime.now().hour
    
    print(f"\nTime-based greetings (Current hour: {hour}:00):")
    print("-" * 40)
    
    for lang in [Language.ENGLISH, Language.SPANISH, Language.JAPANESE, Language.GERMAN]:
        greeting = i18n.get_greeting_for_time(hour, lang)
        print(f"{lang.value:>10}: {greeting}")
    
    # Show cultural formality differences
    print("\nCultural Formality Adaptation:")
    print("-" * 40)
    
    test_phrase = "Thank you for meeting with me"
    
    for lang in [Language.ENGLISH, Language.JAPANESE, Language.SPANISH, Language.GERMAN]:
        adapted = engine.adapt_formality_for_culture(test_phrase, lang)
        cultural_response = engine.generate_culturally_appropriate_response(
            SocialContext.GRATITUDE,
            lang,
            CommunicationStyle.PROFESSIONAL
        )
        print(f"\n{lang.name}:")
        print(f"  Original: {test_phrase}")
        print(f"  Adapted: {adapted}")
        print(f"  Cultural: {cultural_response}")

def main_menu():
    """Main demo menu"""
    while True:
        print_header()
        
        print("Choose a demo:")
        print("1. Style Morphing - Transform text between communication styles")
        print("2. Multilingual - See ECHO speak in 12 languages")
        print("3. Cultural Adaptation - Experience culturally-aware communication")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            demo_style_morphing()
            input("\nPress Enter to continue...")
        elif choice == '2':
            demo_multilingual()
            input("\nPress Enter to continue...")
        elif choice == '3':
            demo_cultural_adaptation()
            input("\nPress Enter to continue...")
        elif choice == '4':
            print("\n👋 Thank you for trying ECHO!")
            print("Your voice, amplified with intelligence.\n")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")