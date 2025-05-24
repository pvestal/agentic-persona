# Contributing to Agentic Persona

First off, thank you for considering contributing to Agentic Persona! This project thrives on community involvement and continuously learns from every contribution.

## 🤖 How This Project Learns From You

Every contribution helps the AI agents evolve:
- Code patterns are analyzed and adopted
- Documentation styles are learned
- New capabilities are integrated
- Best practices are automatically documented

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/agentic-persona.git`
3. Run setup: `./scripts/setup-dev.sh`
4. Create a branch: `git checkout -b feature/your-feature-name`
5. Make your changes
6. Test thoroughly (tests run automatically on commit)
7. Commit with clear messages
8. Push and create a Pull Request

### Development Setup

```bash
# Automated setup (recommended)
./scripts/setup-dev.sh

# This installs:
# - All dependencies
# - Pre-commit hooks for code quality
# - Test runners
# - Development tools
```

### Pre-commit Hooks

We use automated checks to maintain code quality:
- **Python**: Black formatting, Flake8 linting, mypy type checking
- **JavaScript/Vue**: ESLint with Vue plugin
- **Security**: Automatic secret detection
- **Tests**: Quick tests run on every commit

```bash
# Run all checks manually
pre-commit run --all-files

# Skip hooks in emergency (not recommended)
git commit --no-verify
```

## 📝 Contribution Guidelines

### Code Style
- Follow existing patterns (the AI will learn from consistency)
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and small

### Commit Messages
Format: `type(scope): description`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

Example: `feat(agents): add financial analysis capability`

### Pull Request Process

1. **Update Documentation**: Including this file if needed!
2. **Add Tests**: For new features
3. **Update Evolution Log**: Document what the system learned
4. **Version Bump**: If significant change

### Agent Development

When creating or modifying agents:

```python
# agents/your_agent.py
class YourAgent(BaseAgent):
    """
    Agent purpose and capabilities
    
    Evolution Notes:
    - What this agent learns from
    - How it improves over time
    - Integration points
    """
    
    def __init__(self):
        super().__init__(
            role="Your Agent Role",
            goal="What the agent achieves",
            backstory="Agent's background and expertise",
            memory=True,
            self_reflection=True
        )
```

## 🔄 Continuous Improvement Process

Your contributions trigger an improvement cycle:

1. **Analysis**: The system analyzes your code
2. **Learning**: Patterns and improvements are identified
3. **Integration**: Changes are integrated into agent knowledge
4. **Documentation**: Docs are automatically updated
5. **Evolution**: The system evolves based on your contribution

## 🧪 Testing

- Write tests for new features
- Ensure existing tests pass
- Test voice interactions manually
- Document test scenarios for AI learning

```bash
# Backend tests
cd echo-backend
pytest                    # Run all tests
pytest --cov             # With coverage report
pytest -v -k "test_name" # Run specific test

# Frontend tests
cd echo-frontend
npm test                 # Watch mode
npm run test:coverage    # Coverage report
npm run test:ui         # Interactive UI

# Run all pre-commit checks
pre-commit run --all-files
```

See [TESTING.md](TESTING.md) for comprehensive testing guidelines.

## 🐛 Reporting Issues

When reporting issues, include:
- Description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- System information
- Any relevant logs

The AI will analyze issues to prevent similar problems in the future.

## 💡 Feature Requests

We love new ideas! When suggesting features:
- Explain the use case
- Describe how it fits with existing agents
- Consider how it could evolve over time
- Suggest how the AI could learn from it

## 📚 Documentation

- Update README.md for significant changes
- Document new agent capabilities
- Add examples for new features
- Update API documentation

## 🤝 Code of Conduct

- Be respectful and inclusive
- Help the AI learn positive patterns
- Share knowledge openly
- Support other contributors

## 🎯 Areas We Need Help

- [ ] More agent types
- [ ] Voice model improvements
- [ ] Memory optimization
- [ ] Multi-language support
- [ ] Mobile interface
- [ ] Testing coverage
- [ ] Documentation examples

## 📊 Recognition

Contributors are automatically recognized:
- In the evolution logs
- In agent memory
- In documentation credits
- In the contributor graph

## 🔮 The Future

This project aims to be self-maintaining. Your contributions help build an AI system that can:
- Review its own code
- Suggest improvements
- Generate documentation
- Evolve autonomously

Thank you for being part of this journey!

---

*This contributing guide updates itself based on successful contribution patterns.*