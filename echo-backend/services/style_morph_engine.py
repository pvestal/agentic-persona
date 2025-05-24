"""
Style Morph Engine - Dynamic Communication Style Adaptation
Morphs between different communication styles, moods, and social contexts
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime
import numpy as np
from .i18n import i18n, Language

class CommunicationStyle(Enum):
    """Base communication styles"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FORMAL = "formal"
    FRIENDLY = "friendly"
    EMPATHETIC = "empathetic"
    ASSERTIVE = "assertive"
    PLAYFUL = "playful"
    SCHOLARLY = "scholarly"

class Mood(Enum):
    """Emotional moods that color communication"""
    NEUTRAL = "neutral"
    ENTHUSIASTIC = "enthusiastic"
    CONTEMPLATIVE = "contemplative"
    CONCERNED = "concerned"
    CHEERFUL = "cheerful"
    SERIOUS = "serious"
    WITTY = "witty"
    SUPPORTIVE = "supportive"

class SocialContext(Enum):
    """Social interaction contexts"""
    GREETING = "greeting"
    FAREWELL = "farewell"
    GRATITUDE = "gratitude"
    APOLOGY = "apology"
    CONGRATULATION = "congratulation"
    SYMPATHY = "sympathy"
    INQUIRY = "inquiry"
    RESPONSE = "response"
    SMALL_TALK = "small_talk"
    CONFLICT_RESOLUTION = "conflict_resolution"

@dataclass
class StyleVector:
    """Multi-dimensional style representation"""
    formality: float  # 0 (very casual) to 1 (very formal)
    warmth: float     # 0 (cold/distant) to 1 (warm/friendly)
    energy: float     # 0 (subdued) to 1 (energetic)
    verbosity: float  # 0 (terse) to 1 (elaborate)
    humor: float      # 0 (serious) to 1 (playful)
    empathy: float    # 0 (detached) to 1 (empathetic)
    
    def interpolate(self, target: 'StyleVector', factor: float) -> 'StyleVector':
        """Smoothly interpolate between two style vectors"""
        return StyleVector(
            formality=self.formality + (target.formality - self.formality) * factor,
            warmth=self.warmth + (target.warmth - self.warmth) * factor,
            energy=self.energy + (target.energy - self.energy) * factor,
            verbosity=self.verbosity + (target.verbosity - self.verbosity) * factor,
            humor=self.humor + (target.humor - self.humor) * factor,
            empathy=self.empathy + (target.empathy - self.empathy) * factor
        )
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for calculations"""
        return np.array([
            self.formality, self.warmth, self.energy,
            self.verbosity, self.humor, self.empathy
        ])
    
    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'StyleVector':
        """Create from numpy array"""
        return cls(*arr.tolist())

class StyleMorphEngine:
    """Engine for morphing between communication styles"""
    
    def __init__(self):
        # Define style vectors for each base style
        self.style_vectors = {
            CommunicationStyle.PROFESSIONAL: StyleVector(0.8, 0.5, 0.5, 0.6, 0.2, 0.4),
            CommunicationStyle.CASUAL: StyleVector(0.2, 0.7, 0.6, 0.4, 0.6, 0.5),
            CommunicationStyle.FORMAL: StyleVector(1.0, 0.3, 0.3, 0.7, 0.0, 0.3),
            CommunicationStyle.FRIENDLY: StyleVector(0.3, 0.9, 0.7, 0.5, 0.5, 0.7),
            CommunicationStyle.EMPATHETIC: StyleVector(0.5, 0.8, 0.4, 0.6, 0.2, 1.0),
            CommunicationStyle.ASSERTIVE: StyleVector(0.6, 0.4, 0.8, 0.5, 0.1, 0.3),
            CommunicationStyle.PLAYFUL: StyleVector(0.1, 0.8, 0.9, 0.4, 0.9, 0.6),
            CommunicationStyle.SCHOLARLY: StyleVector(0.9, 0.4, 0.4, 0.9, 0.1, 0.4)
        }
        
        # Mood modifiers (additive adjustments to style vectors)
        self.mood_modifiers = {
            Mood.NEUTRAL: np.array([0, 0, 0, 0, 0, 0]),
            Mood.ENTHUSIASTIC: np.array([-0.1, 0.2, 0.3, 0.1, 0.2, 0.1]),
            Mood.CONTEMPLATIVE: np.array([0.1, -0.1, -0.2, 0.2, -0.1, 0.1]),
            Mood.CONCERNED: np.array([0.1, 0.1, -0.1, 0.1, -0.2, 0.3]),
            Mood.CHEERFUL: np.array([-0.1, 0.3, 0.2, 0, 0.3, 0.2]),
            Mood.SERIOUS: np.array([0.2, -0.2, -0.1, 0.1, -0.3, 0]),
            Mood.WITTY: np.array([0, 0.1, 0.1, 0, 0.4, 0]),
            Mood.SUPPORTIVE: np.array([0, 0.3, 0, 0.1, 0, 0.4])
        }
        
        # Social context templates
        self.context_templates = self._initialize_context_templates()
        
        # Style transition history for smooth morphing
        self.style_history = []
        self.current_vector = self.style_vectors[CommunicationStyle.PROFESSIONAL]
    
    def _initialize_context_templates(self) -> Dict[SocialContext, Dict[str, List[str]]]:
        """Initialize templates for different social contexts"""
        return {
            SocialContext.GREETING: {
                "formal": ["Good morning", "Good afternoon", "Good evening", "Greetings"],
                "casual": ["Hey", "Hi", "Hello", "Hey there"],
                "friendly": ["Hey there!", "Hi!", "Hello!", "Howdy!"],
                "professional": ["Hello", "Good to see you", "Welcome"],
            },
            SocialContext.FAREWELL: {
                "formal": ["Goodbye", "Farewell", "Until next time"],
                "casual": ["Bye", "See ya", "Later", "Take care"],
                "friendly": ["See you later!", "Take care!", "Bye for now!"],
                "professional": ["Best regards", "Have a good day", "Thank you"],
            },
            SocialContext.GRATITUDE: {
                "formal": ["I appreciate your assistance", "Thank you very much"],
                "casual": ["Thanks", "Thanks a lot", "Appreciate it"],
                "friendly": ["Thanks so much!", "You're awesome!", "Really appreciate it!"],
                "professional": ["Thank you for your time", "I appreciate your help"],
            },
            # ... more contexts
        }
    
    def morph_style(
        self,
        text: str,
        target_style: CommunicationStyle,
        mood: Mood = Mood.NEUTRAL,
        context: Optional[SocialContext] = None,
        transition_speed: float = 0.5
    ) -> str:
        """Morph text to target style with mood and context considerations"""
        
        # Calculate target style vector with mood modifier
        target_vector = self.style_vectors[target_style]
        mood_modifier = self.mood_modifiers[mood]
        
        # Apply mood to create adjusted target
        adjusted_array = np.clip(target_vector.to_array() + mood_modifier, 0, 1)
        adjusted_target = StyleVector.from_array(adjusted_array)
        
        # Smooth transition from current to target
        self.current_vector = self.current_vector.interpolate(adjusted_target, transition_speed)
        
        # Apply transformations based on vector
        morphed_text = self._apply_style_transformations(text, self.current_vector, context)
        
        # Record in history for learning
        self.style_history.append({
            "timestamp": datetime.now(),
            "original": text,
            "morphed": morphed_text,
            "style": target_style,
            "mood": mood,
            "vector": self.current_vector
        })
        
        return morphed_text
    
    def _apply_style_transformations(
        self,
        text: str,
        style_vector: StyleVector,
        context: Optional[SocialContext]
    ) -> str:
        """Apply style transformations based on style vector"""
        
        # Start with original text
        result = text
        
        # Apply formality transformations
        if style_vector.formality > 0.7:
            result = self._increase_formality(result)
        elif style_vector.formality < 0.3:
            result = self._decrease_formality(result)
        
        # Apply warmth transformations
        if style_vector.warmth > 0.7:
            result = self._add_warmth(result)
        
        # Apply energy transformations
        if style_vector.energy > 0.7:
            result = self._add_energy(result)
        elif style_vector.energy < 0.3:
            result = self._reduce_energy(result)
        
        # Apply verbosity transformations
        if style_vector.verbosity > 0.7:
            result = self._elaborate(result)
        elif style_vector.verbosity < 0.3:
            result = self._condense(result)
        
        # Apply humor if appropriate
        if style_vector.humor > 0.6 and context not in [SocialContext.SYMPATHY, SocialContext.APOLOGY]:
            result = self._add_light_humor(result)
        
        # Apply empathy markers
        if style_vector.empathy > 0.7:
            result = self._add_empathy(result)
        
        # Apply context-specific templates if available
        if context:
            result = self._apply_context_template(result, context, style_vector)
        
        return result
    
    def _increase_formality(self, text: str) -> str:
        """Increase formality of text"""
        replacements = {
            r'\bhi\b': 'hello',
            r'\bhey\b': 'hello',
            r'\byeah\b': 'yes',
            r'\bnope\b': 'no',
            r'\bgonna\b': 'going to',
            r'\bwanna\b': 'want to',
            r'\bgotta\b': 'have to',
            r'\bkinda\b': 'somewhat',
            r'\bsorta\b': 'sort of',
            r'\bthanks\b': 'thank you',
            r'\bok\b': 'certainly',
            r'\bbye\b': 'goodbye',
            r"can't": 'cannot',
            r"won't": 'will not',
            r"it's": 'it is',
            r"I'm": 'I am',
            r"you're": 'you are',
            r"we're": 'we are',
            r"they're": 'they are',
            r"I'll": 'I will',
            r"you'll": 'you will',
            r"we'll": 'we will',
        }
        
        result = text
        for pattern, replacement in replacements.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Capitalize first letter
        result = result[0].upper() + result[1:] if result else result
        
        # Ensure proper punctuation
        if result and result[-1] not in '.!?':
            result += '.'
        
        return result
    
    def _decrease_formality(self, text: str) -> str:
        """Decrease formality of text"""
        replacements = {
            r'\bhello\b': 'hi',
            r'\byes\b': 'yeah',
            r'\bthank you\b': 'thanks',
            r'\bgoodbye\b': 'bye',
            'going to': 'gonna',
            'want to': 'wanna',
            'have to': 'gotta',
            'kind of': 'kinda',
            'sort of': 'sorta',
        }
        
        result = text
        for pattern, replacement in replacements.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Remove overly formal punctuation
        result = result.rstrip('.')
        
        return result
    
    def _add_warmth(self, text: str) -> str:
        """Add warmth to communication"""
        warm_additions = [
            "I hope you're doing well",
            "It's great to hear from you",
            "I'm happy to help",
            "Feel free to reach out anytime",
            "Take care",
            "Wishing you the best"
        ]
        
        # Add warm greeting if it's a greeting context
        if any(greeting in text.lower() for greeting in ['hello', 'hi', 'greetings']):
            return text + "! " + np.random.choice(warm_additions[:3])
        
        # Add warm closing if it's a farewell
        if any(farewell in text.lower() for farewell in ['bye', 'goodbye', 'farewell']):
            return text + ". " + np.random.choice(warm_additions[3:])
        
        return text
    
    def _add_energy(self, text: str) -> str:
        """Add energy and enthusiasm"""
        # Add exclamation marks where appropriate
        if text.endswith('.'):
            text = text[:-1] + '!'
        
        # Add energetic words
        energetic_additions = ['definitely', 'absolutely', 'really', 'totally']
        
        # Insert energetic modifiers
        words = text.split()
        if len(words) > 3:
            insert_pos = np.random.randint(1, len(words) - 1)
            words.insert(insert_pos, np.random.choice(energetic_additions))
            text = ' '.join(words)
        
        return text
    
    def _reduce_energy(self, text: str) -> str:
        """Reduce energy for more subdued communication"""
        # Replace exclamation marks with periods
        text = text.replace('!', '.')
        
        # Remove overly energetic words
        calm_replacements = {
            'definitely': 'certainly',
            'absolutely': 'yes',
            'really': 'quite',
            'totally': 'entirely',
            'amazing': 'good',
            'awesome': 'nice',
            'fantastic': 'good'
        }
        
        for energetic, calm in calm_replacements.items():
            text = text.replace(energetic, calm)
        
        return text
    
    def _elaborate(self, text: str) -> str:
        """Make text more verbose"""
        elaborations = {
            r'\bgood\b': 'quite good',
            r'\bnice\b': 'rather nice',
            r'\bok\b': 'acceptable',
            r'\bfine\b': 'perfectly fine',
            r'\bthanks\b': 'thank you very much',
            r'\byes\b': 'yes, indeed',
            r'\bno\b': 'no, I\'m afraid not'
        }
        
        result = text
        for pattern, replacement in elaborations.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def _condense(self, text: str) -> str:
        """Make text more concise"""
        # Remove filler words
        fillers = [
            'actually', 'basically', 'really', 'very', 'quite',
            'rather', 'somewhat', 'indeed', 'certainly'
        ]
        
        words = text.split()
        filtered_words = [w for w in words if w.lower() not in fillers]
        
        return ' '.join(filtered_words)
    
    def _add_light_humor(self, text: str) -> str:
        """Add light humor where appropriate"""
        # Add playful endings
        playful_endings = [
            " 😊", " 😄", " :)", " haha", " 😎"
        ]
        
        if np.random.random() > 0.5:
            text += np.random.choice(playful_endings)
        
        return text
    
    def _add_empathy(self, text: str) -> str:
        """Add empathetic language"""
        empathy_phrases = {
            "I understand": "I completely understand",
            "I see": "I can see why you'd feel that way",
            "That's": "I can imagine that's",
            "difficult": "challenging, and I appreciate you sharing",
        }
        
        result = text
        for phrase, empathetic in empathy_phrases.items():
            if phrase in result:
                result = result.replace(phrase, empathetic)
                break
        
        return result
    
    def _apply_context_template(
        self,
        text: str,
        context: SocialContext,
        style_vector: StyleVector
    ) -> str:
        """Apply context-specific templates"""
        if context not in self.context_templates:
            return text
        
        templates = self.context_templates[context]
        
        # Choose template category based on style vector
        if style_vector.formality > 0.8:
            category = "formal"
        elif style_vector.warmth > 0.7:
            category = "friendly"
        elif style_vector.formality > 0.5:
            category = "professional"
        else:
            category = "casual"
        
        if category in templates and templates[category]:
            # Replace generic greetings/farewells with styled ones
            template = np.random.choice(templates[category])
            
            # Smart replacement based on context
            if context == SocialContext.GREETING:
                for greeting in ['hello', 'hi', 'hey', 'greetings']:
                    if greeting in text.lower():
                        return text.lower().replace(greeting, template.lower())
            
            elif context == SocialContext.FAREWELL:
                for farewell in ['bye', 'goodbye', 'farewell', 'see you']:
                    if farewell in text.lower():
                        return text.lower().replace(farewell, template.lower())
        
        return text
    
    def analyze_style(self, text: str) -> StyleVector:
        """Analyze the style vector of given text"""
        # Initialize with neutral values
        formality = 0.5
        warmth = 0.5
        energy = 0.5
        verbosity = 0.5
        humor = 0.0
        empathy = 0.5
        
        # Analyze formality
        formal_indicators = ['therefore', 'however', 'furthermore', 'regarding', 'pursuant']
        informal_indicators = ['hey', 'yeah', 'gonna', 'wanna', 'kinda']
        
        for word in formal_indicators:
            if word in text.lower():
                formality += 0.1
        
        for word in informal_indicators:
            if word in text.lower():
                formality -= 0.1
        
        # Analyze energy
        if text.count('!') > 0:
            energy += 0.2 * min(text.count('!'), 3)
        
        # Analyze verbosity
        word_count = len(text.split())
        if word_count > 20:
            verbosity = min(0.9, 0.5 + (word_count - 20) * 0.02)
        elif word_count < 10:
            verbosity = max(0.1, 0.5 - (10 - word_count) * 0.05)
        
        # Analyze warmth
        warm_words = ['hope', 'care', 'appreciate', 'thank', 'please', 'kind']
        for word in warm_words:
            if word in text.lower():
                warmth += 0.1
        
        # Analyze humor
        humor_indicators = ['haha', 'lol', ':)', '😊', '😄', 'joke', 'funny']
        for indicator in humor_indicators:
            if indicator in text:
                humor += 0.2
        
        # Analyze empathy
        empathy_words = ['understand', 'feel', 'appreciate', 'imagine', 'sorry']
        for word in empathy_words:
            if word in text.lower():
                empathy += 0.1
        
        # Normalize values
        return StyleVector(
            formality=np.clip(formality, 0, 1),
            warmth=np.clip(warmth, 0, 1),
            energy=np.clip(energy, 0, 1),
            verbosity=np.clip(verbosity, 0, 1),
            humor=np.clip(humor, 0, 1),
            empathy=np.clip(empathy, 0, 1)
        )
    
    def get_style_distance(self, vector1: StyleVector, vector2: StyleVector) -> float:
        """Calculate distance between two style vectors"""
        arr1 = vector1.to_array()
        arr2 = vector2.to_array()
        return float(np.linalg.norm(arr1 - arr2))
    
    def suggest_style_transition(
        self,
        current_text: str,
        target_audience: str
    ) -> Tuple[CommunicationStyle, Mood]:
        """Suggest appropriate style and mood for target audience"""
        audience_profiles = {
            "boss": (CommunicationStyle.PROFESSIONAL, Mood.NEUTRAL),
            "colleague": (CommunicationStyle.FRIENDLY, Mood.SUPPORTIVE),
            "client": (CommunicationStyle.PROFESSIONAL, Mood.ENTHUSIASTIC),
            "friend": (CommunicationStyle.CASUAL, Mood.CHEERFUL),
            "support_request": (CommunicationStyle.EMPATHETIC, Mood.SUPPORTIVE),
            "academic": (CommunicationStyle.SCHOLARLY, Mood.CONTEMPLATIVE),
            "child": (CommunicationStyle.PLAYFUL, Mood.CHEERFUL),
            "elderly": (CommunicationStyle.FORMAL, Mood.SUPPORTIVE),
        }
        
        return audience_profiles.get(
            target_audience.lower(),
            (CommunicationStyle.PROFESSIONAL, Mood.NEUTRAL)
        )
    
    def morph_style_multilingual(
        self,
        text: str,
        target_style: CommunicationStyle,
        mood: Mood = Mood.NEUTRAL,
        context: Optional[SocialContext] = None,
        source_language: Language = Language.ENGLISH,
        target_language: Language = Language.ENGLISH,
        transition_speed: float = 0.5
    ) -> Dict[str, Any]:
        """Morph text style with multi-language support"""
        
        # Detect source language if not specified
        if source_language == Language.ENGLISH:
            source_language = i18n.detect_language(text)
        
        # First, morph the style in the source language
        morphed_text = self.morph_style(
            text=text,
            target_style=target_style,
            mood=mood,
            context=context,
            transition_speed=transition_speed
        )
        
        # If target language is different, translate while maintaining style
        if source_language != target_language:
            translated_text = i18n.translate_style_morphing(
                morphed_text,
                source_language,
                target_language,
                maintain_style=True
            )
        else:
            translated_text = morphed_text
        
        return {
            "original": text,
            "morphed": morphed_text,
            "translated": translated_text,
            "source_language": source_language.value,
            "target_language": target_language.value,
            "style": target_style.value,
            "mood": mood.value
        }
    
    def get_multilingual_templates(
        self,
        context: SocialContext,
        language: Language = Language.ENGLISH
    ) -> Dict[str, List[str]]:
        """Get context templates in specified language"""
        templates = {}
        
        # Map style categories to template types
        style_mapping = {
            "formal": ["formal", "professional"],
            "casual": ["casual", "friendly"],
            "professional": ["professional"],
            "friendly": ["friendly", "casual"]
        }
        
        for style_cat, template_types in style_mapping.items():
            templates[style_cat] = []
            
            # Get translations for this context
            if context == SocialContext.GREETING:
                templates[style_cat].extend([
                    i18n.get("greeting.hello", language),
                    i18n.get("greeting.good_morning", language),
                    i18n.get("greeting.welcome", language)
                ])
            elif context == SocialContext.FAREWELL:
                templates[style_cat].extend([
                    i18n.get("farewell.goodbye", language),
                    i18n.get("farewell.see_you_later", language),
                    i18n.get("farewell.take_care", language)
                ])
            elif context == SocialContext.GRATITUDE:
                templates[style_cat].extend([
                    i18n.get("gratitude.thank_you", language),
                    i18n.get("gratitude.thanks", language),
                    i18n.get("gratitude.much_appreciated", language)
                ])
            elif context == SocialContext.APOLOGY:
                templates[style_cat].extend([
                    i18n.get("apology.sorry", language),
                    i18n.get("apology.my_apologies", language),
                    i18n.get("apology.excuse_me", language)
                ])
        
        return templates
    
    def adapt_formality_for_culture(
        self,
        text: str,
        target_language: Language,
        cultural_context: str = "default"
    ) -> str:
        """Adapt formality level based on cultural norms"""
        
        # Cultural formality adjustments
        cultural_formality = {
            Language.JAPANESE: 0.8,      # More formal by default
            Language.KOREAN: 0.7,         # Formal with hierarchy
            Language.GERMAN: 0.6,         # Moderate formality
            Language.FRENCH: 0.6,         # Polite formality
            Language.SPANISH: 0.4,        # Warmer, less formal
            Language.ITALIAN: 0.4,        # Expressive, less formal
            Language.ENGLISH: 0.5,        # Neutral
            Language.PORTUGUESE: 0.4,     # Warm and friendly
            Language.CHINESE: 0.7,        # Respectful formality
            Language.ARABIC: 0.7,         # Traditional formality
            Language.RUSSIAN: 0.6,        # Moderate formality
            Language.HINDI: 0.6          # Respectful
        }
        
        # Get cultural formality level
        formality_adjustment = cultural_formality.get(target_language, 0.5)
        
        # Adjust current style vector for cultural norms
        adjusted_vector = self.current_vector
        adjusted_vector.formality = formality_adjustment
        
        # Apply cultural adaptations
        return self._apply_style_transformations(text, adjusted_vector, None)
    
    def generate_culturally_appropriate_response(
        self,
        context: SocialContext,
        language: Language,
        style: CommunicationStyle,
        additional_context: Dict[str, Any] = None
    ) -> str:
        """Generate a culturally appropriate response"""
        
        # Get appropriate templates
        templates = self.get_multilingual_templates(context, language)
        
        # Select template based on style
        if style in [CommunicationStyle.FORMAL, CommunicationStyle.PROFESSIONAL]:
            template_list = templates.get("formal", [])
        elif style in [CommunicationStyle.CASUAL, CommunicationStyle.FRIENDLY]:
            template_list = templates.get("casual", [])
        else:
            template_list = templates.get("professional", [])
        
        # Choose a template
        if template_list:
            response = np.random.choice(template_list)
        else:
            # Fallback to basic response
            response = i18n.get("greeting.hello", language)
        
        # Add cultural adaptations
        response = self.adapt_formality_for_culture(response, language)
        
        return response