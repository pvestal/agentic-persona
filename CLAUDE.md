# Development Notes for Claude

## Project Context
This is an agentic persona system designed to automate personal/professional tasks through specialized AI agents.

## Key Information

### Current State
- Frontend UI exists but no backend logic
- Vue 3 + Vite setup is working
- No actual agent functionality implemented yet

### Development Commands
```bash
# Frontend
cd persona-prototype
npm run dev        # Development server
npm run build      # Production build
npm run preview    # Preview build

# Linting (when implemented)
# npm run lint
# npm run typecheck
```

### Code Conventions
- Vue 3 Composition API
- TypeScript preferred (not yet implemented)
- Component-based architecture
- Minimal comments unless complex logic

### Priority Focus
1. Documentation Automator agent first
2. Backend infrastructure setup
3. LLM integration service
4. Task delegation framework

### Important Paths
- Frontend: `/workspaces/agentic-persona/persona-prototype/`
- Docs: `/workspaces/agentic-persona/docs/` (archived planning)
- Main docs: `PROJECT.md`, `TODOS.md`, `CLAUDE.md`

### Architecture Decisions
- Modular agent system
- Event-driven communication
- API-first design
- Conversation memory persistence

### Next Session Checklist
1. Read `TODOS.md` for current tasks
2. Check `PROJECT.md` for architecture
3. Update progress in both files
4. Focus on highest priority incomplete tasks

### Common Tasks
- Adding new agent: Create in `persona-backend/agents/`
- Updating UI: Work in `persona-prototype/src/`
- API changes: Update both frontend and backend
- Documentation: Update `PROJECT.md` with changes

## Session Memory
*This section should be updated each conversation with key decisions and progress*

### 2025-01-23
- Reorganized project structure
- Created unified documentation system
- Established TODO tracking
- Identified core implementation needs