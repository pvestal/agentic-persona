# Architecture Decisions

## Agent Framework: CrewAI

### Decision
Use **CrewAI** as the primary agent framework.

### Rationale
- **Performance**: 5.76x faster than alternatives
- **Architecture**: Role-based agents align perfectly with our 5 personas
- **Memory**: Built-in short-term, long-term, entity, and contextual memory
- **Simplicity**: Minimal dependencies, easy to integrate
- **Community**: 100k+ developers, active support
- **License**: MIT (fully open source)

### Implementation Example
```python
from crewai import Agent, Task, Crew

# Documentation Automator Agent
doc_agent = Agent(
    role='Documentation Automator',
    goal='Convert conversations and code into organized documentation',
    backstory='Expert technical writer with deep understanding of code',
    memory=True,
    tools=[markdown_generator, file_manager, template_engine]
)
```

## Backend Options for Codespace

### Option 1: FastAPI + SQLite (Recommended for Development)
**Pros:**
- Runs entirely in Codespace
- No external dependencies
- Fast development cycle
- Easy to migrate data later

**Cons:**
- Single instance only
- No real-time sync between instances

**Use when:** Developing/testing or personal use only

### Option 2: Firebase (Recommended for Multi-Instance)
**Pros:**
- Real-time sync across instances
- Built-in auth
- Scales automatically
- Free tier generous

**Cons:**
- Vendor lock-in
- Requires internet connection
- Google dependency

**Use when:** Multiple users/devices need access

### Option 3: Self-Hosted with Network Storage
**Pros:**
- Full control
- Can use PostgreSQL/MySQL
- Network file share for assets
- No vendor lock-in

**Cons:**
- Requires infrastructure setup
- More complex deployment
- Manual scaling

**Use when:** Enterprise deployment or privacy requirements

## Recommended Architecture

### For Codespace Development
```
persona-prototype/          # Vue frontend
persona-backend/           
├── main.py               # FastAPI app
├── agents/               # CrewAI agents
│   ├── base.py          # Base agent class
│   ├── documentation.py 
│   ├── code_review.py
│   └── ...
├── database/
│   └── sqlite.db        # Local development DB
├── api/                 # REST endpoints
└── services/            # Business logic
```

### For Production (Firebase)
```
Frontend → Firebase Hosting
Backend → Cloud Functions
Database → Firestore
Auth → Firebase Auth
Storage → Cloud Storage
Queue → Firebase Functions + Pub/Sub
```

### Hybrid Approach (Recommended)
1. Develop locally with SQLite
2. Use environment variables for configuration
3. Abstract database layer
4. Deploy to Firebase for production
5. Keep option to self-host

## Next Steps
1. Set up CrewAI in backend
2. Create FastAPI structure
3. Implement first agent (Documentation Automator)
4. Add Firebase config for production deployment