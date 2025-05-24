# LLM Integration Guide

## Overview
The Agentic Persona system now includes LLM (Large Language Model) integration for intelligent response generation. This enables agents to generate contextual, personalized responses to messages.

## Features

### 1. Response Generation
- Generate contextual responses based on message content
- Support for multiple LLM providers (OpenAI, Anthropic)
- Fallback to template responses when LLM is unavailable

### 2. Message Analysis
- Analyze message intent (question, request, information, etc.)
- Determine urgency levels
- Extract key entities and categories
- Sentiment analysis

### 3. Response Enhancement
- Adapt responses to user communication preferences
- Match tone and formality levels
- Adjust response length based on context

### 4. Summary Generation
- Create daily/weekly summaries of messages
- Extract key topics and action items
- Generate recommendations for follow-up

## Configuration

### 1. Set API Keys
Add your LLM API keys to `.env`:

```bash
# At least one is required
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

### 2. Provider Selection
The system automatically selects the available provider:
- If both are configured, Anthropic is preferred
- Falls back to OpenAI if Anthropic is unavailable
- Uses template responses if no LLM is configured

## Usage

### In Autonomous Responder
The `AutonomousResponder` agent automatically uses LLM for response generation:

```python
responder = AutonomousResponder(user_profile)
result = await responder.process_message(
    message="Can we schedule a meeting?",
    context=MessageContext(
        platform=MessagePlatform.EMAIL,
        sender="colleague@example.com"
    )
)
```

### Direct LLM Service Usage
```python
from services.llm_service import llm_service

# Generate a response
response = await llm_service.generate_response(
    message="What's the project status?",
    agent_persona="Professional assistant",
    temperature=0.7
)

# Analyze message intent
analysis = await llm_service.analyze_message_intent(
    "The server is down and customers are complaining!"
)

# Generate summary
summary = await llm_service.generate_summary(
    messages=message_list,
    summary_type="daily"
)
```

### API Endpoints

#### Test LLM Generation
```bash
curl -X POST http://localhost:8000/api/messages/test-llm \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Can we reschedule our meeting?",
    "platform": "email",
    "sender": "john@example.com"
  }'
```

#### Process Message with LLM
```bash
curl -X POST http://localhost:8000/api/messages/process \
  -H "Content-Type: application/json" \
  -d '{
    "content": "I need the Q4 report by Friday",
    "platform": "slack",
    "sender": "manager@company.com",
    "urgency": 0.8
  }'
```

## Testing

### Run Demo Script
```bash
cd echo-backend
python demo_llm.py
```

This will test:
- Basic response generation
- Message intent analysis
- Response enhancement with preferences
- Summary generation

### Unit Tests
```bash
pytest tests/test_services/test_llm_service.py -v
```

## Customization

### Response Personas
Customize agent personas in `autonomous_responder.py`:

```python
persona = f"""
You are {agent_name} responding on behalf of {user_name}.
Style: {communication_style}
Tone: {preferred_tone}
Special instructions: {custom_instructions}
"""
```

### Temperature Settings
Adjust creativity/consistency:
- `0.3` - Very consistent, formal
- `0.5` - Balanced
- `0.7` - More creative, casual
- `0.9` - Very creative, varied

### Token Limits
Configure response length:
- Brief: 150 tokens
- Concise: 300 tokens  
- Detailed: 500 tokens

## Best Practices

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables
   - Rotate keys regularly

2. **Error Handling**
   - Always have fallback responses
   - Log LLM errors for debugging
   - Monitor API usage and costs

3. **Response Quality**
   - Test with various message types
   - Collect user feedback
   - Continuously refine personas

4. **Performance**
   - Cache common responses
   - Use appropriate token limits
   - Consider rate limiting

## Troubleshooting

### No LLM Response
1. Check API keys in `.env`
2. Verify internet connection
3. Check API rate limits
4. Review error logs

### Poor Response Quality
1. Refine agent personas
2. Adjust temperature settings
3. Provide more context
4. Use message history

### High Latency
1. Reduce token limits
2. Use caching
3. Consider async processing
4. Monitor API performance

## Future Enhancements

1. **Local Model Support**
   - Integration with Ollama
   - Support for open-source models
   - On-device processing

2. **Advanced Features**
   - Multi-turn conversation handling
   - Context window management
   - Fine-tuning support
   - Custom model training

3. **Integration Expansion**
   - Support for more LLM providers
   - Specialized models for different tasks
   - Multi-modal capabilities (images, voice)

## Cost Considerations

### OpenAI Pricing (GPT-4 Turbo)
- Input: $0.01 / 1K tokens
- Output: $0.03 / 1K tokens

### Anthropic Pricing (Claude 3 Sonnet)
- Input: $0.003 / 1K tokens
- Output: $0.015 / 1K tokens

### Optimization Tips
1. Use shorter prompts when possible
2. Cache frequent responses
3. Implement user-based rate limiting
4. Monitor usage with logging