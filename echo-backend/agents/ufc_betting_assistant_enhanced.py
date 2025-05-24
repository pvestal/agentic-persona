"""
Enhanced UFC Betting Assistant Agent - Octagon Oracle AI
Analyzes UFC fights using LLM and learns from prediction outcomes
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
from dataclasses import dataclass, asdict
import asyncio
from decimal import Decimal
import logging

from crewai import Agent
from agents.base_agent import BaseAgent, AgentConfig

try:
    from services.llm_service import llm_service
except ImportError:
    llm_service = None

try:
    from services.learning_system import learning_system, FeedbackType
except ImportError:
    learning_system = None
    FeedbackType = None

logger = logging.getLogger(__name__)


class FightOutcome(Enum):
    WIN_KO_TKO = "ko_tko"
    WIN_SUBMISSION = "submission"
    WIN_DECISION = "decision"
    DRAW = "draw"
    NO_CONTEST = "no_contest"


class BettingMarket(Enum):
    MONEYLINE = "moneyline"
    OVER_UNDER = "over_under"
    METHOD_OF_VICTORY = "method"
    ROUND_BETTING = "round"
    PROP_BETS = "props"


class WeightClass(Enum):
    FLYWEIGHT = "flyweight"
    BANTAMWEIGHT = "bantamweight"
    FEATHERWEIGHT = "featherweight"
    LIGHTWEIGHT = "lightweight"
    WELTERWEIGHT = "welterweight"
    MIDDLEWEIGHT = "middleweight"
    LIGHT_HEAVYWEIGHT = "light_heavyweight"
    HEAVYWEIGHT = "heavyweight"
    WOMENS_STRAWWEIGHT = "womens_strawweight"
    WOMENS_FLYWEIGHT = "womens_flyweight"
    WOMENS_BANTAMWEIGHT = "womens_bantamweight"
    WOMENS_FEATHERWEIGHT = "womens_featherweight"


@dataclass
class FighterStats:
    name: str
    nickname: Optional[str] = None
    record: str = "0-0-0"  # "25-3-0"
    height: int = 70  # in inches
    reach: int = 70   # in inches
    stance: str = "orthodox"  # orthodox/southpaw/switch
    age: int = 25
    win_by_ko: int = 0
    win_by_sub: int = 0
    win_by_dec: int = 0
    losses_by_ko: int = 0
    losses_by_sub: int = 0
    losses_by_dec: int = 0
    avg_fight_time: float = 10.0  # minutes
    takedown_accuracy: float = 0.0
    takedown_defense: float = 0.0
    striking_accuracy: float = 0.0
    striking_defense: float = 0.0
    sig_strikes_per_min: float = 0.0
    sig_strikes_absorbed_per_min: float = 0.0
    recent_form: List[str] = None  # Last 5 fights ["W", "W", "L", "W", "W"]
    injury_history: List[str] = None
    camp: Optional[str] = None
    
    def __post_init__(self):
        if self.recent_form is None:
            self.recent_form = []
        if self.injury_history is None:
            self.injury_history = []


@dataclass
class FightAnalysis:
    fighter1: FighterStats
    fighter2: FighterStats
    weight_class: WeightClass
    is_title_fight: bool = False
    is_main_event: bool = False
    scheduled_rounds: int = 3
    venue: Optional[str] = None
    elevation: Optional[int] = None  # feet above sea level
    fight_date: Optional[datetime] = None
    

@dataclass
class BettingRecommendation:
    market: BettingMarket
    pick: str
    confidence: float  # 0-1
    expected_value: float
    reasoning: List[str]
    key_factors: List[str]
    risks: List[str]
    llm_analysis: Optional[str] = None
    prediction_id: Optional[str] = None


class UFCBettingAssistantEnhanced(BaseAgent):
    """AI-powered UFC fight analysis with LLM integration and learning"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        default_config = {
            "name": "Octagon Oracle AI",
            "full_name": "Octagon Oracle AI - Enhanced UFC Analysis Expert",
            "role": "AI-powered UFC fight analyst with machine learning",
            "goal": "provide data-driven UFC fight analysis using AI and historical learning",
            "backstory": """I am Octagon Oracle AI, your advanced UFC fight analyst powered by 
            artificial intelligence. I combine traditional fight analysis with cutting-edge LLM 
            technology to provide deeper insights. I learn from past predictions to continuously 
            improve my accuracy. I study fighter statistics, styles, matchups, training camps, 
            and even social media sentiment to provide comprehensive fight analysis. Remember: 
            all predictions are for entertainment purposes only.""",
            "tools": [],
            "verbose": True,
            "allow_delegation": False,
            "max_iter": 5
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(AgentConfig(**default_config))
        
        # Enhanced analysis factors
        self.style_matchups = {
            "wrestler_vs_striker": {
                "factors": ["takedown_defense", "sprawl", "ground_control", "cage_wrestling"],
                "advantage": "wrestler if TD% > 45% and striker TDD < 70%"
            },
            "pressure_vs_counter": {
                "factors": ["forward_pressure", "cardio", "chin", "output_rate"],
                "advantage": "pressure if cardio advantage and good chin"
            },
            "orthodox_vs_southpaw": {
                "factors": ["stance_familiarity", "lead_hand_usage", "liver_kick_defense"],
                "advantage": "southpaw historically +5% win rate"
            },
            "boxer_vs_kickboxer": {
                "factors": ["leg_kick_defense", "distance_management", "clinch_work"],
                "advantage": "depends on range control"
            },
            "bjj_vs_wrestler": {
                "factors": ["submission_defense", "scrambles", "top_control"],
                "advantage": "wrestler if good sub defense"
            }
        }
        
        self.camp_quality_scores = {
            "American Top Team": 0.85,
            "Jackson Wink MMA": 0.82,
            "City Kickboxing": 0.88,
            "Team Alpha Male": 0.80,
            "American Kickboxing Academy": 0.83,
            "Tristar Gym": 0.81,
            "Fortis MMA": 0.79,
            "Sanford MMA": 0.84
        }
        
        # Track predictions for learning
        self.prediction_history = []
        self.accuracy_stats = {
            "moneyline": {"correct": 0, "total": 0},
            "over_under": {"correct": 0, "total": 0},
            "method": {"correct": 0, "total": 0}
        }
    
    async def analyze_matchup_enhanced(
        self, 
        fighter1: FighterStats, 
        fighter2: FighterStats,
        fight_details: Dict[str, Any],
        include_llm_analysis: bool = True
    ) -> Tuple[FightAnalysis, Optional[str]]:
        """Enhanced matchup analysis with LLM insights"""
        
        analysis = FightAnalysis(
            fighter1=fighter1,
            fighter2=fighter2,
            weight_class=WeightClass(fight_details.get("weight_class", "lightweight")),
            is_title_fight=fight_details.get("is_title_fight", False),
            is_main_event=fight_details.get("is_main_event", False),
            scheduled_rounds=fight_details.get("rounds", 3),
            venue=fight_details.get("venue"),
            elevation=fight_details.get("elevation"),
            fight_date=fight_details.get("fight_date")
        )
        
        llm_analysis = None
        if include_llm_analysis and llm_service:
            llm_analysis = await self._get_llm_fight_analysis(analysis)
        
        return analysis, llm_analysis
    
    async def _get_llm_fight_analysis(self, analysis: FightAnalysis) -> str:
        """Get detailed fight analysis from LLM"""
        if not llm_service:
            return None
        
        prompt = f"""
        Analyze this UFC matchup in detail:
        
        FIGHTER 1: {analysis.fighter1.name}
        - Record: {analysis.fighter1.record}
        - Height/Reach: {analysis.fighter1.height}in / {analysis.fighter1.reach}in
        - Stance: {analysis.fighter1.stance}
        - Age: {analysis.fighter1.age}
        - Finishes: {analysis.fighter1.win_by_ko} KOs, {analysis.fighter1.win_by_sub} Subs
        - Recent Form: {' '.join(analysis.fighter1.recent_form[-5:])}
        - Striking: {analysis.fighter1.striking_accuracy:.1%} accuracy, {analysis.fighter1.sig_strikes_per_min:.1f} per min
        - Wrestling: {analysis.fighter1.takedown_accuracy:.1%} TD accuracy, {analysis.fighter1.takedown_defense:.1%} TD defense
        
        FIGHTER 2: {analysis.fighter2.name}
        - Record: {analysis.fighter2.record}
        - Height/Reach: {analysis.fighter2.height}in / {analysis.fighter2.reach}in
        - Stance: {analysis.fighter2.stance}
        - Age: {analysis.fighter2.age}
        - Finishes: {analysis.fighter2.win_by_ko} KOs, {analysis.fighter2.win_by_sub} Subs
        - Recent Form: {' '.join(analysis.fighter2.recent_form[-5:])}
        - Striking: {analysis.fighter2.striking_accuracy:.1%} accuracy, {analysis.fighter2.sig_strikes_per_min:.1f} per min
        - Wrestling: {analysis.fighter2.takedown_accuracy:.1%} TD accuracy, {analysis.fighter2.takedown_defense:.1%} TD defense
        
        Fight Details:
        - Weight Class: {analysis.weight_class.value}
        - Title Fight: {analysis.is_title_fight}
        - Scheduled Rounds: {analysis.scheduled_rounds}
        
        Provide a detailed technical analysis covering:
        1. Style matchup advantages/disadvantages
        2. Key technical factors that could determine the outcome
        3. Physical advantages (reach, age, size)
        4. Cardio considerations for {analysis.scheduled_rounds} rounds
        5. Mental/momentum factors based on recent form
        6. Specific techniques or strategies each fighter should employ
        7. X-factors that could swing the fight
        
        Focus on technical MMA analysis, not betting advice.
        """
        
        try:
            analysis_text = await llm_service.generate_response(
                message=prompt,
                agent_persona="You are an expert MMA analyst with deep knowledge of fighting techniques, strategies, and fighter tendencies.",
                temperature=0.7,
                max_tokens=800
            )
            return analysis_text
        except Exception as e:
            logger.error(f"Error getting LLM analysis: {e}")
            return None
    
    async def generate_predictions_enhanced(
        self, 
        analysis: FightAnalysis,
        llm_analysis: Optional[str] = None,
        odds: Optional[Dict[str, float]] = None
    ) -> List[BettingRecommendation]:
        """Generate enhanced predictions with LLM insights"""
        predictions = []
        
        # Get base predictions
        base_predictions = await self._generate_base_predictions(analysis)
        
        # Enhance with LLM insights if available
        if llm_analysis and llm_service:
            for pred in base_predictions:
                enhanced_reasoning = await self._enhance_prediction_with_llm(
                    pred, analysis, llm_analysis
                )
                if enhanced_reasoning:
                    pred.reasoning.extend(enhanced_reasoning)
                    pred.llm_analysis = llm_analysis
        
        # Apply learning adjustments if available
        if learning_system:
            for pred in base_predictions:
                adjustments = await self._apply_learning_adjustments(pred, analysis)
                if adjustments:
                    pred.confidence *= adjustments['confidence_modifier']
                    pred.reasoning.append(f"Adjusted based on historical accuracy: {adjustments['reason']}")
        
        # Calculate value if odds provided
        if odds:
            for pred in base_predictions:
                if pred.market == BettingMarket.MONEYLINE and pred.pick in odds:
                    value_analysis = self._analyze_betting_value(pred, odds[pred.pick])
                    if value_analysis['has_value']:
                        pred.reasoning.append(f"Value bet: {value_analysis['edge']:.1%} edge")
                    else:
                        pred.risks.append("No positive expected value at current odds")
        
        # Generate prediction IDs for tracking
        for pred in base_predictions:
            pred.prediction_id = f"ufc_{datetime.now().strftime('%Y%m%d')}_{analysis.fighter1.name}_{pred.market.value}"
        
        return base_predictions
    
    async def _generate_base_predictions(self, analysis: FightAnalysis) -> List[BettingRecommendation]:
        """Generate base predictions using traditional analysis"""
        predictions = []
        
        # Moneyline prediction
        ml_pick, ml_confidence, ml_factors = await self._predict_winner_enhanced(analysis)
        predictions.append(BettingRecommendation(
            market=BettingMarket.MONEYLINE,
            pick=ml_pick,
            confidence=ml_confidence,
            expected_value=0.0,  # Will be calculated with odds
            reasoning=self._generate_detailed_reasoning(analysis, ml_pick, ml_factors),
            key_factors=ml_factors,
            risks=self._identify_detailed_risks(analysis, ml_pick)
        ))
        
        # Over/Under prediction
        ou_pick, ou_confidence, ou_reasoning = await self._predict_over_under_enhanced(analysis)
        predictions.append(BettingRecommendation(
            market=BettingMarket.OVER_UNDER,
            pick=ou_pick,
            confidence=ou_confidence,
            expected_value=0.0,
            reasoning=ou_reasoning,
            key_factors=["finish_rate", "pace", "cardio", "damage_accumulation"],
            risks=["Early finish", "Pace changes", "Referee intervention"]
        ))
        
        # Method of victory
        method_pick, method_confidence, method_reasoning = await self._predict_method_enhanced(analysis)
        if method_confidence > 0.55:  # Lower threshold with better analysis
            predictions.append(BettingRecommendation(
                market=BettingMarket.METHOD_OF_VICTORY,
                pick=method_pick,
                confidence=method_confidence,
                expected_value=0.0,
                reasoning=method_reasoning,
                key_factors=self._get_enhanced_method_factors(method_pick, analysis),
                risks=["Multiple victory paths", "Game plan changes", "Injury during fight"]
            ))
        
        return predictions
    
    async def _predict_winner_enhanced(
        self, 
        analysis: FightAnalysis
    ) -> Tuple[str, float, List[str]]:
        """Enhanced winner prediction with detailed factors"""
        fighter1 = analysis.fighter1
        fighter2 = analysis.fighter2
        
        factors = []
        f1_score = 0.5  # Start even
        
        # Physical advantages
        reach_diff = fighter1.reach - fighter2.reach
        if abs(reach_diff) >= 3:
            advantage = 0.06 * (reach_diff / 3)  # Scale by inches
            f1_score += advantage
            factors.append(f"{'Reach advantage' if reach_diff > 0 else 'Reach disadvantage'} ({abs(reach_diff)}in)")
        
        # Age and experience
        age_factor = self._calculate_age_factor(fighter1.age, fighter2.age)
        f1_score += age_factor['advantage']
        if age_factor['significant']:
            factors.append(age_factor['reason'])
        
        # Technical advantages
        striking_diff = fighter1.striking_accuracy - fighter2.striking_accuracy
        if abs(striking_diff) > 0.05:
            f1_score += striking_diff * 0.3  # Weight striking heavily
            factors.append(f"{'Superior' if striking_diff > 0 else 'Inferior'} striking accuracy")
        
        # Wrestling/grappling
        td_defense_diff = fighter1.takedown_defense - fighter2.takedown_defense
        if abs(td_defense_diff) > 0.1:
            f1_score += td_defense_diff * 0.25
            factors.append(f"{'Better' if td_defense_diff > 0 else 'Worse'} takedown defense")
        
        # Finish ability
        f1_finish_rate = (fighter1.win_by_ko + fighter1.win_by_sub) / max(1, sum([fighter1.win_by_ko, fighter1.win_by_sub, fighter1.win_by_dec]))
        f2_finish_rate = (fighter2.win_by_ko + fighter2.win_by_sub) / max(1, sum([fighter2.win_by_ko, fighter2.win_by_sub, fighter2.win_by_dec]))
        
        if abs(f1_finish_rate - f2_finish_rate) > 0.2:
            f1_score += (f1_finish_rate - f2_finish_rate) * 0.15
            factors.append(f"{'Higher' if f1_finish_rate > f2_finish_rate else 'Lower'} finish rate")
        
        # Recent form
        f1_form_score = self._calculate_form_score(fighter1.recent_form)
        f2_form_score = self._calculate_form_score(fighter2.recent_form)
        form_diff = f1_form_score - f2_form_score
        
        if abs(form_diff) > 0.2:
            f1_score += form_diff * 0.2
            factors.append(f"{'Better' if form_diff > 0 else 'Worse'} recent form")
        
        # Camp quality if available
        if fighter1.camp and fighter2.camp:
            camp1_score = self.camp_quality_scores.get(fighter1.camp, 0.75)
            camp2_score = self.camp_quality_scores.get(fighter2.camp, 0.75)
            if abs(camp1_score - camp2_score) > 0.05:
                f1_score += (camp1_score - camp2_score) * 0.1
                factors.append(f"Training at {'superior' if camp1_score > camp2_score else 'inferior'} camp")
        
        # Elevation adjustment if applicable
        if analysis.elevation and analysis.elevation > 4000:
            # High elevation favors better cardio
            if fighter1.avg_fight_time > fighter2.avg_fight_time:
                f1_score += 0.05
                factors.append(f"Better cardio for high elevation ({analysis.elevation}ft)")
        
        # Title fight experience
        if analysis.is_title_fight:
            # Would check title fight history in real implementation
            factors.append("Title fight experience factor")
        
        # Calculate final confidence
        confidence = min(0.85, max(0.15, abs(f1_score - 0.5) * 1.5 + 0.4))
        
        if f1_score >= 0.5:
            return fighter1.name, confidence, factors
        else:
            return fighter2.name, confidence, factors
    
    def _calculate_age_factor(self, age1: int, age2: int) -> Dict[str, Any]:
        """Calculate age-related advantages"""
        age_diff = age1 - age2
        
        # Optimal age range for MMA is typically 28-32
        optimal_age = 30
        distance1 = abs(age1 - optimal_age)
        distance2 = abs(age2 - optimal_age)
        
        advantage = (distance2 - distance1) * 0.01  # Small factor per year
        
        result = {
            "advantage": advantage,
            "significant": abs(age_diff) >= 5,
            "reason": ""
        }
        
        if abs(age_diff) >= 5:
            if age1 < age2 and age1 < 35:
                result["reason"] = f"Youth advantage ({age1} vs {age2})"
            elif age2 < age1 and age2 < 35:
                result["reason"] = f"Youth disadvantage ({age1} vs {age2})"
            elif age1 > 35 or age2 > 35:
                younger = age1 if age1 < age2 else age2
                result["reason"] = f"Age concerns for older fighter"
        
        return result
    
    def _calculate_form_score(self, recent_form: List[str]) -> float:
        """Calculate weighted form score (recent fights weighted more)"""
        if not recent_form:
            return 0.5
        
        weights = [0.35, 0.25, 0.20, 0.12, 0.08]  # Most recent to oldest
        score = 0.0
        
        for i, result in enumerate(recent_form[-5:]):
            if i < len(weights):
                score += weights[i] * (1.0 if result == "W" else 0.0)
        
        return score
    
    async def _predict_over_under_enhanced(
        self, 
        analysis: FightAnalysis
    ) -> Tuple[str, float, List[str]]:
        """Enhanced over/under prediction"""
        threshold = 1.5 if analysis.scheduled_rounds == 3 else 2.5
        reasoning = []
        
        # Calculate finish probability with more factors
        f1_finish_rate = (analysis.fighter1.win_by_ko + analysis.fighter1.win_by_sub) / max(1, 
            analysis.fighter1.win_by_ko + analysis.fighter1.win_by_sub + analysis.fighter1.win_by_dec)
        f2_finish_rate = (analysis.fighter2.win_by_ko + analysis.fighter2.win_by_sub) / max(1,
            analysis.fighter2.win_by_ko + analysis.fighter2.win_by_sub + analysis.fighter2.win_by_dec)
        
        combined_finish_rate = (f1_finish_rate + f2_finish_rate) / 2
        
        # Factor in average fight time
        avg_time = (analysis.fighter1.avg_fight_time + analysis.fighter2.avg_fight_time) / 2
        threshold_minutes = threshold * 5
        
        # Analyze pace and output
        combined_output = analysis.fighter1.sig_strikes_per_min + analysis.fighter2.sig_strikes_per_min
        
        # Decision factors
        under_factors = 0
        over_factors = 0
        
        if combined_finish_rate > 0.6:
            under_factors += 2
            reasoning.append(f"High combined finish rate ({combined_finish_rate:.1%})")
        
        if avg_time < threshold_minutes:
            under_factors += 1
            reasoning.append(f"Historical avg fight time ({avg_time:.1f} min) suggests early finish")
        else:
            over_factors += 1
            reasoning.append(f"Fighters typically go longer ({avg_time:.1f} min average)")
        
        if combined_output > 12:
            under_factors += 1
            reasoning.append("High output could lead to early finish")
        elif combined_output < 8:
            over_factors += 1
            reasoning.append("Lower output suggests longer fight")
        
        # Check for specific matchup factors
        if abs(analysis.fighter1.reach - analysis.fighter2.reach) > 5:
            over_factors += 1
            reasoning.append("Significant reach advantage could lead to technical fight")
        
        # Calculate confidence
        total_factors = under_factors + over_factors
        if under_factors > over_factors:
            confidence = 0.5 + (under_factors / total_factors) * 0.35
            return f"Under {threshold}", confidence, reasoning
        else:
            confidence = 0.5 + (over_factors / total_factors) * 0.35
            return f"Over {threshold}", confidence, reasoning
    
    async def _predict_method_enhanced(
        self, 
        analysis: FightAnalysis
    ) -> Tuple[str, float, List[str]]:
        """Enhanced method of victory prediction"""
        f1 = analysis.fighter1
        f2 = analysis.fighter2
        reasoning = []
        
        # Calculate detailed finish percentages
        f1_total = f1.win_by_ko + f1.win_by_sub + f1.win_by_dec
        f2_total = f2.win_by_ko + f2.win_by_sub + f2.win_by_dec
        
        if f1_total == 0 or f2_total == 0:
            return "Decision", 0.5, ["Insufficient data for method prediction"]
        
        # Combined method percentages
        ko_percentage = ((f1.win_by_ko + f2.win_by_ko) / (f1_total + f2_total))
        sub_percentage = ((f1.win_by_sub + f2.win_by_sub) / (f1_total + f2_total))
        dec_percentage = ((f1.win_by_dec + f2.win_by_dec) / (f1_total + f2_total))
        
        # Analyze specific factors
        method_scores = {
            "KO/TKO": ko_percentage,
            "Submission": sub_percentage,
            "Decision": dec_percentage
        }
        
        # Adjust based on fight factors
        if analysis.scheduled_rounds == 5:
            method_scores["Decision"] *= 1.2  # Longer fights favor decisions
            reasoning.append("5-round fight increases decision likelihood")
        
        # Check for specific advantages
        power_diff = abs(f1.sig_strikes_per_min - f2.sig_strikes_per_min)
        if power_diff > 2:
            method_scores["KO/TKO"] *= 1.15
            reasoning.append("Significant striking power differential")
        
        # Submission threats
        if f1.win_by_sub > 5 or f2.win_by_sub > 5:
            method_scores["Submission"] *= 1.2
            reasoning.append("High-level submission threat present")
        
        # Durability factors
        ko_losses = f1.losses_by_ko + f2.losses_by_ko
        if ko_losses > 3:
            method_scores["KO/TKO"] *= 1.1
            reasoning.append("Durability concerns increase KO probability")
        
        # Normalize scores
        total_score = sum(method_scores.values())
        for method in method_scores:
            method_scores[method] /= total_score
        
        # Get the most likely method
        best_method = max(method_scores.items(), key=lambda x: x[1])
        
        # Add specific reasoning for the chosen method
        if best_method[0] == "KO/TKO":
            reasoning.append(f"Combined KO rate: {ko_percentage:.1%}")
        elif best_method[0] == "Submission":
            reasoning.append(f"Combined submission rate: {sub_percentage:.1%}")
        else:
            reasoning.append(f"Combined decision rate: {dec_percentage:.1%}")
        
        return best_method[0], best_method[1], reasoning
    
    async def _enhance_prediction_with_llm(
        self,
        prediction: BettingRecommendation,
        analysis: FightAnalysis,
        llm_analysis: str
    ) -> List[str]:
        """Enhance prediction reasoning with LLM insights"""
        if not llm_service:
            return []
        
        prompt = f"""
        Based on this fight analysis, provide 2-3 specific technical reasons supporting a {prediction.pick} 
        {prediction.market.value} prediction:
        
        Analysis excerpt: {llm_analysis[:500]}...
        
        Current reasoning: {', '.join(prediction.reasoning[:3])}
        
        Add technical insights about:
        - Specific techniques or tendencies that support this prediction
        - Historical patterns in similar matchups
        - Camp or coaching factors
        - Any unique circumstances for this fight
        
        Be concise and specific to MMA technique.
        """
        
        try:
            enhanced_reasoning = await llm_service.generate_response(
                message=prompt,
                agent_persona="You are a technical MMA analyst providing specific fight insights.",
                temperature=0.6,
                max_tokens=200
            )
            
            # Parse into list of reasons
            reasons = [r.strip() for r in enhanced_reasoning.split('\n') if r.strip() and len(r.strip()) > 10]
            return reasons[:3]  # Limit to 3 additional reasons
            
        except Exception as e:
            logger.error(f"Error enhancing prediction: {e}")
            return []
    
    async def _apply_learning_adjustments(
        self,
        prediction: BettingRecommendation,
        analysis: FightAnalysis
    ) -> Optional[Dict[str, Any]]:
        """Apply learning system adjustments based on historical accuracy"""
        if not learning_system:
            return None
        
        try:
            # Get historical accuracy for this type of prediction
            market_accuracy = self.accuracy_stats.get(prediction.market.value, {})
            
            if market_accuracy.get('total', 0) < 10:
                return None  # Not enough data
            
            accuracy_rate = market_accuracy['correct'] / market_accuracy['total']
            
            # Adjust confidence based on historical accuracy
            adjustment = {
                'confidence_modifier': 1.0,
                'reason': f"Historical {prediction.market.value} accuracy: {accuracy_rate:.1%}"
            }
            
            if accuracy_rate > 0.65:
                adjustment['confidence_modifier'] = 1.1
                adjustment['reason'] += " (high accuracy)"
            elif accuracy_rate < 0.45:
                adjustment['confidence_modifier'] = 0.9
                adjustment['reason'] += " (low accuracy)"
            
            return adjustment
            
        except Exception as e:
            logger.error(f"Error applying learning adjustments: {e}")
            return None
    
    def _analyze_betting_value(
        self, 
        prediction: BettingRecommendation, 
        odds: float
    ) -> Dict[str, Any]:
        """Analyze if bet has positive expected value"""
        implied_prob = self._odds_to_probability(odds)
        edge = prediction.confidence - implied_prob
        
        return {
            'has_value': edge > 0.05,  # 5% minimum edge
            'edge': edge,
            'implied_probability': implied_prob,
            'true_probability': prediction.confidence,
            'kelly_stake': self._kelly_criterion(prediction.confidence, odds) if edge > 0.05 else 0
        }
    
    def _generate_detailed_reasoning(
        self,
        analysis: FightAnalysis,
        pick: str,
        factors: List[str]
    ) -> List[str]:
        """Generate detailed reasoning for pick"""
        reasoning = []
        winner = analysis.fighter1 if pick == analysis.fighter1.name else analysis.fighter2
        loser = analysis.fighter2 if pick == analysis.fighter1.name else analysis.fighter1
        
        # Add factor-based reasoning
        reasoning.extend(factors[:3])  # Top 3 factors
        
        # Add statistical comparisons
        if winner.striking_accuracy > loser.striking_accuracy:
            reasoning.append(f"Superior striking accuracy ({winner.striking_accuracy:.1%} vs {loser.striking_accuracy:.1%})")
        
        if winner.takedown_defense > loser.takedown_defense:
            reasoning.append(f"Better takedown defense ({winner.takedown_defense:.1%} vs {loser.takedown_defense:.1%})")
        
        # Add finish ability comparison
        winner_finishes = winner.win_by_ko + winner.win_by_sub
        loser_finishes = loser.win_by_ko + loser.win_by_sub
        if winner_finishes > loser_finishes:
            reasoning.append(f"More finishes ({winner_finishes} vs {loser_finishes})")
        
        return reasoning[:5]  # Limit to 5 reasons
    
    def _identify_detailed_risks(
        self,
        analysis: FightAnalysis,
        pick: str
    ) -> List[str]:
        """Identify detailed risks for the pick"""
        risks = ["MMA's inherent unpredictability"]
        
        loser = analysis.fighter2 if pick == analysis.fighter1.name else analysis.fighter1
        
        # Specific risks
        if loser.win_by_ko >= 10:
            risks.append(f"{loser.name} has significant KO power ({loser.win_by_ko} KO wins)")
        
        if loser.win_by_sub >= 5:
            risks.append(f"{loser.name} is a submission threat ({loser.win_by_sub} sub wins)")
        
        # Check recent losses
        pick_fighter = analysis.fighter1 if pick == analysis.fighter1.name else analysis.fighter2
        recent_losses = sum(1 for r in pick_fighter.recent_form[-3:] if r == "L")
        if recent_losses >= 2:
            risks.append(f"Concerning recent form ({recent_losses} losses in last 3)")
        
        # Cardio concerns for 5 rounds
        if analysis.scheduled_rounds == 5:
            if pick_fighter.avg_fight_time < 12:
                risks.append("Unproven in championship rounds")
        
        # Injury history
        if pick_fighter.injury_history:
            risks.append("Previous injury concerns")
        
        return risks[:4]  # Limit to 4 risks
    
    def _get_enhanced_method_factors(
        self, 
        method: str, 
        analysis: FightAnalysis
    ) -> List[str]:
        """Get enhanced factors for method prediction"""
        factors = []
        
        if method == "KO/TKO":
            factors.extend([
                "Power differential",
                "Chin durability history",
                "Striking volume",
                "Damage accumulation"
            ])
            
            # Add specific factors
            total_ko_power = analysis.fighter1.win_by_ko + analysis.fighter2.win_by_ko
            if total_ko_power > 20:
                factors.append("Combined 20+ KO victories")
                
        elif method == "Submission":
            factors.extend([
                "Grappling credentials",
                "Submission defense",
                "Scrambling ability",
                "Ground control time"
            ])
            
            # Add specific factors
            if analysis.fighter1.win_by_sub > 7 or analysis.fighter2.win_by_sub > 7:
                factors.append("Elite submission specialist present")
                
        else:  # Decision
            factors.extend([
                "Cardio levels",
                "Point fighting ability",
                "Defensive skills",
                "Championship round experience"
            ])
            
            if analysis.scheduled_rounds == 5:
                factors.append("5-round distance favors decision")
        
        return factors
    
    async def track_prediction_outcome(
        self,
        prediction_id: str,
        actual_outcome: str,
        fight_result: Dict[str, Any]
    ):
        """Track prediction outcomes for learning"""
        if not learning_system:
            return
        
        # Find the prediction
        prediction_data = None
        for pred in self.prediction_history:
            if pred.get('id') == prediction_id:
                prediction_data = pred
                break
        
        if not prediction_data:
            return
        
        # Determine if prediction was correct
        correct = False
        if prediction_data['market'] == BettingMarket.MONEYLINE.value:
            correct = prediction_data['pick'] == actual_outcome
        elif prediction_data['market'] == BettingMarket.OVER_UNDER.value:
            fight_duration = fight_result.get('duration_rounds', 0)
            threshold = float(prediction_data['pick'].split()[1])
            correct = (prediction_data['pick'].startswith("Over") and fight_duration > threshold) or \
                     (prediction_data['pick'].startswith("Under") and fight_duration < threshold)
        elif prediction_data['market'] == BettingMarket.METHOD_OF_VICTORY.value:
            correct = prediction_data['pick'].lower() in fight_result.get('method', '').lower()
        
        # Update accuracy stats
        market = prediction_data['market']
        self.accuracy_stats[market]['total'] += 1
        if correct:
            self.accuracy_stats[market]['correct'] += 1
        
        # Submit to learning system
        feedback_type = FeedbackType.APPROVED if correct else FeedbackType.REJECTED
        
        await learning_system.record_feedback(
            message_id=prediction_id,
            feedback_type=feedback_type,
            original_response=json.dumps(prediction_data),
            context={
                'actual_outcome': actual_outcome,
                'fight_result': fight_result,
                'prediction_confidence': prediction_data.get('confidence', 0),
                'was_correct': correct
            }
        )
        
        logger.info(f"Tracked prediction outcome: {prediction_id} - {'Correct' if correct else 'Incorrect'}")
    
    def _odds_to_probability(self, american_odds: float) -> float:
        """Convert American odds to implied probability"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    def _kelly_criterion(self, win_prob: float, american_odds: float) -> float:
        """Calculate optimal bet size using Kelly Criterion"""
        decimal_odds = self._american_to_decimal(american_odds)
        
        # Kelly formula: f = (bp - q) / b
        b = decimal_odds - 1
        p = win_prob
        q = 1 - p
        
        kelly = (b * p - q) / b
        
        # Use fractional Kelly (25%) for safety
        return max(0, min(0.10, kelly * 0.25))  # Cap at 10% of bankroll
    
    def _american_to_decimal(self, american_odds: float) -> float:
        """Convert American odds to decimal"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def get_enhanced_disclaimer(self) -> str:
        """Get enhanced gambling disclaimer"""
        return """
        🚨 IMPORTANT DISCLAIMER 🚨
        
        This AI-powered analysis is for ENTERTAINMENT PURPOSES ONLY.
        
        ⚠️ WARNINGS:
        - Gambling involves significant risk of financial loss
        - Never bet more than you can afford to lose
        - Past prediction accuracy does not guarantee future results
        - AI predictions are opinions based on data, not certainties
        - The house always maintains an edge
        
        📊 Our Current Accuracy (for transparency):
        - Moneyline: {ml_acc}%
        - Over/Under: {ou_acc}%
        - Method: {method_acc}%
        
        🆘 Problem Gambling Resources:
        - National Council on Problem Gambling: 1-800-522-4700
        - www.ncpgambling.org
        - Gamblers Anonymous: www.gamblersanonymous.org
        
        ⚖️ Legal Notice:
        - You must be of legal gambling age in your jurisdiction
        - Online gambling may not be legal in your area
        - This service does not facilitate betting
        - We are not responsible for any losses
        
        By using this service, you acknowledge that:
        ✓ You understand the risks involved
        ✓ You will gamble responsibly if you choose to bet
        ✓ You will seek help if gambling becomes a problem
        ✓ You accept full responsibility for your actions
        """.format(
            ml_acc=round(self.accuracy_stats['moneyline']['correct'] / max(1, self.accuracy_stats['moneyline']['total']) * 100, 1),
            ou_acc=round(self.accuracy_stats['over_under']['correct'] / max(1, self.accuracy_stats['over_under']['total']) * 100, 1),
            method_acc=round(self.accuracy_stats['method']['correct'] / max(1, self.accuracy_stats['method']['total']) * 100, 1)
        )