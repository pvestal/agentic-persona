"""
UFC Betting Assistant Agent - Octagon Oracle
Analyzes UFC fights and provides betting insights (for entertainment purposes only)
Based on github.com/pvestal/ufc-betting-system
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
from dataclasses import dataclass
import asyncio
from decimal import Decimal

from crewai import Agent
from agents.base_agent import BaseAgent, AgentConfig

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
    record: str  # "25-3-0"
    height: int  # in inches
    reach: int   # in inches
    stance: str  # orthodox/southpaw
    age: int
    win_by_ko: int
    win_by_sub: int
    win_by_dec: int
    avg_fight_time: float  # minutes
    takedown_accuracy: float
    takedown_defense: float
    striking_accuracy: float
    striking_defense: float
    recent_form: List[str]  # Last 5 fights ["W", "W", "L", "W", "W"]

@dataclass
class FightAnalysis:
    fighter1: FighterStats
    fighter2: FighterStats
    weight_class: WeightClass
    is_title_fight: bool
    is_main_event: bool
    scheduled_rounds: int
    
@dataclass
class BettingRecommendation:
    market: BettingMarket
    pick: str
    confidence: float  # 0-1
    expected_value: float
    reasoning: List[str]
    key_factors: List[str]
    risks: List[str]

class UFCBettingAssistant(BaseAgent):
    """AI-powered UFC fight analysis and betting insights"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Use a fight-themed name
        default_config = {
            "name": "Octagon Oracle",
            "full_name": "Octagon Oracle - UFC Analysis Expert",
            "role": "UFC fight analyst and betting strategist",
            "goal": "provide data-driven UFC fight analysis and betting insights",
            "backstory": """I am Octagon Oracle, your expert UFC fight analyst. I study fighter 
            statistics, styles, matchups, and historical data to provide insights for fight outcomes. 
            I emphasize responsible gambling and remind users that all predictions are for entertainment 
            purposes only. My analysis combines technical fighting knowledge with statistical patterns.""",
            "tools": [],
            "verbose": True,
            "allow_delegation": False,
            "max_iter": 5
        }
        
        if config:
            default_config.update(config)
        
        super().__init__(AgentConfig(**default_config))
        
        # Initialize analysis factors
        self.style_matchups = {
            "wrestler_vs_striker": {
                "factors": ["takedown_defense", "sprawl", "ground_control"],
                "advantage": "wrestler if TD% > 45% and striker TDD < 70%"
            },
            "pressure_vs_counter": {
                "factors": ["forward_pressure", "cardio", "chin"],
                "advantage": "pressure if cardio advantage and good chin"
            },
            "orthodox_vs_southpaw": {
                "factors": ["stance_familiarity", "lead_hand_usage"],
                "advantage": "southpaw historically +5% win rate"
            }
        }
        
        self.key_metrics = [
            "significant_strikes_per_minute",
            "striking_accuracy",
            "takedown_average",
            "submission_average",
            "average_fight_time",
            "finish_rate"
        ]
    
    async def analyze_matchup(
        self, 
        fighter1: FighterStats, 
        fighter2: FighterStats,
        fight_details: Dict[str, Any]
    ) -> FightAnalysis:
        """Analyze the matchup between two fighters"""
        
        analysis = FightAnalysis(
            fighter1=fighter1,
            fighter2=fighter2,
            weight_class=WeightClass(fight_details.get("weight_class", "lightweight")),
            is_title_fight=fight_details.get("is_title_fight", False),
            is_main_event=fight_details.get("is_main_event", False),
            scheduled_rounds=fight_details.get("rounds", 3)
        )
        
        return analysis
    
    def _calculate_style_advantage(
        self, 
        fighter1: FighterStats, 
        fighter2: FighterStats
    ) -> Tuple[str, float]:
        """Calculate which fighter has the style advantage"""
        advantages = []
        
        # Wrestler vs Striker
        if fighter1.takedown_accuracy > 0.45 and fighter2.takedown_defense < 0.70:
            advantages.append((fighter1.name, 0.15, "wrestling advantage"))
        elif fighter2.takedown_accuracy > 0.45 and fighter1.takedown_defense < 0.70:
            advantages.append((fighter2.name, 0.15, "wrestling advantage"))
        
        # Reach advantage
        reach_diff = abs(fighter1.reach - fighter2.reach)
        if reach_diff >= 3:
            longer_fighter = fighter1 if fighter1.reach > fighter2.reach else fighter2
            advantages.append((longer_fighter.name, 0.08, f"{reach_diff}in reach advantage"))
        
        # Age and experience
        age_diff = abs(fighter1.age - fighter2.age)
        if age_diff >= 5:
            younger_fighter = fighter1 if fighter1.age < fighter2.age else fighter2
            # Younger is usually better unless very inexperienced
            advantages.append((younger_fighter.name, 0.05, "age advantage"))
        
        # Recent form
        def form_score(form):
            return sum(1 for result in form[-5:] if result == "W") / min(5, len(form))
        
        f1_form = form_score(fighter1.recent_form)
        f2_form = form_score(fighter2.recent_form)
        
        if abs(f1_form - f2_form) >= 0.4:
            better_form = fighter1 if f1_form > f2_form else fighter2
            advantages.append((better_form.name, 0.10, "better recent form"))
        
        # Calculate total advantage
        if not advantages:
            return "even", 0.0
        
        fighter_advantages = {}
        for fighter, adv, reason in advantages:
            if fighter not in fighter_advantages:
                fighter_advantages[fighter] = 0
            fighter_advantages[fighter] += adv
        
        best_fighter = max(fighter_advantages.items(), key=lambda x: x[1])
        return best_fighter[0], best_fighter[1]
    
    async def generate_predictions(
        self, 
        analysis: FightAnalysis
    ) -> List[BettingRecommendation]:
        """Generate betting predictions for the fight"""
        predictions = []
        
        # Moneyline prediction
        ml_pick, ml_confidence = await self._predict_winner(analysis)
        predictions.append(BettingRecommendation(
            market=BettingMarket.MONEYLINE,
            pick=ml_pick,
            confidence=ml_confidence,
            expected_value=self._calculate_expected_value(ml_pick, ml_confidence),
            reasoning=self._generate_reasoning(analysis, ml_pick),
            key_factors=self._identify_key_factors(analysis),
            risks=self._identify_risks(analysis, ml_pick)
        ))
        
        # Over/Under prediction
        ou_pick, ou_confidence = await self._predict_over_under(analysis)
        predictions.append(BettingRecommendation(
            market=BettingMarket.OVER_UNDER,
            pick=ou_pick,
            confidence=ou_confidence,
            expected_value=self._calculate_expected_value(ou_pick, ou_confidence),
            reasoning=[f"Fight likely goes {ou_pick}"],
            key_factors=["finish_rate", "cardio", "fight_style"],
            risks=["Early finish possibility", "Pace uncertainty"]
        ))
        
        # Method of victory
        method_pick, method_confidence = await self._predict_method(analysis)
        if method_confidence > 0.6:  # Only recommend if confident
            predictions.append(BettingRecommendation(
                market=BettingMarket.METHOD_OF_VICTORY,
                pick=method_pick,
                confidence=method_confidence,
                expected_value=self._calculate_expected_value(method_pick, method_confidence),
                reasoning=[f"Most likely outcome: {method_pick}"],
                key_factors=self._get_method_factors(method_pick),
                risks=["Multiple paths to victory", "Fight dynamics"]
            ))
        
        return predictions
    
    async def _predict_winner(
        self, 
        analysis: FightAnalysis
    ) -> Tuple[str, float]:
        """Predict the fight winner"""
        fighter1 = analysis.fighter1
        fighter2 = analysis.fighter2
        
        # Base prediction on multiple factors
        f1_score = 0.5  # Start even
        
        # Style advantage
        style_winner, style_adv = self._calculate_style_advantage(fighter1, fighter2)
        if style_winner == fighter1.name:
            f1_score += style_adv
        else:
            f1_score -= style_adv
        
        # Statistical advantages
        if fighter1.striking_accuracy > fighter2.striking_accuracy:
            f1_score += 0.05
        if fighter1.takedown_defense > fighter2.takedown_defense:
            f1_score += 0.05
        if fighter1.win_by_ko + fighter1.win_by_sub > fighter2.win_by_ko + fighter2.win_by_sub:
            f1_score += 0.08  # Finish ability
        
        # Cap confidence
        confidence = min(0.85, max(0.15, abs(f1_score - 0.5) + 0.5))
        
        if f1_score >= 0.5:
            return fighter1.name, confidence
        else:
            return fighter2.name, confidence
    
    async def _predict_over_under(
        self, 
        analysis: FightAnalysis
    ) -> Tuple[str, float]:
        """Predict if fight goes over/under rounds threshold"""
        # Usually 1.5 rounds for 3-round fights, 2.5 for 5-round fights
        threshold = 1.5 if analysis.scheduled_rounds == 3 else 2.5
        
        # Calculate finish probability
        f1_finish_rate = (analysis.fighter1.win_by_ko + analysis.fighter1.win_by_sub) / 10  # Simplified
        f2_finish_rate = (analysis.fighter2.win_by_ko + analysis.fighter2.win_by_sub) / 10
        
        combined_finish_rate = (f1_finish_rate + f2_finish_rate) / 2
        
        # Adjust for fight time history
        avg_fight_time = (analysis.fighter1.avg_fight_time + analysis.fighter2.avg_fight_time) / 2
        
        if avg_fight_time < threshold * 5:  # Convert rounds to minutes
            return "Under", 0.65
        else:
            return "Over", 0.60
    
    async def _predict_method(
        self, 
        analysis: FightAnalysis
    ) -> Tuple[str, float]:
        """Predict method of victory"""
        f1 = analysis.fighter1
        f2 = analysis.fighter2
        
        # Simple method prediction based on historical finishes
        total_finishes = f1.win_by_ko + f1.win_by_sub + f2.win_by_ko + f2.win_by_sub
        total_decisions = f1.win_by_dec + f2.win_by_dec
        
        if total_finishes > total_decisions * 1.5:
            # Likely finish
            if (f1.win_by_ko + f2.win_by_ko) > (f1.win_by_sub + f2.win_by_sub):
                return "KO/TKO", 0.55
            else:
                return "Submission", 0.50
        else:
            return "Decision", 0.65
    
    def _generate_reasoning(
        self, 
        analysis: FightAnalysis, 
        pick: str
    ) -> List[str]:
        """Generate reasoning for the pick"""
        reasons = []
        
        winner = analysis.fighter1 if pick == analysis.fighter1.name else analysis.fighter2
        loser = analysis.fighter2 if pick == analysis.fighter1.name else analysis.fighter1
        
        # Add specific reasons
        if winner.reach > loser.reach:
            reasons.append(f"{winner.reach - loser.reach}in reach advantage")
        
        if winner.takedown_defense > 0.75:
            reasons.append("Excellent takedown defense")
        
        if winner.striking_accuracy > loser.striking_accuracy:
            reasons.append(f"Better striking accuracy ({winner.striking_accuracy:.1%} vs {loser.striking_accuracy:.1%})")
        
        # Recent form
        winner_form_score = sum(1 for r in winner.recent_form[-5:] if r == "W") / 5
        if winner_form_score >= 0.8:
            reasons.append(f"Strong recent form ({int(winner_form_score * 5)}-{int((1-winner_form_score) * 5)} last 5)")
        
        return reasons
    
    def _identify_key_factors(self, analysis: FightAnalysis) -> List[str]:
        """Identify key factors for the fight"""
        factors = []
        
        # Stylistic factors
        if abs(analysis.fighter1.reach - analysis.fighter2.reach) >= 3:
            factors.append("Significant reach differential")
        
        if analysis.is_title_fight:
            factors.append("Championship experience")
        
        if analysis.scheduled_rounds == 5:
            factors.append("5-round cardio crucial")
        
        # Check for striker vs grappler
        f1_striking = analysis.fighter1.win_by_ko / max(1, analysis.fighter1.win_by_ko + analysis.fighter1.win_by_sub + analysis.fighter1.win_by_dec)
        f2_striking = analysis.fighter2.win_by_ko / max(1, analysis.fighter2.win_by_ko + analysis.fighter2.win_by_sub + analysis.fighter2.win_by_dec)
        
        if abs(f1_striking - f2_striking) > 0.3:
            factors.append("Classic striker vs grappler matchup")
        
        return factors
    
    def _identify_risks(
        self, 
        analysis: FightAnalysis, 
        pick: str
    ) -> List[str]:
        """Identify betting risks"""
        risks = []
        
        # General risks
        risks.append("MMA is inherently unpredictable")
        
        # Specific risks
        if analysis.is_title_fight and analysis.scheduled_rounds == 5:
            risks.append("5-round fight cardio uncertainty")
        
        loser = analysis.fighter2 if pick == analysis.fighter1.name else analysis.fighter1
        if loser.win_by_ko >= 10:
            risks.append(f"{loser.name} has knockout power")
        
        if any(r == "L" for r in analysis.fighter1.recent_form[-3:]) or any(r == "L" for r in analysis.fighter2.recent_form[-3:]):
            risks.append("Recent losses may impact performance")
        
        return risks
    
    def _calculate_expected_value(self, pick: str, confidence: float) -> float:
        """Calculate expected value (simplified)"""
        # In real implementation, would use actual odds
        # For now, assume even odds
        implied_probability = 0.5
        
        if confidence > implied_probability:
            return (confidence - implied_probability) * 100
        else:
            return -((implied_probability - confidence) * 100)
    
    def _get_method_factors(self, method: str) -> List[str]:
        """Get factors for method prediction"""
        if method == "KO/TKO":
            return ["Striking power", "Chin durability", "Accumulated damage"]
        elif method == "Submission":
            return ["Grappling skill", "Submission defense", "Cardio"]
        else:  # Decision
            return ["Cardio", "Volume striking", "Octagon control"]
    
    async def analyze_betting_value(
        self, 
        predictions: List[BettingRecommendation],
        odds: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Analyze betting value based on odds"""
        value_bets = []
        
        for pred in predictions:
            if pred.market == BettingMarket.MONEYLINE and pred.pick in odds:
                implied_prob = self._odds_to_probability(odds[pred.pick])
                
                if pred.confidence > implied_prob + 0.05:  # 5% edge minimum
                    value_bets.append({
                        "bet": pred.pick,
                        "confidence": pred.confidence,
                        "implied_probability": implied_prob,
                        "edge": pred.confidence - implied_prob,
                        "recommended_stake": self._kelly_criterion(pred.confidence, odds[pred.pick])
                    })
        
        return value_bets
    
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
        # where b = decimal odds - 1, p = win probability, q = 1 - p
        b = decimal_odds - 1
        p = win_prob
        q = 1 - p
        
        kelly = (b * p - q) / b
        
        # Use fractional Kelly (25%) for safety
        return max(0, min(0.1, kelly * 0.25))  # Cap at 10% of bankroll
    
    def _american_to_decimal(self, american_odds: float) -> float:
        """Convert American odds to decimal"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def get_disclaimer(self) -> str:
        """Get gambling disclaimer"""
        return """
        IMPORTANT DISCLAIMER:
        
        This analysis is for ENTERTAINMENT PURPOSES ONLY.
        
        - Gambling involves risk of loss
        - Never bet more than you can afford to lose
        - Past performance doesn't guarantee future results
        - Seek help if gambling becomes a problem
        
        Gambling Problem? Call 1-800-GAMBLER
        
        By using this service, you acknowledge that:
        - You are of legal gambling age in your jurisdiction
        - Online gambling may not be legal in your area
        - All predictions are opinions, not guarantees
        - The house always has an edge
        """

# Example fighter data structure
"""
fighter1 = FighterStats(
    name="Fighter One",
    record="25-3-0",
    height=72,  # 6'0"
    reach=74,
    stance="orthodox",
    age=29,
    win_by_ko=12,
    win_by_sub=5,
    win_by_dec=8,
    avg_fight_time=11.5,  # minutes
    takedown_accuracy=0.45,
    takedown_defense=0.82,
    striking_accuracy=0.48,
    striking_defense=0.65,
    recent_form=["W", "W", "W", "L", "W"]
)
"""