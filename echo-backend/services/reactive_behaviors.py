"""
Reactive Behaviors Service - Makes agents proactive and responsive
"""
from datetime import datetime, time
from typing import Dict, List, Optional, Callable, Any
import asyncio
from enum import Enum
import json

class TriggerType(Enum):
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    PATTERN_BASED = "pattern_based"
    CONTEXT_BASED = "context_based"

class ReactiveBehavior:
    def __init__(
        self,
        name: str,
        trigger_type: TriggerType,
        condition: Callable[[], bool],
        action: Callable[[], Any],
        description: str,
        priority: int = 5
    ):
        self.name = name
        self.trigger_type = trigger_type
        self.condition = condition
        self.action = action
        self.description = description
        self.priority = priority
        self.last_triggered = None
        self.trigger_count = 0

class ReactiveBehaviorEngine:
    def __init__(self):
        self.behaviors: Dict[str, ReactiveBehavior] = {}
        self.running = False
        self.check_interval = 60  # seconds
        self.context: Dict[str, Any] = {
            "user_state": "active",
            "last_interaction": datetime.now(),
            "message_queue": [],
            "platform_states": {},
            "user_preferences": {}
        }
        
    def register_behavior(self, behavior: ReactiveBehavior):
        """Register a new reactive behavior"""
        self.behaviors[behavior.name] = behavior
        
    def update_context(self, updates: Dict[str, Any]):
        """Update the context that behaviors can react to"""
        self.context.update(updates)
        # Check event-based behaviors immediately
        asyncio.create_task(self._check_event_behaviors())
        
    async def _check_event_behaviors(self):
        """Check behaviors triggered by events"""
        for behavior in self.behaviors.values():
            if behavior.trigger_type == TriggerType.EVENT_BASED:
                try:
                    if await behavior.condition(self.context):
                        await self._execute_behavior(behavior)
                except Exception as e:
                    print(f"Error checking behavior {behavior.name}: {e}")
                    
    async def _execute_behavior(self, behavior: ReactiveBehavior):
        """Execute a behavior's action"""
        try:
            result = await behavior.action(self.context)
            behavior.last_triggered = datetime.now()
            behavior.trigger_count += 1
            print(f"Executed behavior: {behavior.name}")
            return result
        except Exception as e:
            print(f"Error executing behavior {behavior.name}: {e}")
            
    async def start(self):
        """Start the reactive behavior engine"""
        self.running = True
        asyncio.create_task(self._monitor_loop())
        
    async def stop(self):
        """Stop the reactive behavior engine"""
        self.running = False
        
    async def _monitor_loop(self):
        """Main monitoring loop for time-based behaviors"""
        while self.running:
            for behavior in self.behaviors.values():
                if behavior.trigger_type == TriggerType.TIME_BASED:
                    try:
                        if await behavior.condition(self.context):
                            await self._execute_behavior(behavior)
                    except Exception as e:
                        print(f"Error in monitor loop for {behavior.name}: {e}")
            await asyncio.sleep(self.check_interval)

# Example reactive behaviors
def create_default_behaviors():
    """Create a set of default reactive behaviors"""
    behaviors = []
    
    # Daily Summary Behavior
    async def daily_summary_condition(context):
        now = datetime.now()
        # Check if it's 9 AM and we haven't sent today
        if now.hour == 9 and now.minute < 1:
            last_summary = context.get("last_daily_summary")
            if not last_summary or last_summary.date() < now.date():
                return True
        return False
        
    async def daily_summary_action(context):
        # Generate daily summary
        summary = {
            "type": "daily_summary",
            "timestamp": datetime.now().isoformat(),
            "content": {
                "pending_messages": len(context.get("message_queue", [])),
                "yesterday_activity": "Generated placeholder summary",
                "today_priorities": ["Check important emails", "Review calendar"],
                "suggested_actions": ["Respond to urgent messages", "Prepare for meetings"]
            }
        }
        context["last_daily_summary"] = datetime.now()
        return summary
        
    behaviors.append(ReactiveBehavior(
        name="daily_summary",
        trigger_type=TriggerType.TIME_BASED,
        condition=daily_summary_condition,
        action=daily_summary_action,
        description="Generates a daily summary at 9 AM",
        priority=8
    ))
    
    # Inactivity Alert Behavior
    async def inactivity_condition(context):
        last_interaction = context.get("last_interaction")
        if last_interaction:
            time_since = datetime.now() - last_interaction
            # Alert if no interaction for 2 hours during work hours
            if time_since.seconds > 7200 and 9 <= datetime.now().hour <= 17:
                return True
        return False
        
    async def inactivity_action(context):
        alert = {
            "type": "inactivity_alert",
            "timestamp": datetime.now().isoformat(),
            "content": {
                "message": "You've been inactive for a while. Any tasks I can help with?",
                "suggestions": ["Check messages", "Review todo list", "Take a break"]
            }
        }
        return alert
        
    behaviors.append(ReactiveBehavior(
        name="inactivity_alert",
        trigger_type=TriggerType.TIME_BASED,
        condition=inactivity_condition,
        action=inactivity_action,
        description="Alerts user about inactivity during work hours",
        priority=5
    ))
    
    # Important Message Detection
    async def important_message_condition(context):
        messages = context.get("message_queue", [])
        for msg in messages:
            if msg.get("priority") == "high" and not msg.get("processed"):
                return True
        return False
        
    async def important_message_action(context):
        messages = context.get("message_queue", [])
        important_msgs = [m for m in messages if m.get("priority") == "high" and not m.get("processed")]
        
        notification = {
            "type": "important_message_alert",
            "timestamp": datetime.now().isoformat(),
            "content": {
                "count": len(important_msgs),
                "messages": important_msgs[:3],  # First 3 important messages
                "action_required": True
            }
        }
        
        # Mark as processed
        for msg in important_msgs:
            msg["processed"] = True
            
        return notification
        
    behaviors.append(ReactiveBehavior(
        name="important_message_detection",
        trigger_type=TriggerType.EVENT_BASED,
        condition=important_message_condition,
        action=important_message_action,
        description="Detects and alerts about important messages",
        priority=10
    ))
    
    # Pattern Recognition - Routine Disruption
    async def routine_disruption_condition(context):
        # Simplified pattern detection
        current_hour = datetime.now().hour
        expected_state = "active" if 9 <= current_hour <= 17 else "idle"
        actual_state = context.get("user_state", "active")
        
        if expected_state != actual_state:
            last_alert = context.get("last_routine_alert")
            if not last_alert or (datetime.now() - last_alert).seconds > 3600:
                return True
        return False
        
    async def routine_disruption_action(context):
        alert = {
            "type": "routine_disruption",
            "timestamp": datetime.now().isoformat(),
            "content": {
                "message": "Noticed a change in your usual pattern. Everything okay?",
                "detected_pattern": "Unusual activity state for this time",
                "suggestions": ["Update your status", "Set away message", "Continue as normal"]
            }
        }
        context["last_routine_alert"] = datetime.now()
        return alert
        
    behaviors.append(ReactiveBehavior(
        name="routine_disruption_detection",
        trigger_type=TriggerType.PATTERN_BASED,
        condition=routine_disruption_condition,
        action=routine_disruption_action,
        description="Detects disruptions in user routine",
        priority=6
    ))
    
    return behaviors