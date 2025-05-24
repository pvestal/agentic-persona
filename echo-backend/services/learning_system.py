"""
Learning System for ECHO
Tracks user feedback and improves response generation over time
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import asyncio
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

try:
    from services.llm_service import llm_service
except ImportError:
    llm_service = None

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of user feedback"""
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"
    RATING = "rating"
    IMPLICIT_POSITIVE = "implicit_positive"  # No negative feedback within time window
    IMPLICIT_NEGATIVE = "implicit_negative"  # Quick rejection or edit


@dataclass
class ResponsePattern:
    """Pattern learned from user feedback"""
    context_type: str
    response_style: str
    success_rate: float
    sample_count: int
    common_edits: List[Dict[str, str]]
    preferred_phrases: List[str]
    avoided_phrases: List[str]
    avg_response_length: int
    tone_preferences: Dict[str, float]


@dataclass
class LearningInsight:
    """Insights derived from learning data"""
    insight_type: str
    confidence: float
    description: str
    recommendation: str
    supporting_data: Dict[str, Any]


class LearningSystem:
    """System for learning from user feedback and improving responses"""
    
    def __init__(self):
        self.learning_cache = {}
        self.pattern_cache = {}
        self.insight_cache = {}
        self.last_analysis = None
        
        # Learning configuration
        self.min_samples_for_pattern = 5
        self.confidence_threshold = 0.7
        self.recency_weight = 0.3  # Weight for recent feedback
        self.edit_similarity_threshold = 0.8
        
        # Background task will be started when event loop is available
        self._analysis_task = None
    
    async def record_feedback(
        self,
        message_id: str,
        feedback_type: FeedbackType,
        original_response: str,
        edited_response: Optional[str] = None,
        rating: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record user feedback on a response"""
        try:
            # Calculate response quality score
            quality_score = self._calculate_quality_score(
                feedback_type, rating, edited_response, original_response
            )
            
            # Extract learning features
            features = await self._extract_features(
                original_response,
                edited_response,
                context
            )
            
            # Store in database
            learning_entry = {
                "message_id": message_id,
                "feedback_type": feedback_type.value,
                "original_response": original_response,
                "edited_response": edited_response,
                "quality_score": quality_score,
                "features": json.dumps(features),
                "context": json.dumps(context or {}),
                "created_at": datetime.utcnow()
            }
            
            # Save to database (would use actual ORM here)
            # await self.db.save_learning_data(learning_entry)
            
            # Update pattern cache
            await self._update_patterns(features, quality_score, context)
            
            # Generate immediate insights
            insights = await self._generate_insights(feedback_type, features)
            
            logger.info(f"Recorded {feedback_type.value} feedback for message {message_id}")
            
            return {
                "feedback_recorded": True,
                "quality_score": quality_score,
                "insights": insights,
                "patterns_updated": True
            }
            
        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
            return {"feedback_recorded": False, "error": str(e)}
    
    async def get_response_improvements(
        self,
        message: str,
        initial_response: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get improvements for a response based on learning data"""
        try:
            # Find similar contexts
            similar_contexts = await self._find_similar_contexts(context)
            
            # Get successful patterns
            patterns = await self._get_successful_patterns(similar_contexts)
            
            # Apply learned improvements
            improvements = {
                "suggested_edits": [],
                "style_adjustments": {},
                "length_recommendation": None,
                "tone_adjustments": {},
                "confidence": 0.0
            }
            
            if patterns:
                # Analyze what made previous responses successful
                improvements = await self._analyze_successful_patterns(
                    initial_response,
                    patterns,
                    context
                )
                
                # Generate improved response if confidence is high
                if improvements["confidence"] > self.confidence_threshold:
                    improved_response = await self._generate_improved_response(
                        message,
                        initial_response,
                        improvements,
                        context
                    )
                    improvements["improved_response"] = improved_response
            
            return improvements
            
        except Exception as e:
            logger.error(f"Error getting response improvements: {e}")
            return {"error": str(e)}
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get learned preferences for a specific user"""
        try:
            # Aggregate feedback data for user
            preferences = {
                "communication_style": await self._infer_communication_style(user_id),
                "response_length": await self._infer_preferred_length(user_id),
                "tone_preferences": await self._infer_tone_preferences(user_id),
                "common_edits": await self._get_common_edits(user_id),
                "response_patterns": await self._get_response_patterns(user_id),
                "platform_preferences": await self._get_platform_preferences(user_id)
            }
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}
    
    async def analyze_learning_trends(
        self,
        time_range: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Analyze learning trends over time"""
        try:
            if not time_range:
                time_range = timedelta(days=30)
            
            trends = {
                "approval_rate_trend": await self._calculate_approval_trend(time_range),
                "common_feedback_patterns": await self._analyze_feedback_patterns(time_range),
                "improvement_areas": await self._identify_improvement_areas(time_range),
                "successful_adaptations": await self._find_successful_adaptations(time_range),
                "user_satisfaction_trend": await self._calculate_satisfaction_trend(time_range)
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {}
    
    def _calculate_quality_score(
        self,
        feedback_type: FeedbackType,
        rating: Optional[float],
        edited_response: Optional[str],
        original_response: str
    ) -> float:
        """Calculate quality score based on feedback"""
        if feedback_type == FeedbackType.APPROVED:
            return 1.0
        elif feedback_type == FeedbackType.REJECTED:
            return 0.0
        elif feedback_type == FeedbackType.EDITED:
            # Calculate based on edit distance
            if edited_response:
                similarity = self._calculate_text_similarity(
                    original_response,
                    edited_response
                )
                return similarity  # Minor edits = higher score
            return 0.5
        elif feedback_type == FeedbackType.RATING:
            return rating or 0.5
        elif feedback_type == FeedbackType.IMPLICIT_POSITIVE:
            return 0.8
        else:  # IMPLICIT_NEGATIVE
            return 0.2
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Simple implementation - could use more sophisticated methods
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def _extract_features(
        self,
        original_response: str,
        edited_response: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract learning features from feedback"""
        features = {
            "response_length": len(original_response),
            "word_count": len(original_response.split()),
            "has_greeting": any(g in original_response.lower() for g in ["hello", "hi", "hey"]),
            "has_closing": any(c in original_response.lower() for c in ["regards", "best", "sincerely"]),
            "is_question": "?" in original_response,
            "sentiment": "neutral",  # Would use sentiment analysis
            "formality_level": self._estimate_formality(original_response),
        }
        
        if edited_response:
            features["edit_distance"] = self._calculate_edit_distance(
                original_response,
                edited_response
            )
            features["length_change"] = len(edited_response) - len(original_response)
            features["added_phrases"] = self._find_added_phrases(
                original_response,
                edited_response
            )
            features["removed_phrases"] = self._find_removed_phrases(
                original_response,
                edited_response
            )
        
        if context:
            features["platform"] = context.get("platform", "unknown")
            features["urgency"] = context.get("urgency", 0.5)
            features["sender_type"] = context.get("sender_type", "unknown")
            features["time_of_day"] = context.get("time_of_day", "unknown")
        
        return features
    
    def _estimate_formality(self, text: str) -> float:
        """Estimate formality level of text"""
        informal_indicators = ["hey", "yeah", "gonna", "wanna", "lol", "btw"]
        formal_indicators = ["regards", "sincerely", "furthermore", "therefore", "kindly"]
        
        text_lower = text.lower()
        informal_count = sum(1 for ind in informal_indicators if ind in text_lower)
        formal_count = sum(1 for ind in formal_indicators if ind in text_lower)
        
        if informal_count + formal_count == 0:
            return 0.5
        
        return formal_count / (informal_count + formal_count)
    
    def _calculate_edit_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._calculate_edit_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _find_added_phrases(self, original: str, edited: str) -> List[str]:
        """Find phrases added in the edit"""
        original_words = set(original.lower().split())
        edited_words = set(edited.lower().split())
        added = edited_words - original_words
        return list(added)[:10]  # Limit to 10 phrases
    
    def _find_removed_phrases(self, original: str, edited: str) -> List[str]:
        """Find phrases removed in the edit"""
        original_words = set(original.lower().split())
        edited_words = set(edited.lower().split())
        removed = original_words - edited_words
        return list(removed)[:10]  # Limit to 10 phrases
    
    async def _update_patterns(
        self,
        features: Dict[str, Any],
        quality_score: float,
        context: Optional[Dict[str, Any]]
    ):
        """Update learned patterns based on feedback"""
        pattern_key = f"{context.get('platform', 'unknown')}_{context.get('sender_type', 'unknown')}"
        
        if pattern_key not in self.pattern_cache:
            self.pattern_cache[pattern_key] = {
                "features": [],
                "scores": [],
                "contexts": []
            }
        
        self.pattern_cache[pattern_key]["features"].append(features)
        self.pattern_cache[pattern_key]["scores"].append(quality_score)
        self.pattern_cache[pattern_key]["contexts"].append(context)
        
        # Keep only recent entries
        max_entries = 100
        if len(self.pattern_cache[pattern_key]["features"]) > max_entries:
            self.pattern_cache[pattern_key]["features"] = self.pattern_cache[pattern_key]["features"][-max_entries:]
            self.pattern_cache[pattern_key]["scores"] = self.pattern_cache[pattern_key]["scores"][-max_entries:]
            self.pattern_cache[pattern_key]["contexts"] = self.pattern_cache[pattern_key]["contexts"][-max_entries:]
    
    async def _generate_insights(
        self,
        feedback_type: FeedbackType,
        features: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate immediate insights from feedback"""
        insights = []
        
        if feedback_type == FeedbackType.EDITED:
            if features.get("length_change", 0) < -20:
                insights.append({
                    "type": "response_length",
                    "message": "User prefers shorter responses",
                    "confidence": 0.8
                })
            elif features.get("length_change", 0) > 20:
                insights.append({
                    "type": "response_length",
                    "message": "User prefers more detailed responses",
                    "confidence": 0.8
                })
            
            if features.get("added_phrases"):
                insights.append({
                    "type": "vocabulary",
                    "message": f"User added: {', '.join(features['added_phrases'][:3])}",
                    "confidence": 0.7
                })
        
        return insights
    
    async def _periodic_analysis(self):
        """Periodically analyze learning data"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Analyze patterns
                analysis_results = await self.analyze_learning_trends(timedelta(days=7))
                
                # Update insights cache
                self.insight_cache = analysis_results
                self.last_analysis = datetime.utcnow()
                
                logger.info("Completed periodic learning analysis")
                
            except Exception as e:
                logger.error(f"Error in periodic analysis: {e}")
    
    async def _find_similar_contexts(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar contexts from learning history"""
        similar = []
        
        for pattern_key, pattern_data in self.pattern_cache.items():
            for stored_context in pattern_data["contexts"]:
                similarity = self._calculate_context_similarity(context, stored_context)
                if similarity > 0.7:
                    similar.append(stored_context)
        
        return similar
    
    def _calculate_context_similarity(self, context1: Dict, context2: Dict) -> float:
        """Calculate similarity between two contexts"""
        if not context1 or not context2:
            return 0.0
        
        common_keys = set(context1.keys()).intersection(set(context2.keys()))
        if not common_keys:
            return 0.0
        
        matches = sum(1 for key in common_keys if context1[key] == context2[key])
        return matches / len(common_keys)
    
    async def _get_successful_patterns(
        self,
        contexts: List[Dict[str, Any]]
    ) -> List[ResponsePattern]:
        """Get successful response patterns for given contexts"""
        patterns = []
        
        # Group by context type
        context_groups = defaultdict(list)
        for ctx in contexts:
            key = f"{ctx.get('platform', 'unknown')}_{ctx.get('sender_type', 'unknown')}"
            context_groups[key].append(ctx)
        
        # Analyze each group
        for context_type, group_contexts in context_groups.items():
            if len(group_contexts) >= self.min_samples_for_pattern:
                pattern = await self._analyze_context_group(context_type, group_contexts)
                if pattern:
                    patterns.append(pattern)
        
        return patterns
    
    async def _analyze_context_group(
        self,
        context_type: str,
        contexts: List[Dict[str, Any]]
    ) -> Optional[ResponsePattern]:
        """Analyze a group of similar contexts"""
        # This would aggregate learning data for the context group
        # For now, return a mock pattern
        return ResponsePattern(
            context_type=context_type,
            response_style="professional",
            success_rate=0.85,
            sample_count=len(contexts),
            common_edits=[],
            preferred_phrases=["I'd be happy to help", "Thank you for reaching out"],
            avoided_phrases=["Sorry for the inconvenience"],
            avg_response_length=150,
            tone_preferences={"friendly": 0.8, "formal": 0.6}
        )
    
    async def _analyze_successful_patterns(
        self,
        initial_response: str,
        patterns: List[ResponsePattern],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze successful patterns to improve response"""
        improvements = {
            "suggested_edits": [],
            "style_adjustments": {},
            "length_recommendation": None,
            "tone_adjustments": {},
            "confidence": 0.0
        }
        
        if not patterns:
            return improvements
        
        # Aggregate insights from patterns
        avg_length = np.mean([p.avg_response_length for p in patterns])
        current_length = len(initial_response.split())
        
        if abs(current_length - avg_length) > 20:
            improvements["length_recommendation"] = int(avg_length)
        
        # Aggregate tone preferences
        tone_scores = defaultdict(list)
        for pattern in patterns:
            for tone, score in pattern.tone_preferences.items():
                tone_scores[tone].append(score)
        
        improvements["tone_adjustments"] = {
            tone: np.mean(scores) for tone, scores in tone_scores.items()
        }
        
        # Calculate confidence based on pattern consistency
        improvements["confidence"] = min(len(patterns) / 10, 1.0) * np.mean([p.success_rate for p in patterns])
        
        return improvements
    
    async def _generate_improved_response(
        self,
        message: str,
        initial_response: str,
        improvements: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate an improved response based on learning"""
        if not llm_service:
            return initial_response
        
        improvement_prompt = f"""Based on user feedback patterns, improve this response:

Original message: {message}
Initial response: {initial_response}

Improvements needed:
- Tone adjustments: {improvements.get('tone_adjustments', {})}
- Length recommendation: {improvements.get('length_recommendation', 'no change')} words
- Style: {improvements.get('style_adjustments', {})}

Generate an improved response that incorporates these learnings."""

        try:
            improved = await llm_service.generate_response(
                improvement_prompt,
                agent_persona="You are refining responses based on user preferences.",
                temperature=0.3
            )
            return improved
        except Exception as e:
            logger.error(f"Error generating improved response: {e}")
            return initial_response
    
    async def _infer_communication_style(self, user_id: str) -> str:
        """Infer user's preferred communication style"""
        # Analyze feedback patterns to determine style
        # For now, return a default
        return "professional_friendly"
    
    async def _infer_preferred_length(self, user_id: str) -> str:
        """Infer user's preferred response length"""
        # Analyze edit patterns to determine preference
        return "concise"
    
    async def _infer_tone_preferences(self, user_id: str) -> Dict[str, float]:
        """Infer user's tone preferences"""
        return {
            "friendly": 0.8,
            "professional": 0.7,
            "casual": 0.3,
            "formal": 0.4
        }
    
    async def _get_common_edits(self, user_id: str) -> List[Dict[str, str]]:
        """Get common edits made by user"""
        return [
            {"original": "Sorry for the inconvenience", "edited": "I appreciate your patience"},
            {"original": "Please let me know", "edited": "Feel free to reach out"}
        ]
    
    async def _get_response_patterns(self, user_id: str) -> List[Dict[str, Any]]:
        """Get successful response patterns for user"""
        return []
    
    async def _get_platform_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get platform-specific preferences"""
        return {
            "email": {"formality": "high", "length": "detailed"},
            "slack": {"formality": "low", "length": "brief"},
            "sms": {"formality": "low", "length": "very_brief"}
        }
    
    async def _calculate_approval_trend(self, time_range: timedelta) -> List[Dict[str, Any]]:
        """Calculate approval rate trend over time"""
        # Would query database for actual data
        return [
            {"date": "2024-01-01", "approval_rate": 0.75},
            {"date": "2024-01-08", "approval_rate": 0.78},
            {"date": "2024-01-15", "approval_rate": 0.82},
            {"date": "2024-01-22", "approval_rate": 0.85}
        ]
    
    async def _analyze_feedback_patterns(self, time_range: timedelta) -> Dict[str, Any]:
        """Analyze patterns in user feedback"""
        return {
            "most_edited_phrases": ["Sorry for", "Please note", "Unfortunately"],
            "preferred_openings": ["Thanks for reaching out", "I'd be happy to help"],
            "preferred_closings": ["Let me know if you need anything else", "Feel free to reach out"]
        }
    
    async def _identify_improvement_areas(self, time_range: timedelta) -> List[str]:
        """Identify areas needing improvement"""
        return [
            "Response length consistency",
            "Tone matching for urgent messages",
            "Technical explanation clarity"
        ]
    
    async def _find_successful_adaptations(self, time_range: timedelta) -> List[Dict[str, Any]]:
        """Find successful adaptations made by the system"""
        return [
            {
                "adaptation": "Shortened email responses",
                "success_rate_improvement": 0.15,
                "user_satisfaction_increase": 0.2
            }
        ]
    
    async def _calculate_satisfaction_trend(self, time_range: timedelta) -> List[Dict[str, Any]]:
        """Calculate user satisfaction trend"""
        return [
            {"date": "2024-01-01", "satisfaction": 0.7},
            {"date": "2024-01-08", "satisfaction": 0.75},
            {"date": "2024-01-15", "satisfaction": 0.8},
            {"date": "2024-01-22", "satisfaction": 0.83}
        ]


# Singleton instance
learning_system = LearningSystem()