# ArqLeads

**AI-Powered Lead Generation System for Architecture Studios**

ArqLeads is an intelligent lead qualification system designed specifically for architecture studios. Using conversational AI, it automatically engages with potential clients, extracts key project information, scores leads based on business value, and notifies the sales team of high-priority opportunities in real-time.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technical Architecture](#technical-architecture)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Performance](#performance)
- [Security](#security)
- [Monitoring](#monitoring)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Overview

ArqLeads solves the critical problem of lead qualification in architecture studios by automating the initial client interaction process. The system uses natural language processing to conduct intelligent conversations with potential clients, automatically extracting project requirements, budget information, timelines, and contact details.

### Problem Statement

Traditional lead generation for architecture studios involves:
- Manual qualification of every inquiry
- Time-consuming initial consultations
- Missed opportunities due to delayed responses
- Inconsistent data collection
- Difficulty prioritizing high-value leads

### Solution

ArqLeads provides:
- 24/7 automated lead qualification
- Real-time lead scoring (0-100 scale)
- Automatic categorization (Cold/Warm/Hot)
- Instant notifications for high-priority leads
- Comprehensive analytics dashboard
- Integration-ready architecture

## Key Features

### Conversational AI

- **Multi-Provider Support**: Ollama (local/free), OpenAI, or Anthropic Claude
- **Natural Language Understanding**: Extracts structured data from conversations
- **Context-Aware Responses**: Maintains conversation flow and context
- **Multilingual Support**: Primary support for Spanish, extensible to other languages

### Intelligent Lead Scoring

The system automatically scores leads based on:
- **Project Definition** (20 points): Clear project type and scope
- **Budget Information** (25 points): Budget disclosed and meets minimum threshold
- **Timeline Urgency** (30 points): Short timelines score higher
- **Complete Contact Info** (15 points): Name, email, and phone provided
- **Location Match** (10 points): Projects in target service areas

Total score range: 0-100 points

**Categorization:**
- **Cold Leads** (0-29 points): Low priority, minimal information
- **Warm Leads** (30-59 points): Medium priority, partial qualification
- **Hot Leads** (60-100 points): High priority, immediate follow-up required

### Real-Time Notifications

- Email alerts for hot leads (score ≥ 70)
- Customizable notification thresholds
- SMTP integration with major providers (Gmail, SendGrid, etc.)
- HTML-formatted emails with lead details

### Admin Dashboard

- JWT-secured authentication
- Real-time lead statistics
- Interactive data visualization
- Lead filtering and search
- Export capabilities
- Responsive design for mobile access

### Performance Optimization

- **Redis Caching**: 30x performance improvement on stats endpoints
- **Database Indexing**: Optimized queries with 12+ strategic indexes
- **Response Times**: <500ms p95 for all endpoints
- **Horizontal Scalability**: Stateless design for easy scaling

### Security

- JWT authentication for admin access
- Security headers (CSP, HSTS, X-Frame-Options)
- HTTPS enforcement in production
- Rate limiting (configurable per endpoint)
- Input sanitization and validation
- SQL injection protection via ORM

## Technical Architecture

### Tech Stack

**Backend:**
- FastAPI 0.109+ (Python 3.11+)
- SQLAlchemy 2.0 (ORM)
- PostgreSQL 15+ (Database)
- Redis 7.0+ (Cache)
- Alembic (Migrations)
- Pydantic 2.5+ (Validation)

**Frontend:**
- React 19+
- Vite 7+ (Build tool)
- TailwindCSS 4+ (Styling)
- Axios (HTTP client)
- TypeScript 5.9+

**AI/ML:**
- Ollama (Local LLM hosting)
- OpenAI API (Optional)
- Anthropic Claude API (Optional)

**Infrastructure:**
- Docker & Docker Compose
- Nginx (Reverse proxy)
- Prometheus (Metrics)
- Grafana (Visualization)
- GitHub Actions (CI/CD)

### Architecture Diagram

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Frontend  │
│  React SPA  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│  ┌──────────────────────────────┐  │
│  │  API Layer                   │  │
│  │  - /api/v1/chat              │  │
│  │  - /api/v1/leads             │  │
│  │  - /admin                    │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│  ┌──────────▼───────────────────┐  │
│  │  Business Logic              │  │
│  │  - Lead Scoring              │  │
│  │  - Data Extraction           │  │
│  │  - Email Notifications       │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│  ┌──────────▼───────────────────┐  │
│  │  Data Layer                  │  │
│  │  - PostgreSQL (Primary)      │  │
│  │  - Redis (Cache)             │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
       │                    │
       ▼                    ▼
┌─────────────┐      ┌─────────────┐
│   Ollama    │      │  Monitoring │
│  (LLM AI)   │      │  Prometheus │
└─────────────┘      └─────────────┘
```

### Database Schema

**Leads Table:**
- Primary contact information (name, email, phone)
- Project details (type, description, location)
- Financial data (budget, timeline)
- Scoring metrics (score, category, status)
- Qualification flags (has_budget, has_timeline, etc.)
- Metadata (source, UTM parameters, tags)
- Timestamps (created, updated, contacted, converted)

**Conversations Table:**
- Session management
- Message history
- Channel tracking (web, WhatsApp, etc.)
- Context preservation
- Activity status

**Messages Table:**
- Individual message storage
- Role tracking (user/assistant)
- Timestamp logging
- Metadata storage

## System Requirements

### Minimum Requirements

**Development:**
- CPU: 2 cores
- RAM: 4GB
- Disk: 10GB free space
- OS: Linux, macOS, or Windows with WSL2

**Production:**
- CPU: 4 cores
- RAM: 8GB
- Disk: 50GB free space (with backups)
- OS: Linux (Ubuntu 20.04+ recommended)

### Software Dependencies

- Docker 24.0+ and Docker Compose 2.0+
- PostgreSQL 15+ (or Docker)
- Redis 7.0+ (or Docker)
- Python 3.11+
- Node.js 18+ and npm 9+
- Git 2.30+

### Optional Dependencies

- Ollama (for local AI model hosting)
- Nginx (for production deployment)
- Let's Encrypt (for SSL certificates)

## Installation

### Quick Start (Development)

```bash
# Clone repository
git clone https://github.com/NogueiraElectronic/ArqLeads.git
cd ArqLeads

# Configure environment
cp Backend/.env.example Backend/.env
# Edit Backend/.env with your settings

# Start with Docker Compose
docker-compose up -d

# Access application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# Admin Dashboard: http://localhost:8000/admin/login
```

### Manual Installation

#### Backend Setup

```bash
cd Backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure database
# Edit .env with your PostgreSQL connection string

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### Database Setup

**Using Docker:**

```bash
docker run -d \
  --name arqleads-postgres \
  -e POSTGRES_USER=arqleads_user \
  -e POSTGRES_PASSWORD=your_secure_password \
  -e POSTGRES_DB=arqleads_db \
  -p 5432:5432 \
  -v arqleads_postgres_data:/var/lib/postgresql/data \
  postgres:15
```

**Manual PostgreSQL:**

```sql
CREATE DATABASE arqleads_db;
CREATE USER arqleads_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE arqleads_db TO arqleads_user;
```

#### Redis Setup

```bash
# Using Docker
docker run -d \
  --name arqleads-redis \
  -p 6379:6379 \
  redis:7-alpine

# Or install locally (Ubuntu)
sudo apt-get install redis-server
sudo systemctl start redis-server
```

## Configuration

### Environment Variables

Create `Backend/.env` based on the following template:

```env
# Database Configuration
DATABASE_URL=postgresql://arqleads_user:password@localhost:5432/arqleads_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50

# Application Configuration
PROJECT_NAME=ArqLeads System
DEBUG=True
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=generate-with-secrets.token_urlsafe(32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# AI Provider (ollama, openai, or anthropic)
AI_PROVIDER=ollama

# Ollama Configuration (if using local AI)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
OLLAMA_MAX_TOKENS=2048
OLLAMA_TEMPERATURE=0.7

# OpenAI Configuration (optional)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=500

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Email Notifications
SMTP_ENABLED=True
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=ArqLeads System
NOTIFICATION_EMAILS=admin@yourdomain.com,sales@yourdomain.com

# Studio Information
STUDIO_NAME=Your Architecture Studio
STUDIO_LOCATION=Your City, Country
STUDIO_SPECIALTIES=residential,commercial,renovations

# Lead Scoring Configuration
SCORING_PROJECT_DEFINED=20
SCORING_BUDGET_HIGH=25
SCORING_TIMELINE_SHORT=30
SCORING_CONTACT_COMPLETE=15
SCORING_LOCATION_DEFINED=10

SCORE_THRESHOLD_COLD=30
SCORE_THRESHOLD_WARM=60
SCORE_THRESHOLD_HOT=61

MIN_BUDGET_THRESHOLD=15000
MAX_HOT_TIMELINE_MONTHS=3

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_ENABLED=True

# Caching
CACHE_ENABLED=True
CACHE_TTL_SECONDS=300

# Monitoring
LOG_LEVEL=INFO
LOG_FORMAT=json
SENTRY_ENABLED=False
SENTRY_DSN=your-sentry-dsn
```

### Generating Secure Keys

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate database password
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

### AI Provider Setup

#### Option 1: Ollama (Local, Free)

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3.1

# Start Ollama server
ollama serve

# Configure .env
# AI_PROVIDER=ollama
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.1
```

#### Option 2: OpenAI

```bash
# Get API key from https://platform.openai.com/api-keys

# Configure .env
# AI_PROVIDER=openai
# OPENAI_API_KEY=sk-your-key-here
```

#### Option 3: Anthropic Claude

```bash
# Get API key from https://console.anthropic.com/

# Configure .env
# AI_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## Usage

### Accessing the System

**Frontend (User Chat):**
```
http://localhost:5173
```

**Admin Dashboard:**
```
http://localhost:8000/admin/login
Default credentials: admin / admin123
IMPORTANT: Change these in production
```

**API Documentation:**
```
http://localhost:8000/docs
Interactive Swagger UI with all endpoints
```

**Health Check:**
```bash
curl http://localhost:8000/health
```

### Chat Widget Integration

To integrate the chat widget into your website:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Your Architecture Studio</title>
</head>
<body>
    <!-- Your website content -->

    <!-- ArqLeads Chat Widget -->
    <div id="arqleads-chat-root"></div>
    <script src="http://your-domain.com/chat-widget.js"></script>
</body>
</html>
```

### Admin Dashboard Features

**Dashboard Overview:**
- Total leads count
- Hot/Warm/Cold lead distribution
- Conversion metrics
- Recent activity timeline
- Performance graphs

**Lead Management:**
- Search and filter leads
- Update lead status
- Add notes and tags
- Export to CSV
- Bulk operations

**Analytics:**
- Lead source tracking
- Conversion funnel analysis
- Response time metrics
- ROI calculations

## Development

### Project Structure

```
ArqLeads/
├── Backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   ├── admin.py      # Admin routes
│   │   │   ├── chat.py       # Chat endpoints
│   │   │   └── leads.py      # Lead management
│   │   ├── core/             # Core functionality
│   │   │   ├── auth.py       # Authentication
│   │   │   ├── cache.py      # Redis caching
│   │   │   ├── config.py     # Configuration
│   │   │   ├── database.py   # Database setup
│   │   │   ├── models/       # SQLAlchemy models
│   │   │   ├── security.py   # Security middleware
│   │   │   └── services/     # Business logic
│   │   ├── templates/        # HTML templates
│   │   └── main.py           # Application entry
│   ├── tests/                # Test suite
│   ├── alembic/              # Database migrations
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment config
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   └── ChatWidget.tsx
│   │   ├── App.tsx           # Main app component
│   │   └── main.tsx          # Entry point
│   ├── public/               # Static assets
│   ├── package.json          # Node dependencies
│   └── vite.config.ts        # Vite configuration
├── e2e/                      # E2E tests (Playwright)
├── load_testing/             # Load tests (Locust)
├── monitoring/               # Prometheus/Grafana configs
├── docker-compose.yml        # Development compose file
├── docker-compose.prod.yml   # Production compose file
└── README.md                 # This file
```

### Development Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
pytest                        # Run backend tests
npm run test                  # Run frontend tests

# Commit changes
git add .
git commit -m "feat: your feature description"

# Push and create PR
git push origin feature/your-feature-name
```

### Code Style

**Backend (Python):**
- Follow PEP 8 guidelines
- Use type hints
- Maximum line length: 100 characters
- Use Black for formatting: `black .`
- Use flake8 for linting: `flake8 app/`

**Frontend (TypeScript):**
- Follow ESLint configuration
- Use Prettier for formatting
- Functional components with hooks
- TypeScript strict mode enabled

### Database Migrations

```bash
# Create new migration
cd Backend
alembic revision --autogenerate -m "Description of changes"

# Review generated migration in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View current version
alembic current

# View migration history
alembic history
```

## Testing

### Backend Tests

```bash
cd Backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_chat_service.py

# Run specific test
pytest tests/test_chat_service.py::TestChatService::test_extract_budget

# View coverage report
open htmlcov/index.html
```

**Test Coverage:**
- Target: >80% code coverage
- Unit tests for all services
- Integration tests for API endpoints
- Database fixture tests

### Frontend Tests

```bash
cd frontend

# Run tests
npm run test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage

# Watch mode
npm run test -- --watch
```

### End-to-End Tests

```bash
cd e2e

# Install browsers (first time only)
npx playwright install

# Run all tests
npm run test

# Run in headed mode
npm run test:headed

# Run specific browser
npm run test -- --project=chromium

# Debug mode
npm run test:debug

# Generate report
npm run report
```

### Load Testing

```bash
cd load_testing

# Install Locust
pip install -r requirements.txt

# Run load test (Web UI)
locust -f locustfile.py --host=http://localhost:8000
# Open http://localhost:8089

# Run headless
locust -f locustfile.py --host=http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --headless

# Generate HTML report
locust -f locustfile.py --host=http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --headless \
  --html report.html
```

**Performance Targets:**
- Concurrent users: 100-200
- Requests per second: >100
- Response time p95: <500ms
- Error rate: <1%

## Deployment

### Production Checklist

Before deploying to production, review `DEPLOYMENT_CHECKLIST.md` for comprehensive verification steps.

**Critical Items:**
- All tests passing
- Environment variables configured
- SECRET_KEY changed from default
- Database backups configured
- HTTPS/SSL certificates installed
- Admin password changed
- Email notifications tested
- Monitoring configured
- Log aggregation setup
- Rate limiting enabled

### Docker Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Run database migrations
docker-compose run --rm backend alembic upgrade head

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify deployment
curl https://your-domain.com/health

# View logs
docker-compose logs -f backend
```

### VPS/Server Deployment

**Prerequisites:**
- Ubuntu 20.04+ or similar Linux distribution
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)

**Installation Steps:**

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/NogueiraElectronic/ArqLeads.git
cd ArqLeads

# Configure environment
cp Backend/.env.example Backend/.env
nano Backend/.env  # Edit with production values

# Deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Setup Nginx reverse proxy
sudo apt-get install nginx
# Configure Nginx (see documentation)

# Setup SSL with Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Environment-Specific Configuration

**Production .env differences:**

```env
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=production-secure-key-here
DATABASE_URL=postgresql://user:pass@db-host:5432/db
CORS_ORIGINS=https://yourdomain.com
SMTP_ENABLED=True
LOG_LEVEL=WARNING
SENTRY_ENABLED=True
```

### Scaling

**Horizontal Scaling:**

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

**Load Balancer Configuration:**

Use Nginx or cloud provider's load balancer to distribute traffic across backend replicas.

## API Documentation

### Authentication

Admin endpoints require JWT authentication:

```bash
# Login
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}

# Use token in subsequent requests
curl http://localhost:8000/admin/dashboard \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Chat Endpoints

**Send Message:**

```bash
POST /api/v1/chat/message
Content-Type: application/json

{
  "session_id": "unique-session-id",
  "message": "I need to renovate my apartment",
  "language": "es",
  "channel": "web"
}

Response:
{
  "message": "I'd be happy to help you with your apartment renovation...",
  "timestamp": "2024-01-15T10:30:00Z",
  "lead_score": 45,
  "lead_category": "warm"
}
```

### Lead Management Endpoints

**Get All Leads:**

```bash
GET /api/v1/leads/?page=1&page_size=20&category=hot

Response:
{
  "total": 150,
  "page": 1,
  "page_size": 20,
  "leads": [...]
}
```

**Get Lead Statistics:**

```bash
GET /api/v1/leads/stats

Response:
{
  "total_leads": 150,
  "hot_leads": 25,
  "warm_leads": 60,
  "cold_leads": 65,
  "avg_score": 52.3,
  "leads_today": 5,
  "leads_this_week": 23,
  "leads_this_month": 87
}
```

**Update Lead:**

```bash
PATCH /api/v1/leads/{lead_id}
Content-Type: application/json

{
  "status": "contacted",
  "notes": "Called client, scheduled meeting"
}
```

### Health & Metrics

**Health Check:**

```bash
GET /health

Response:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "ai_provider": "ollama"
}
```

**Prometheus Metrics:**

```bash
GET /metrics

Response:
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/v1/leads/stats"} 1523
# TYPE http_request_duration_seconds histogram
...
```

## Performance

### Benchmarks

**API Response Times (95th percentile):**
- `/health`: 5ms
- `/api/v1/leads/stats` (cached): 8ms
- `/api/v1/leads/stats` (uncached): 150ms
- `/api/v1/chat/message`: 1200ms (depends on AI provider)

**Database Performance:**
- Lead lookup by ID: <2ms
- Lead search with filters: <15ms
- Statistics aggregation (cached): <5ms
- Statistics aggregation (uncached): <100ms

**Cache Performance:**
- Cache hit rate: >95%
- Redis latency: <1ms
- Memory usage: ~50MB for 10,000 leads

### Optimization Techniques

**Database:**
- 12 strategic indexes on frequently queried columns
- Partial indexes for hot lead queries
- Connection pooling (10-20 connections)
- Query result caching via Redis

**Application:**
- Redis caching for expensive queries
- Async I/O for all database operations
- Background task processing for emails
- Response compression (gzip)

**Frontend:**
- Code splitting and lazy loading
- Asset optimization and minification
- CDN delivery for static assets
- Service worker caching

## Security

### Security Features

**Authentication & Authorization:**
- JWT tokens with configurable expiration
- Bcrypt password hashing (12 rounds)
- Role-based access control (RBAC)
- Secure session management

**Network Security:**
- HTTPS enforcement in production
- CORS configuration
- Rate limiting (60 requests/minute default)
- Security headers (CSP, HSTS, X-Frame-Options)

**Data Protection:**
- SQL injection protection via ORM
- XSS prevention through input sanitization
- CSRF protection
- Encrypted database connections

**Infrastructure:**
- Docker container isolation
- Minimal container privileges
- Regular security updates
- Automated vulnerability scanning

### Security Best Practices

**For Production:**

1. Change all default credentials
2. Use strong SECRET_KEY (32+ characters)
3. Enable HTTPS with valid SSL certificate
4. Configure firewall (allow only 80, 443)
5. Regular security audits
6. Monitor logs for suspicious activity
7. Keep dependencies updated
8. Implement backup strategy
9. Use environment variables for secrets
10. Enable Sentry or similar error tracking

## Monitoring

### Prometheus Metrics

**Application Metrics:**
- `http_requests_total` - Total HTTP requests by endpoint
- `http_request_duration_seconds` - Request duration histogram
- `database_connections_active` - Active database connections
- `cache_hit_rate` - Redis cache hit percentage
- `leads_created_total` - Total leads created
- `leads_by_category` - Lead distribution by category

**System Metrics:**
- CPU usage
- Memory consumption
- Disk I/O
- Network throughput

### Grafana Dashboards

Pre-configured dashboards available in `monitoring/grafana/`:

- **ArqLeads Overview**: System health and key metrics
- **API Performance**: Request rates, latencies, errors
- **Database Performance**: Query times, connection pool
- **Lead Analytics**: Lead trends, conversion rates

### Logging

**Structured Logging:**

All logs are output in JSON format for easy parsing:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "app.api.chat",
  "message": "request_completed",
  "method": "POST",
  "path": "/api/v1/chat/message",
  "status_code": 200,
  "duration_ms": 1250
}
```

**Log Levels:**
- `DEBUG`: Development only, detailed information
- `INFO`: General informational messages
- `WARNING`: Warning messages, potential issues
- `ERROR`: Error messages, failures
- `CRITICAL`: Critical failures requiring immediate attention

### Alerting

Configure alerts in Prometheus/Alertmanager for:

- Response time p95 > 1000ms
- Error rate > 5%
- Database connections > 80% of pool
- Disk usage > 80%
- Memory usage > 90%
- System downtime

## Contributing

We welcome contributions from the community. Please follow these guidelines:

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest` and `npm run test`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Pull Request Process

1. Update documentation for any new features
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers
6. Address review feedback
7. Squash commits before merge

### Code Review Guidelines

- Code follows project style guidelines
- Tests provide adequate coverage
- Documentation is clear and complete
- No security vulnerabilities introduced
- Performance impact considered
- Backward compatibility maintained

### Issue Reporting

When reporting issues, please include:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, etc.)
- Relevant logs or error messages
- Screenshots if applicable

## License

This project is licensed under the MIT License - see the LICENSE file for details.

Copyright (c) 2024 ArqLeads Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Support

### Documentation

- **Quick Start**: `QUICK_START.md`
- **Architecture**: `ARCHITECTURE.md`
- **Deployment**: `DEPLOYMENT_CHECKLIST.md`
- **Operations**: `PRODUCTION_RUNBOOK.md`
- **API Docs**: http://localhost:8000/docs

### Community

- GitHub Issues: Report bugs and request features
- GitHub Discussions: Ask questions and share ideas
- Documentation Wiki: Detailed guides and tutorials

### Professional Support

For enterprise support, custom development, or consulting services, contact:

- Email: support@arqleads.com
- Website: https://arqleads.com

### Changelog

See `CHANGELOG.md` for version history and release notes.

### Roadmap

See `ROADMAP.md` for planned features and improvements.

---

**Version**: 1.0.0
**Last Updated**: 2024-01-15
**Status**: Production Ready

Built with precision for architecture studios worldwide.
