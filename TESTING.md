# Testing Guide

This guide covers testing practices for the ECHO (Evolving Cognitive Helper & Orchestrator) project.

## Quick Start

### Backend Testing (Python/FastAPI)

```bash
cd echo-backend
pip install -r requirements.txt
pytest
```

### Frontend Testing (Vue.js/Vitest)

```bash
cd echo-frontend
npm install
npm test
```

## Testing Structure

### Backend Tests
```
echo-backend/tests/
├── conftest.py          # Shared fixtures
├── test_agents/         # Agent unit tests
├── test_services/       # Service layer tests
└── test_api/           # API endpoint tests
```

### Frontend Tests
```
echo-frontend/src/
├── components/__tests__/  # Component unit tests
└── views/__tests__/      # View integration tests
```

## Running Tests

### Backend

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agents/test_base_agent.py

# Run tests matching pattern
pytest -k "test_autonomy"

# Run with verbose output
pytest -v
```

### Frontend

```bash
# Run tests in watch mode
npm test

# Run tests once
npm test -- --run

# Run with UI
npm run test:ui

# Generate coverage report
npm run test:coverage
```

## Writing Tests

### Backend Test Example

```python
import pytest
from agents.base_agent import BaseAgent

class TestBaseAgent:
    @pytest.fixture
    def agent(self):
        return BaseAgent(name="test_agent")
    
    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        result = await agent.execute("test task", {})
        assert result["success"] is True
```

### Frontend Test Example

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '../MyComponent.vue'

describe('MyComponent', () => {
  it('renders properly', () => {
    const wrapper = mount(MyComponent, {
      props: { msg: 'Hello' }
    })
    expect(wrapper.text()).toContain('Hello')
  })
})
```

## Test Coverage

We aim for:
- 80% code coverage for critical business logic
- 60% coverage for UI components
- 100% coverage for utility functions

Check coverage reports:
- Backend: `echo-backend/htmlcov/index.html`
- Frontend: `echo-frontend/coverage/index.html`

## CI/CD

Tests run automatically on:
- Every push to `main` or `develop`
- Every pull request

See `.github/workflows/test.yml` for CI configuration.

## Mocking and Fixtures

### Backend Fixtures (pytest)
- `db_session`: In-memory database session
- `client`: FastAPI test client
- `mock_agent_data`: Sample agent configuration

### Frontend Mocking
- Use `vi.mock()` for module mocking
- Use `@vue/test-utils` stubs for component mocking

## Best Practices

1. **Write tests first** (TDD) for new features
2. **Keep tests isolated** - no dependencies between tests
3. **Use descriptive test names** that explain what's being tested
4. **Mock external dependencies** (APIs, databases, etc.)
5. **Test edge cases** and error conditions
6. **Keep tests fast** - use in-memory databases and mocks

## Debugging Tests

### Backend
```bash
# Run with debugger
pytest --pdb

# Show print statements
pytest -s

# Stop on first failure
pytest -x
```

### Frontend
```bash
# Run specific test file
npm test src/components/__tests__/StatCard.test.js

# Debug in browser
npm run test:ui
```

## Audio Testing

ECHO includes comprehensive audio testing capabilities for voice input/output.

### Running Audio Tests

```bash
# Run audio unit tests
cd echo-backend
pytest tests/audio/ -v

# Run audio integration tests
pytest tests/audio/test_audio_integration.py -v

# Interactive audio demo (test mode)
python demo_audio.py --test

# Quick automated audio tests
python demo_audio.py --test --quick
```

### Audio Test Features

1. **Voice Command Recognition**
   - Test transcription accuracy
   - Command intent extraction
   - Multi-language support

2. **Text-to-Speech**
   - Speech synthesis quality
   - Language support
   - Voice parameters (speed, pitch)

3. **End-to-End Testing**
   - Voice input → Agent processing → Voice output
   - Wake word detection
   - Continuous listening mode

### Audio API Testing

```bash
# Test audio endpoints
curl -X POST http://localhost:8000/api/audio/transcribe \
  -F "audio_file=@test.wav" \
  -F "language=en" \
  -F "enable_test_mode=true" \
  -F "test_transcription=Hello world"

# Test text-to-speech
curl -X POST http://localhost:8000/api/audio/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from ECHO", "language": "en"}'
```

### Test Mode

Audio components support test mode for CI/CD environments without audio hardware:

```python
# Enable test mode in tests
audio_processor = AudioProcessor()
audio_processor.enable_test_mode("mock transcription")

# Test mode generates synthetic audio data
audio = audio_processor.record_audio()  # Returns test audio
result = audio_processor.transcribe_audio(audio)  # Returns mock transcription
```

## Contributing

When submitting PRs:
1. All tests must pass
2. New features need tests
3. Maintain or improve coverage
4. Update this guide if adding new test patterns
5. Test audio features in test mode if no hardware available