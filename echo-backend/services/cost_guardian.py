"""
Cost Guardian - Protects you from runaway API costs
CRITICAL: This service prevents financial damage
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass
import asyncio
from pathlib import Path

@dataclass
class CostLimits:
    """Your financial safety limits"""
    max_per_request: float = float(os.getenv('MAX_PER_REQUEST', '1.00'))
    max_daily: float = float(os.getenv('MAX_DAILY_COST', '10.00'))
    max_monthly: float = float(os.getenv('MAX_MONTHLY_COST', '100.00'))
    emergency_shutdown: float = float(os.getenv('EMERGENCY_SHUTDOWN_COST', '500.00'))
    
class CostGuardian:
    """
    Monitors and prevents excessive API spending
    SAVES YOUR WALLET
    """
    
    def __init__(self):
        self.limits = CostLimits()
        self.cost_file = Path('costs/usage_tracking.json')
        self.cost_file.parent.mkdir(exist_ok=True)
        
        # Cost tracking
        self.current_costs = self.load_costs()
        
        # Service costs (per 1K tokens)
        self.token_costs = {
            'gpt-3.5-turbo': 0.002,
            'gpt-4': 0.03,
            'gpt-4-turbo-preview': 0.01,
            'claude-3-opus': 0.025,
            'claude-3-sonnet': 0.003,
            'claude-3-haiku': 0.0025
        }
        
        # Other service costs
        self.service_costs = {
            'sms': 0.0075,
            'firebase_read': 0.06 / 100000,  # per document
            'firebase_write': 0.18 / 100000,  # per document
        }
        
        # Shutdown flag
        self.emergency_shutdown = False
        
    def load_costs(self) -> Dict[str, Any]:
        """Load current cost tracking"""
        if self.cost_file.exists():
            with open(self.cost_file, 'r') as f:
                return json.load(f)
        return {
            'daily': {},
            'monthly': {},
            'total': 0,
            'last_reset': datetime.now().isoformat()
        }
    
    def save_costs(self):
        """Persist cost tracking"""
        with open(self.cost_file, 'w') as f:
            json.dump(self.current_costs, f, indent=2)
    
    def check_before_api_call(
        self,
        service: str,
        estimated_tokens: int = 1000,
        model: str = None
    ) -> tuple[bool, str]:
        """
        CHECK BEFORE SPENDING MONEY
        Returns: (allowed, reason)
        """
        
        # Emergency shutdown check
        if self.emergency_shutdown:
            return False, "EMERGENCY SHUTDOWN - Costs exceeded limits"
        
        # Calculate estimated cost
        if model and model in self.token_costs:
            estimated_cost = (estimated_tokens / 1000) * self.token_costs[model]
        elif service in self.service_costs:
            estimated_cost = self.service_costs[service]
        else:
            estimated_cost = 0.10  # Default high estimate for safety
        
        # Check per-request limit
        if estimated_cost > self.limits.max_per_request:
            return False, f"Request cost ${estimated_cost:.2f} exceeds limit ${self.limits.max_per_request}"
        
        # Check daily limit
        today = datetime.now().strftime('%Y-%m-%d')
        daily_total = self.current_costs['daily'].get(today, 0) + estimated_cost
        
        if daily_total > self.limits.max_daily:
            return False, f"Daily limit reached: ${daily_total:.2f} > ${self.limits.max_daily}"
        
        # Check monthly limit
        month = datetime.now().strftime('%Y-%m')
        monthly_total = self.current_costs['monthly'].get(month, 0) + estimated_cost
        
        if monthly_total > self.limits.max_monthly:
            return False, f"Monthly limit reached: ${monthly_total:.2f} > ${self.limits.max_monthly}"
        
        # Check emergency shutdown threshold
        if self.current_costs['total'] + estimated_cost > self.limits.emergency_shutdown:
            self.emergency_shutdown = True
            return False, f"EMERGENCY: Total costs ${self.current_costs['total']:.2f} approaching shutdown limit"
        
        return True, f"Approved: ${estimated_cost:.2f}"
    
    def record_cost(
        self,
        service: str,
        actual_cost: float,
        metadata: Dict[str, Any] = None
    ):
        """Record actual cost after API call"""
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')
        
        # Update daily
        if today not in self.current_costs['daily']:
            self.current_costs['daily'][today] = 0
        self.current_costs['daily'][today] += actual_cost
        
        # Update monthly
        if month not in self.current_costs['monthly']:
            self.current_costs['monthly'][month] = 0
        self.current_costs['monthly'][month] += actual_cost
        
        # Update total
        self.current_costs['total'] += actual_cost
        
        # Log the cost
        print(f"💰 Cost recorded: {service} = ${actual_cost:.4f}")
        print(f"   Daily total: ${self.current_costs['daily'][today]:.2f}")
        print(f"   Monthly total: ${self.current_costs['monthly'][month]:.2f}")
        
        # Check if we should sound alarms
        if self.current_costs['daily'][today] > self.limits.max_daily * 0.8:
            print("⚠️  WARNING: Approaching daily limit!")
        
        if self.current_costs['monthly'][month] > self.limits.max_monthly * 0.8:
            print("🚨 ALERT: Approaching monthly limit!")
        
        self.save_costs()
    
    def get_current_usage(self) -> Dict[str, Any]:
        """Get current usage stats"""
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')
        
        return {
            'daily': {
                'used': self.current_costs['daily'].get(today, 0),
                'limit': self.limits.max_daily,
                'percentage': (self.current_costs['daily'].get(today, 0) / self.limits.max_daily) * 100
            },
            'monthly': {
                'used': self.current_costs['monthly'].get(month, 0),
                'limit': self.limits.max_monthly,
                'percentage': (self.current_costs['monthly'].get(month, 0) / self.limits.max_monthly) * 100
            },
            'total': self.current_costs['total'],
            'emergency_shutdown': self.emergency_shutdown
        }
    
    def estimate_message_cost(self, message: str, platform: str) -> float:
        """Estimate cost before processing"""
        # Rough token estimation (1 token ≈ 4 characters)
        tokens = len(message) / 4
        
        # Add system prompt tokens
        tokens += 500  # System prompt overhead
        
        # Add response tokens (estimate 2x input)
        tokens *= 3
        
        # Calculate based on default model
        model_cost = self.token_costs.get('claude-3-sonnet', 0.003)
        llm_cost = (tokens / 1000) * model_cost
        
        # Add platform costs
        platform_costs = {
            'sms': self.service_costs['sms'],
            'firebase': self.service_costs['firebase_write'] * 2  # Read + write
        }
        
        total = llm_cost + platform_costs.get(platform, 0)
        
        return total
    
    def create_cost_report(self) -> str:
        """Generate cost report"""
        usage = self.get_current_usage()
        
        report = f"""
💰 COST REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}
================================================

📅 DAILY USAGE:
   Spent: ${usage['daily']['used']:.2f} / ${usage['daily']['limit']:.2f}
   Used: {usage['daily']['percentage']:.1f}%
   
📆 MONTHLY USAGE:
   Spent: ${usage['monthly']['used']:.2f} / ${usage['monthly']['limit']:.2f}
   Used: {usage['monthly']['percentage']:.1f}%

💵 TOTAL SPENT: ${usage['total']:.2f}

⚡ STATUS: {'🚨 EMERGENCY SHUTDOWN' if usage['emergency_shutdown'] else '✅ OPERATIONAL'}

📊 BREAKDOWN BY SERVICE:
   (Implement detailed tracking)
   
⚠️  WARNINGS:
"""
        
        if usage['daily']['percentage'] > 80:
            report += "   - Daily limit almost reached!\n"
        if usage['monthly']['percentage'] > 80:
            report += "   - Monthly limit almost reached!\n"
        if usage['total'] > self.limits.emergency_shutdown * 0.5:
            report += "   - Approaching emergency shutdown threshold!\n"
            
        return report
    
    def reset_daily_costs(self):
        """Reset daily costs (run at midnight)"""
        # Clean up old daily entries (keep 30 days)
        cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        self.current_costs['daily'] = {
            k: v for k, v in self.current_costs['daily'].items()
            if k > cutoff
        }
        self.save_costs()
    
    def emergency_shutdown_all(self):
        """EMERGENCY: Stop all processing"""
        self.emergency_shutdown = True
        print("🚨🚨🚨 EMERGENCY SHUTDOWN ACTIVATED 🚨🚨🚨")
        print("ALL API CALLS BLOCKED")
        print("Current total: $", self.current_costs['total'])
        
        # Create shutdown file
        with open('EMERGENCY_SHUTDOWN.flag', 'w') as f:
            f.write(f"Shutdown at: {datetime.now()}\nTotal cost: ${self.current_costs['total']}")
        
        return "EMERGENCY SHUTDOWN COMPLETE"

# Global instance
cost_guardian = CostGuardian()

# Decorator for protecting expensive functions
def protect_with_cost_check(service: str, model: str = None):
    """Decorator to check costs before function execution"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Estimate cost
            estimated_tokens = kwargs.get('max_tokens', 1000)
            
            # Check if allowed
            allowed, reason = cost_guardian.check_before_api_call(
                service, estimated_tokens, model
            )
            
            if not allowed:
                raise Exception(f"COST PROTECTION: {reason}")
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Record actual cost (simplified - you'd calculate real cost)
            actual_cost = estimated_tokens / 1000 * 0.01  # Rough estimate
            cost_guardian.record_cost(service, actual_cost)
            
            return result
        return wrapper
    return decorator