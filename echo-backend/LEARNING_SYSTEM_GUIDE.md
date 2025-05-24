# Learning System Guide

## Overview
The ECHO Learning System continuously improves response generation by learning from user feedback. It tracks patterns, analyzes edits, and adapts to user preferences over time.

## Features

### 1. Feedback Collection
- **Approve**: Mark responses as correct
- **Reject**: Mark responses as inappropriate
- **Edit**: Provide corrected versions
- **Rating**: Score response quality (coming soon)

### 2. Pattern Recognition
- Tracks common edits and corrections
- Identifies preferred phrases and styles
- Learns communication patterns per platform
- Adapts to individual user preferences

### 3. Real-time Improvement
- Applies learned patterns to new responses
- Suggests improvements based on past feedback
- Adjusts tone and length automatically
- Maintains context-aware adaptations

## How It Works

### Feedback Loop
1. **Generate**: AI creates initial response
2. **Review**: User reviews the response
3. **Feedback**: User approves, rejects, or edits
4. **Learn**: System analyzes feedback patterns
5. **Improve**: Future responses incorporate learnings

### Learning Algorithms
- **Edit Distance**: Measures similarity between original and edited responses
- **Pattern Matching**: Identifies common corrections
- **Confidence Scoring**: Weights feedback by consistency
- **Contextual Analysis**: Considers platform, sender, and message type

## Using the Interactive Demo

### Basic Workflow
1. Send a message through the Message Processing form
2. Review the generated response
3. Provide feedback using the buttons:
   - ✅ **Approve**: Response is perfect
   - ✏️ **Edit**: Make corrections
   - ❌ **Reject**: Response is inappropriate

### Viewing Insights
- Click "View Learning Trends" to see patterns
- Insights update in real-time as you provide feedback
- Monitor approval rates and improvement areas

## API Endpoints

### Submit Feedback
```bash
POST /api/learning/feedback
{
  "message_id": "msg_123",
  "feedback_type": "edited",
  "original_response": "Original text",
  "edited_response": "Corrected text",
  "context": {
    "platform": "email",
    "sender": "john@example.com"
  }
}
```

### Get User Preferences
```bash
GET /api/learning/preferences/{user_id}
```

### View Learning Trends
```bash
GET /api/learning/trends?days=7
```

### Get Learning Insights
```bash
GET /api/learning/insights
```

## Learning Metrics

### Tracked Data
- **Response Quality**: Approval/rejection rates
- **Edit Patterns**: Common corrections
- **Length Preferences**: Optimal response lengths
- **Tone Analysis**: Formal vs casual preferences
- **Platform Differences**: Per-platform adaptations

### Improvement Areas
The system identifies and tracks:
- Response length consistency
- Tone matching accuracy
- Technical explanation clarity
- Greeting/closing preferences
- Time-of-day variations

## Best Practices

### For Users
1. **Be Consistent**: Provide feedback regularly
2. **Edit Specifics**: Make precise corrections
3. **Use Platform Correctly**: Select the right platform
4. **Review Patterns**: Check learning trends periodically

### For Developers
1. **Batch Feedback**: Submit multiple feedbacks together
2. **Include Context**: Always provide platform and sender
3. **Monitor Confidence**: Check confidence scores
4. **Test Improvements**: Verify learned patterns work

## Privacy & Security

### Data Handling
- Feedback is stored locally
- No personal data in learning patterns
- Anonymized aggregation for trends
- User-specific data isolation

### Access Control
- User can only access their own preferences
- Admins can view aggregated trends
- No cross-user data leakage
- Secure feedback submission

## Troubleshooting

### Common Issues

**Feedback Not Saving**
- Check message_id is unique
- Verify feedback_type is valid
- Ensure context is provided

**No Improvements Showing**
- Minimum 5 samples needed for patterns
- Check confidence threshold (0.7)
- Verify similar contexts exist

**Incorrect Adaptations**
- Review recent feedback for conflicts
- Check if contradictory edits exist
- Reset specific pattern if needed

## Future Enhancements

### Planned Features
1. **Multi-user Learning**: Share patterns across users
2. **A/B Testing**: Test improvement effectiveness
3. **Sentiment Learning**: Adapt emotional tone
4. **Language Detection**: Multi-language support
5. **Voice Learning**: Audio response preferences

### Advanced Analytics
- Prediction accuracy metrics
- Learning curve visualization
- Pattern clustering analysis
- Automated insight generation

## Examples

### Scenario 1: Email Formality
User consistently edits casual greetings to formal ones:
- Original: "Hey there!"
- Edited: "Dear colleague,"
- Learning: System adapts to use formal greetings for emails

### Scenario 2: Response Length
User shortens verbose responses:
- Original: 150 words
- Edited: 50 words
- Learning: System generates more concise responses

### Scenario 3: Technical Terms
User simplifies technical jargon:
- Original: "Implement asynchronous callback"
- Edited: "Set up automatic response"
- Learning: System uses simpler language

## Integration Guide

### With Agents
```python
# In your agent
from services.learning_system import learning_system

# Get improvements
improvements = await learning_system.get_response_improvements(
    message="User message",
    initial_response="AI response",
    context={"platform": "slack"}
)

# Apply improvements
if improvements["improved_response"]:
    response = improvements["improved_response"]
```

### With Frontend
```javascript
// Submit feedback
await fetch('/api/learning/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message_id: messageId,
        feedback_type: 'approved',
        original_response: response
    })
});
```

## Monitoring

### Key Metrics
- Daily approval rate
- Average edit distance
- Pattern recognition accuracy
- User satisfaction trend
- Response improvement rate

### Dashboard Access
Visit `/api/learning/insights` for current metrics
Check `/api/learning/trends` for historical data

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Submit issues to the project repository

The learning system is designed to improve continuously. The more feedback provided, the better it becomes at generating appropriate responses!