# Board of Directors AI System

A production-ready AI agent management system that implements a board of directors pattern for task delegation and execution. The system features multiple AI directors with different specialties, performance-based rotation, and comprehensive monitoring.

## Features

- **Multi-Agent Architecture**: Support for multiple AI providers (OpenAI, Anthropic, Ollama)
- **Performance-Based Leadership**: Automatic chairperson rotation based on performance metrics
- **Privacy Shield**: PII detection and filtering while allowing AI API access
- **Production Security**: JWT authentication, rate limiting, and comprehensive audit logging
- **Real-time Monitoring**: Prometheus metrics, Grafana dashboards, and health checks
- **Scalable Architecture**: Docker-based deployment with PostgreSQL and Redis

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Vue.js SPA    │────▶│  FastAPI Backend │────▶│   PostgreSQL    │
│   (Port 8000)   │     │   (Port 3000)   │     │   Database      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                          │
                               ▼                          ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │     Redis       │     │   AI Directors  │
                        │  Cache/Queue    │     │ (Multiple APIs) │
                        └─────────────────┘     └─────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/board-of-directors-ai.git
   cd board-of-directors-ai
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:8000
   - API Documentation: http://localhost:3000/api/v1/docs
   - Grafana: http://localhost:3001
   - Prometheus: http://localhost:9090

## Development Setup

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 3000
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

- `SECRET_KEY`: JWT signing key (generate with `openssl rand -hex 32`)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `ANTHROPIC_API_KEY`: Anthropic API key (optional)

### AI Directors Configuration

Directors can be configured through the API or admin interface:

```json
{
  "name": "GPT-4 Director",
  "role": "General Intelligence",
  "endpoint": "https://api.openai.com/v1/chat/completions",
  "specialties": ["analysis", "planning", "documentation"],
  "api_key": "your-api-key"
}
```

## API Documentation

### Authentication

```bash
# Register
curl -X POST http://localhost:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "email": "user@example.com", "password": "password"}'

# Login
curl -X POST http://localhost:3000/api/v1/auth/login \
  -F "username=user" \
  -F "password=password"
```

### Task Management

```bash
# Create task
curl -X POST http://localhost:3000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Analyze market data",
    "description": "Perform analysis of Q4 market trends",
    "priority": "high",
    "requirements": ["Include competitor analysis", "Focus on emerging markets"]
  }'

# Execute task
curl -X POST http://localhost:3000/api/v1/tasks/{task_id}/execute \
  -H "Authorization: Bearer $TOKEN"
```

## Testing

### Backend Tests

```bash
cd backend
pytest --cov=backend tests/
```

### Frontend Tests

```bash
cd frontend
npm run test
npm run test:coverage
```

### Integration Tests

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Deployment

### Production Deployment Checklist

- [ ] Generate strong SECRET_KEY
- [ ] Configure SSL/TLS certificates
- [ ] Set up database backups
- [ ] Configure monitoring alerts
- [ ] Review security settings
- [ ] Set up log aggregation
- [ ] Configure CDN for static assets
- [ ] Set up CI/CD pipeline

### Kubernetes Deployment

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/services/
kubectl apply -f k8s/ingress.yaml
```

## Monitoring

### Health Checks

- Backend: `GET /api/v1/health`
- Frontend: `GET /health`
- Database: PostgreSQL health check via pg_isready
- Redis: Redis PING command

### Metrics

Prometheus metrics available at `/metrics`:

- Request duration histogram
- Request count by status
- Active connections
- Task execution metrics
- Director performance metrics

### Logging

Structured JSON logging with the following fields:

- timestamp
- level
- message
- request_id
- user_id
- duration
- error (if applicable)

## Security

### Privacy Shield

The Privacy Shield component:
- Detects and filters PII in requests/responses
- Allows all AI API endpoints
- Logs filtering operations for audit
- Configurable detection confidence

### Rate Limiting

Default limits:
- 60 requests/minute
- 1000 requests/hour
- 10000 requests/day

### Authentication

- JWT-based authentication
- Refresh token rotation
- Password strength validation
- Account lockout after failed attempts

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Documentation: https://docs.boardofdirectors.ai
- Issues: https://github.com/yourusername/board-of-directors-ai/issues
- Email: support@boardofdirectors.ai