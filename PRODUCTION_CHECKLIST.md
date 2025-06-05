# Production Deployment Checklist

## Pre-Deployment Requirements

### 1. Infrastructure Setup
- [ ] **Server Requirements**
  - [ ] Minimum 4 vCPUs, 8GB RAM for production
  - [ ] 100GB SSD storage with room for growth
  - [ ] Ubuntu 22.04 LTS or similar
  - [ ] Docker 24.0+ and Docker Compose 2.20+
  
- [ ] **Domain and SSL**
  - [ ] Register production domain
  - [ ] Configure DNS A records
  - [ ] Obtain SSL certificates (Let's Encrypt recommended)
  - [ ] Configure reverse proxy (nginx/traefik)

### 2. Security Configuration

- [ ] **Secrets Management**
  - [ ] Generate strong SECRET_KEY: `openssl rand -hex 32`
  - [ ] Generate secure database passwords
  - [ ] Generate Redis password
  - [ ] Store secrets in secure vault (HashiCorp Vault, AWS Secrets Manager)
  
- [ ] **API Keys**
  - [ ] Obtain production API keys for:
    - [ ] OpenAI (if using)
    - [ ] Anthropic (if using)
    - [ ] Sentry for error tracking
    - [ ] Email service provider
  
- [ ] **Network Security**
  - [ ] Configure firewall rules
    ```bash
    ufw allow 22/tcp    # SSH
    ufw allow 80/tcp    # HTTP
    ufw allow 443/tcp   # HTTPS
    ufw allow 3000/tcp  # API (restrict to internal)
    ufw allow 5432/tcp  # PostgreSQL (restrict to internal)
    ufw allow 6379/tcp  # Redis (restrict to internal)
    ```
  - [ ] Set up VPN for administrative access
  - [ ] Configure fail2ban for brute force protection

### 3. Database Preparation

- [ ] **PostgreSQL Setup**
  - [ ] Create production database
  - [ ] Create application user with limited privileges
  - [ ] Configure connection pooling
  - [ ] Set up replication (optional but recommended)
  
- [ ] **Migrations**
  ```bash
  docker-compose exec backend alembic upgrade head
  ```
  
- [ ] **Backup Strategy**
  - [ ] Configure automated daily backups
  - [ ] Test backup restoration process
  - [ ] Set up offsite backup storage

### 4. Application Configuration

- [ ] **Environment Variables**
  - [ ] Copy `.env.example` to `.env`
  - [ ] Update all production values
  - [ ] Verify no development/debug settings
  
- [ ] **Performance Tuning**
  - [ ] Configure Redis maxmemory policy
  - [ ] Set PostgreSQL shared_buffers and work_mem
  - [ ] Configure nginx worker processes
  - [ ] Set appropriate Docker resource limits

### 5. Monitoring Setup

- [ ] **Metrics and Alerting**
  - [ ] Configure Prometheus scraping
  - [ ] Import Grafana dashboards
  - [ ] Set up alerts for:
    - [ ] High CPU/Memory usage
    - [ ] Database connection issues
    - [ ] API response times > 1s
    - [ ] Error rate > 1%
    - [ ] Disk space < 20%
  
- [ ] **Logging**
  - [ ] Configure log rotation
  - [ ] Set up centralized logging (ELK/Loki)
  - [ ] Configure log retention policies

## Deployment Steps

### 1. Initial Deployment

```bash
# 1. Clone repository
git clone https://github.com/yourusername/board-of-directors-ai.git
cd board-of-directors-ai

# 2. Configure environment
cp .env.example .env
# Edit .env with production values

# 3. Build images
docker-compose -f docker-compose.prod.yml build

# 4. Start services
docker-compose -f docker-compose.prod.yml up -d

# 5. Run migrations
docker-compose exec backend alembic upgrade head

# 6. Create superuser
docker-compose exec backend python -m backend.cli create-superuser

# 7. Verify health
curl https://yourdomain.com/api/v1/health
```

### 2. Post-Deployment Verification

- [ ] **Functional Tests**
  - [ ] User registration and login
  - [ ] Task creation and execution
  - [ ] Director management
  - [ ] Privacy shield filtering
  - [ ] WebSocket connections
  
- [ ] **Performance Tests**
  - [ ] Load test with expected traffic
  - [ ] Verify response times < 500ms
  - [ ] Check database query performance
  - [ ] Monitor memory usage under load

### 3. Security Verification

- [ ] **Security Scan**
  ```bash
  # Run security scan
  docker run --rm -v $(pwd):/src \
    aquasec/trivy fs --security-checks vuln,config /src
  ```
  
- [ ] **SSL Configuration**
  ```bash
  # Test SSL configuration
  curl -I https://yourdomain.com
  nmap --script ssl-enum-ciphers -p 443 yourdomain.com
  ```

## Maintenance Tasks

### Daily
- [ ] Check system health dashboard
- [ ] Review error logs
- [ ] Monitor disk space
- [ ] Verify backup completion

### Weekly
- [ ] Review performance metrics
- [ ] Check for security updates
- [ ] Analyze user activity patterns
- [ ] Test backup restoration

### Monthly
- [ ] Update dependencies
- [ ] Review and rotate logs
- [ ] Performance optimization review
- [ ] Security audit

## Rollback Plan

### Immediate Rollback Steps
1. **Stop current deployment**
   ```bash
   docker-compose -f docker-compose.prod.yml down
   ```

2. **Restore database**
   ```bash
   pg_restore -h localhost -U postgres -d boardofdirectors backup_file.sql
   ```

3. **Deploy previous version**
   ```bash
   git checkout previous-tag
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Rollback Verification
- [ ] Verify all services are running
- [ ] Check database connectivity
- [ ] Test critical user flows
- [ ] Monitor error rates

## Emergency Contacts

- **DevOps Lead**: [Name] - [Phone] - [Email]
- **Database Admin**: [Name] - [Phone] - [Email]
- **Security Team**: [Name] - [Phone] - [Email]
- **On-Call Engineer**: [Name] - [Phone] - [Email]

## Sign-off

- [ ] Development Team Lead: _________________ Date: _______
- [ ] Security Officer: _________________ Date: _______
- [ ] Operations Manager: _________________ Date: _______
- [ ] Product Owner: _________________ Date: _______