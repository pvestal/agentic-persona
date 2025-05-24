"""
Internationalization (i18n) support for ECHO
Multi-language support for global communication
"""

from typing import Dict, Any, Optional
from enum import Enum
import json
from pathlib import Path

class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"

class I18nService:
    """Internationalization service for multi-language support"""
    
    def __init__(self):
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.default_language = Language.ENGLISH
        self.current_language = Language.ENGLISH
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files"""
        # In production, these would be loaded from JSON files
        # For now, defining inline
        self.translations = {
            Language.ENGLISH.value: {
                "greeting": {
                    "hello": "Hello",
                    "good_morning": "Good morning",
                    "good_afternoon": "Good afternoon",
                    "good_evening": "Good evening",
                    "welcome": "Welcome",
                    "how_are_you": "How are you?"
                },
                "farewell": {
                    "goodbye": "Goodbye",
                    "see_you_later": "See you later",
                    "take_care": "Take care",
                    "have_a_good_day": "Have a good day",
                    "until_next_time": "Until next time"
                },
                "gratitude": {
                    "thank_you": "Thank you",
                    "thanks": "Thanks",
                    "much_appreciated": "Much appreciated",
                    "grateful": "I'm grateful",
                    "thank_you_very_much": "Thank you very much"
                },
                "apology": {
                    "sorry": "Sorry",
                    "my_apologies": "My apologies",
                    "excuse_me": "Excuse me",
                    "pardon": "Pardon",
                    "forgive_me": "Please forgive me"
                },
                "affirmation": {
                    "yes": "Yes",
                    "no": "No",
                    "okay": "Okay",
                    "certainly": "Certainly",
                    "of_course": "Of course",
                    "absolutely": "Absolutely"
                },
                "echo": {
                    "tagline": "Your voice, amplified with intelligence",
                    "welcome_message": "Welcome to ECHO",
                    "learning_mode": "Learning from your communication style",
                    "suggest_mode": "Suggesting responses for you",
                    "draft_mode": "Drafting responses for approval",
                    "auto_mode": "Automatically handling responses"
                }
            },
            Language.SPANISH.value: {
                "greeting": {
                    "hello": "Hola",
                    "good_morning": "Buenos días",
                    "good_afternoon": "Buenas tardes",
                    "good_evening": "Buenas noches",
                    "welcome": "Bienvenido",
                    "how_are_you": "¿Cómo estás?"
                },
                "farewell": {
                    "goodbye": "Adiós",
                    "see_you_later": "Hasta luego",
                    "take_care": "Cuídate",
                    "have_a_good_day": "Que tengas un buen día",
                    "until_next_time": "Hasta la próxima"
                },
                "gratitude": {
                    "thank_you": "Gracias",
                    "thanks": "Gracias",
                    "much_appreciated": "Muy agradecido",
                    "grateful": "Estoy agradecido",
                    "thank_you_very_much": "Muchas gracias"
                },
                "apology": {
                    "sorry": "Lo siento",
                    "my_apologies": "Mis disculpas",
                    "excuse_me": "Disculpe",
                    "pardon": "Perdón",
                    "forgive_me": "Por favor perdóname"
                },
                "affirmation": {
                    "yes": "Sí",
                    "no": "No",
                    "okay": "Vale",
                    "certainly": "Ciertamente",
                    "of_course": "Por supuesto",
                    "absolutely": "Absolutamente"
                },
                "echo": {
                    "tagline": "Tu voz, amplificada con inteligencia",
                    "welcome_message": "Bienvenido a ECHO",
                    "learning_mode": "Aprendiendo de tu estilo de comunicación",
                    "suggest_mode": "Sugiriendo respuestas para ti",
                    "draft_mode": "Redactando respuestas para aprobación",
                    "auto_mode": "Manejando respuestas automáticamente"
                }
            },
            Language.FRENCH.value: {
                "greeting": {
                    "hello": "Bonjour",
                    "good_morning": "Bonjour",
                    "good_afternoon": "Bon après-midi",
                    "good_evening": "Bonsoir",
                    "welcome": "Bienvenue",
                    "how_are_you": "Comment allez-vous?"
                },
                "farewell": {
                    "goodbye": "Au revoir",
                    "see_you_later": "À plus tard",
                    "take_care": "Prenez soin de vous",
                    "have_a_good_day": "Bonne journée",
                    "until_next_time": "À la prochaine"
                },
                "gratitude": {
                    "thank_you": "Merci",
                    "thanks": "Merci",
                    "much_appreciated": "Très apprécié",
                    "grateful": "Je suis reconnaissant",
                    "thank_you_very_much": "Merci beaucoup"
                },
                "apology": {
                    "sorry": "Désolé",
                    "my_apologies": "Mes excuses",
                    "excuse_me": "Excusez-moi",
                    "pardon": "Pardon",
                    "forgive_me": "Veuillez me pardonner"
                },
                "affirmation": {
                    "yes": "Oui",
                    "no": "Non",
                    "okay": "D'accord",
                    "certainly": "Certainement",
                    "of_course": "Bien sûr",
                    "absolutely": "Absolument"
                },
                "echo": {
                    "tagline": "Votre voix, amplifiée avec intelligence",
                    "welcome_message": "Bienvenue à ECHO",
                    "learning_mode": "Apprendre de votre style de communication",
                    "suggest_mode": "Suggérer des réponses pour vous",
                    "draft_mode": "Rédiger des réponses pour approbation",
                    "auto_mode": "Gérer automatiquement les réponses"
                }
            },
            Language.GERMAN.value: {
                "greeting": {
                    "hello": "Hallo",
                    "good_morning": "Guten Morgen",
                    "good_afternoon": "Guten Tag",
                    "good_evening": "Guten Abend",
                    "welcome": "Willkommen",
                    "how_are_you": "Wie geht es Ihnen?"
                },
                "farewell": {
                    "goodbye": "Auf Wiedersehen",
                    "see_you_later": "Bis später",
                    "take_care": "Pass auf dich auf",
                    "have_a_good_day": "Schönen Tag noch",
                    "until_next_time": "Bis zum nächsten Mal"
                },
                "gratitude": {
                    "thank_you": "Danke",
                    "thanks": "Danke",
                    "much_appreciated": "Sehr geschätzt",
                    "grateful": "Ich bin dankbar",
                    "thank_you_very_much": "Vielen Dank"
                },
                "echo": {
                    "tagline": "Ihre Stimme, verstärkt mit Intelligenz",
                    "welcome_message": "Willkommen bei ECHO",
                    "learning_mode": "Lernen von Ihrem Kommunikationsstil",
                    "suggest_mode": "Antworten für Sie vorschlagen",
                    "draft_mode": "Antworten zur Genehmigung entwerfen",
                    "auto_mode": "Automatische Verwaltung von Antworten"
                }
            },
            Language.CHINESE.value: {
                "greeting": {
                    "hello": "你好",
                    "good_morning": "早上好",
                    "good_afternoon": "下午好",
                    "good_evening": "晚上好",
                    "welcome": "欢迎",
                    "how_are_you": "你好吗？"
                },
                "farewell": {
                    "goodbye": "再见",
                    "see_you_later": "回头见",
                    "take_care": "保重",
                    "have_a_good_day": "祝你今天愉快",
                    "until_next_time": "下次见"
                },
                "gratitude": {
                    "thank_you": "谢谢",
                    "thanks": "谢谢",
                    "much_appreciated": "非常感谢",
                    "grateful": "我很感激",
                    "thank_you_very_much": "非常感谢"
                },
                "echo": {
                    "tagline": "您的声音，用智能放大",
                    "welcome_message": "欢迎使用 ECHO",
                    "learning_mode": "学习您的沟通风格",
                    "suggest_mode": "为您建议回复",
                    "draft_mode": "起草回复待批准",
                    "auto_mode": "自动处理回复"
                }
            },
            Language.JAPANESE.value: {
                "greeting": {
                    "hello": "こんにちは",
                    "good_morning": "おはようございます",
                    "good_afternoon": "こんにちは",
                    "good_evening": "こんばんは",
                    "welcome": "ようこそ",
                    "how_are_you": "お元気ですか？"
                },
                "farewell": {
                    "goodbye": "さようなら",
                    "see_you_later": "また後で",
                    "take_care": "お気をつけて",
                    "have_a_good_day": "良い一日を",
                    "until_next_time": "また今度"
                },
                "gratitude": {
                    "thank_you": "ありがとう",
                    "thanks": "ありがとう",
                    "much_appreciated": "感謝しています",
                    "grateful": "感謝しています",
                    "thank_you_very_much": "どうもありがとうございます"
                },
                "echo": {
                    "tagline": "あなたの声を、知能で増幅",
                    "welcome_message": "ECHOへようこそ",
                    "learning_mode": "あなたのコミュニケーションスタイルを学習",
                    "suggest_mode": "返信を提案",
                    "draft_mode": "承認用の返信を下書き",
                    "auto_mode": "自動的に返信を処理"
                }
            }
        }
    
    def get(self, key: str, language: Optional[Language] = None) -> str:
        """Get translated text for a key"""
        lang = (language or self.current_language).value
        
        # Navigate nested keys (e.g., "greeting.hello")
        keys = key.split('.')
        translation = self.translations.get(lang, {})
        
        for k in keys:
            if isinstance(translation, dict):
                translation = translation.get(k)
            else:
                break
        
        # Fallback to English if translation not found
        if translation is None and lang != self.default_language.value:
            return self.get(key, self.default_language)
        
        return translation or key
    
    def set_language(self, language: Language):
        """Set current language"""
        self.current_language = language
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get list of available languages"""
        return {
            lang.value: lang.name.title() 
            for lang in Language
        }
    
    def translate_style_morphing(
        self, 
        text: str, 
        source_lang: Language, 
        target_lang: Language,
        maintain_style: bool = True
    ) -> str:
        """Translate text while maintaining communication style"""
        # This would use a translation API in production
        # For now, returning a placeholder
        return f"[{target_lang.value}] {text}"
    
    def detect_language(self, text: str) -> Language:
        """Detect language of text"""
        # Simple detection based on character sets
        # In production, use a proper language detection library
        
        # Check for Chinese characters
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            return Language.CHINESE
        
        # Check for Japanese characters
        if any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text):
            return Language.JAPANESE
        
        # Check for Korean characters
        if any('\uac00' <= char <= '\ud7af' for char in text):
            return Language.KOREAN
        
        # Check for Arabic characters
        if any('\u0600' <= char <= '\u06ff' for char in text):
            return Language.ARABIC
        
        # Check for Cyrillic (Russian)
        if any('\u0400' <= char <= '\u04ff' for char in text):
            return Language.RUSSIAN
        
        # Default to English for Latin scripts
        return Language.ENGLISH
    
    def get_greeting_for_time(self, hour: int, language: Optional[Language] = None) -> str:
        """Get appropriate greeting based on time of day"""
        lang = language or self.current_language
        
        if 5 <= hour < 12:
            return self.get("greeting.good_morning", lang)
        elif 12 <= hour < 17:
            return self.get("greeting.good_afternoon", lang)
        elif 17 <= hour < 22:
            return self.get("greeting.good_evening", lang)
        else:
            return self.get("greeting.hello", lang)
    
    def localize_autonomy_level(self, level: str, language: Optional[Language] = None) -> str:
        """Localize autonomy level descriptions"""
        lang = language or self.current_language
        
        level_keys = {
            "learn": "echo.learning_mode",
            "suggest": "echo.suggest_mode",
            "draft": "echo.draft_mode",
            "auto_send": "echo.auto_mode"
        }
        
        return self.get(level_keys.get(level, "echo.learning_mode"), lang)

# Global instance
i18n = I18nService()