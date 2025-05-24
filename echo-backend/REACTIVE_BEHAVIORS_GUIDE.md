# Reactive Behaviors Developer Guide

## Overview

The Reactive Behaviors system makes ECHO proactive rather than purely responsive. It allows agents to take autonomous actions based on time, events, patterns, and context changes.

## Architecture

```
ReactiveBehaviorEngine
├── Behaviors (Dict[str, ReactiveBehavior])
├── Context (Dict[str, Any])
├── Monitor Loop (async)
└── WebSocket Integration
```

## Core Components

### 1. ReactiveBehavior Class

```python
class ReactiveBehavior:
    name: str              # Unique identifier
    trigger_type: TriggerType  # TIME_BASED, EVENT_BASED, PATTERN_BASED, CONTEXT_BASED
    condition: Callable    # Function that returns True when behavior should trigger
    action: Callable       # Function executed when triggered
    description: str       # Human-readable description
    priority: int         # 1-10, higher = more important
```

### 2. Trigger Types

- **TIME_BASED**: Checked periodically (every 60 seconds by default)
- **EVENT_BASED**: Triggered immediately when context updates
- **PATTERN_BASED**: Analyzed when patterns emerge in data
- **CONTEXT_BASED**: Activated by specific context changes

## Creating Custom Behaviors

### Example: Meeting Reminder Behavior

```python
async def meeting_reminder_condition(context):
    """Check if there's a meeting in 15 minutes"""
    current_time = datetime.now()
    meetings = context.get("calendar_events", [])
    
    for meeting in meetings:
        meeting_time = datetime.fromisoformat(meeting["start_time"])
        time_until = (meeting_time - current_time).total_seconds() / 60
        
        if 14 <= time_until <= 16:  # 14-16 minutes before
            last_reminder = context.get(f"reminded_{meeting['id']}")
            if not last_reminder:
                return True
    return False

async def meeting_reminder_action(context):
    """Send meeting reminder"""
    # Find the upcoming meeting
    meetings = context.get("calendar_events", [])
    current_time = datetime.now()
    
    for meeting in meetings:
        meeting_time = datetime.fromisoformat(meeting["start_time"])
        time_until = (meeting_time - current_time).total_seconds() / 60
        
        if 14 <= time_until <= 16:
            context[f"reminded_{meeting['id']}"] = current_time
            
            return {
                "type": "meeting_reminder",
                "timestamp": current_time.isoformat(),
                "content": {
                    "meeting": meeting["title"],
                    "time": meeting["start_time"],
                    "location": meeting.get("location", "No location specified"),
                    "attendees": meeting.get("attendees", []),
                    "preparation_tips": [
                        "Review agenda",
                        "Prepare questions",
                        "Test audio/video"
                    ]
                }
            }

# Register the behavior
behavior = ReactiveBehavior(
    name="meeting_reminder",
    trigger_type=TriggerType.TIME_BASED,
    condition=meeting_reminder_condition,
    action=meeting_reminder_action,
    description="Reminds about meetings 15 minutes before",
    priority=9
)
engine.register_behavior(behavior)
```

## WebSocket Integration

Behaviors automatically broadcast notifications through WebSocket:

```javascript
// Frontend WebSocket handler
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'reactive_notification') {
        // Handle the notification
        displayNotification(data.notification);
        updateUIState(data.notification.type);
    }
};
```

## API Endpoints

### Get All Behaviors
```
GET /api/behaviors/
```

### Trigger Specific Behavior
```
POST /api/behaviors/trigger/{behavior_name}
```

### Update Context
```
POST /api/behaviors/context
Body: { "key": "value", ... }
```

### Simulate Event
```
POST /api/behaviors/simulate-event
Body: {
    "type": "message_received|user_inactive|user_active",
    "priority": "high|normal|low",
    "content": "..."
}
```

## Context Management

The context is a shared state dictionary that behaviors use for decisions:

```python
context = {
    "user_state": "active|idle|away",
    "last_interaction": datetime,
    "message_queue": [],
    "platform_states": {
        "email": {"unread": 5},
        "slack": {"mentions": 2}
    },
    "user_preferences": {
        "work_hours": {"start": 9, "end": 17},
        "vip_contacts": ["boss@company.com"]
    },
    "calendar_events": [],
    "learning_data": {}
}
```

## Best Practices

### 1. Behavior Design
- Keep conditions lightweight and fast
- Avoid blocking operations in conditions
- Use priority levels appropriately
- Document expected context keys

### 2. Action Implementation
- Always return a structured result
- Include timestamp and type
- Keep actions idempotent when possible
- Handle errors gracefully

### 3. Context Updates
- Update context atomically
- Clean up temporary context keys
- Use namespaced keys for behavior-specific data
- Limit array sizes (e.g., message_queue)

### 4. Testing
```python
# Test a behavior manually
async def test_behavior():
    engine = ReactiveBehaviorEngine()
    
    # Set up test context
    engine.update_context({
        "test_condition": True
    })
    
    # Register test behavior
    engine.register_behavior(test_behavior)
    
    # Trigger manually
    result = await engine.trigger_behavior("test_behavior")
    assert result is not None
```

## Common Patterns

### 1. Throttled Behaviors
```python
async def throttled_condition(context):
    last_run = context.get("last_throttled_run")
    if not last_run:
        return True
    
    time_since = datetime.now() - last_run
    return time_since.seconds > 3600  # Once per hour
```

### 2. Conditional Chains
```python
async def chain_condition(context):
    # Only run if previous behavior succeeded
    return context.get("previous_behavior_success") == True
```

### 3. User Preference Respect
```python
async def respectful_condition(context):
    # Check user preferences
    if not context.get("user_preferences", {}).get("enable_notifications", True):
        return False
    
    # Check do-not-disturb
    current_hour = datetime.now().hour
    work_hours = context.get("user_preferences", {}).get("work_hours", {})
    
    return work_hours.get("start", 9) <= current_hour < work_hours.get("end", 17)
```

## Debugging

Enable debug logging:
```python
# In settings.py
DEBUG = True

# In your behavior
async def debug_action(context):
    print(f"Behavior triggered with context: {context}")
    # ... rest of action
```

Monitor behavior performance:
```python
# Check behavior statistics
behaviors = await fetch("/api/behaviors/")
for b in behaviors["behaviors"]:
    print(f"{b['name']}: triggered {b['trigger_count']} times")
```

## Future Extensions

1. **Machine Learning Integration**
   - Learn optimal trigger times
   - Predict user needs
   - Adjust priorities dynamically

2. **Multi-Agent Coordination**
   - Behaviors that involve multiple agents
   - Shared context across agents
   - Conflict resolution

3. **External Integrations**
   - Calendar APIs
   - Email providers
   - Task management systems
   - IoT devices

4. **Advanced Patterns**
   - Workflow orchestration
   - Complex event processing
   - Predictive analytics