# AgenticPersona + Music Service Proxy Integration Guide

## Overview

This integration enables the Music Service Proxy to leverage AgenticPersona's AI Board of Directors for intelligent music recommendations and decision-making.

## Database Schema

The integration introduces two new tables:

### 1. `board_consultations`
Stores consultation results from the AI Board of Directors.

**Columns:**
- `id` - UUID primary key
- `user_id` - References the user making the consultation
- `consultation_topic` - The topic/question for the board
- `consultation_context` - JSON context data
- `board_decision` - The board's decision
- `decision_reasoning` - Explanation of the decision
- `confidence_score` - Confidence level (0-1)
- `board_members_consulted` - JSON array of board members
- `consultation_timestamp` - When the consultation occurred
- `metadata` - Additional metadata

### 2. `agentic_preferences`
Stores learned user preferences with confidence tracking.

**Columns:**
- `id` - UUID primary key
- `user_id` - References the user
- `preference_key` - Preference identifier
- `preference_value` - JSON value
- `confidence_level` - Confidence in the preference (0-1)
- `last_updated` - Last update timestamp
- `created_at` - Creation timestamp

## Implementation Steps

### 1. Database Setup
```bash
# Run migration to create tables
cd /home/patrick/music-service-proxy
node migrate.js up
```

### 2. Backend Integration
- Add agentic routes to server.js
- Implement AgenticService
- Add verbose logging
- Test API endpoints

### 3. Frontend Components
- Create Vue components for board consultations
- Add Pinia store for state management
- Update dashboard with AgenticPersona widgets
- Test UI interactions

### 4. Testing
- Unit tests for AgenticService
- Integration tests for API endpoints
- E2E tests for UI flows

### 5. Monitoring
- Add consultation metrics
- Track preference changes
- Monitor API performance

## Success Criteria

- ✅ Dashboard shows real-time board consultations
- ✅ Preferences are stored and retrieved correctly
- ✅ Verbose logging provides clear activity trail
- ✅ Integration doesn't break existing functionality
- ✅ All API calls are authenticated and rate-limited
- ✅ Performance remains under 200ms for consultations

## API Endpoints

### Board Consultation
```
POST /api/agentic/consult
{
  "topic": "playlist_recommendation",
  "context": {
    "mood": "energetic",
    "genre": "electronic",
    "duration": 60
  }
}
```

### Get User Preferences
```
GET /api/agentic/preferences
```

### Update Preference
```
PUT /api/agentic/preferences/:key
{
  "value": {...},
  "confidence": 0.85
}
```

## Important Notes

⚠️ **Maintain backward compatibility** - The integration should enhance, not replace, current Music Service Proxy functionality.

⚠️ **Security** - All endpoints require JWT authentication and implement rate limiting.

⚠️ **Performance** - Use connection pooling and implement caching where appropriate.