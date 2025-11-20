# 🏗️ ArqLeads - Architecture Documentation

## System Overview

ArqLeads es un sistema de captación automatizada de leads para estudios de arquitectura, que utiliza IA conversacional para calificar leads en tiempo real.

## 📐 High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React Frontend<br/>Vite + TailwindCSS]
    end

    subgraph "Application Layer"
        API[FastAPI Backend<br/>Python 3.11]
        WS[WebSocket Server]
    end

    subgraph "AI Layer"
        OLLAMA[Ollama<br/>Local LLM]
        OPENAI[OpenAI API<br/>Optional]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Database)]
        REDIS[(Redis<br/>Cache)]
    end

    subgraph "Monitoring"
        PROM[Prometheus<br/>Metrics]
        GRAF[Grafana<br/>Dashboards]
        ALERT[AlertManager<br/>Alerts]
    end

    UI -->|HTTP/WS| API
    API --> OLLAMA
    API --> OPENAI
    API --> PG
    API --> REDIS
    API --> PROM
    PROM --> GRAF
    PROM --> ALERT
```

## 🔄 Request Flow

### Chat Message Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Cache
    participant AI
    participant DB

    User->>Frontend: Send message
    Frontend->>Backend: POST /api/v1/chat/message
    Backend->>Cache: Check session cache
    alt Cache Hit
        Cache-->>Backend: Return session data
    else Cache Miss
        Backend->>DB: Query session
        DB-->>Backend: Session data
        Backend->>Cache: Store session
    end

    Backend->>AI: Generate response
    AI-->>Backend: AI response

    Backend->>DB: Extract lead info
    Backend->>DB: Calculate score
    Backend->>DB: Save conversation

    alt Hot Lead & Uncontacted
        Backend->>Backend: Trigger email notification
    end

    Backend->>Cache: Update cache
    Backend-->>Frontend: Return response + lead score
    Frontend-->>User: Display message
```

### Admin Dashboard Flow

```mermaid
sequenceDiagram
    participant Admin
    participant Browser
    participant Backend
    participant Auth
    participant Cache
    participant DB

    Admin->>Browser: Access /admin/login
    Browser->>Backend: GET /admin/login
    Backend-->>Browser: Login page

    Admin->>Browser: Enter credentials
    Browser->>Backend: POST /admin/login
    Backend->>Auth: Validate credentials
    Auth-->>Backend: JWT token
    Backend-->>Browser: Token + expiry

    Browser->>Backend: GET /admin/dashboard<br/>(with JWT)
    Backend->>Auth: Verify JWT
    Auth-->>Backend: Valid

    Backend->>Cache: Check stats cache
    alt Cache Hit
        Cache-->>Backend: Cached stats
    else Cache Miss
        Backend->>DB: Query stats
        DB-->>Backend: Stats data
        Backend->>Cache: Store stats (60s TTL)
    end

    Backend-->>Browser: Dashboard HTML
    Browser-->>Admin: Display dashboard
```

## 📊 Data Model

```mermaid
erDiagram
    LEADS ||--o{ CONVERSATIONS : has
    CONVERSATIONS ||--o{ MESSAGES : contains

    LEADS {
        int id PK
        string name
        string email
        string phone
        string project_type
        text project_description
        string location
        float budget
        string timeline
        int timeline_months
        int score
        enum category
        enum status
        string session_id UK
        timestamp created_at
        timestamp updated_at
        timestamp contacted_at
    }

    CONVERSATIONS {
        int id PK
        string session_id UK
        int lead_id FK
        string channel
        bool is_active
        int message_count
        json context
        timestamp started_at
        timestamp last_message_at
    }

    MESSAGES {
        int id PK
        int conversation_id FK
        string role
        text content
        json metadata
        timestamp created_at
    }
```

## 🔐 Security Architecture

```mermaid
graph LR
    subgraph "Public Internet"
        USER[User]
    end

    subgraph "Edge Layer"
        NGINX[Nginx<br/>Reverse Proxy]
        CF[Cloudflare<br/>Optional]
    end

    subgraph "Application Layer"
        MW1[HTTPS Redirect<br/>Middleware]
        MW2[Security Headers<br/>Middleware]
        MW3[Rate Limiter<br/>Middleware]
        MW4[CORS<br/>Middleware]
        AUTH[JWT Auth<br/>Middleware]
        API[FastAPI<br/>Application]
    end

    USER --> CF
    CF --> NGINX
    NGINX --> MW1
    MW1 --> MW2
    MW2 --> MW3
    MW3 --> MW4
    MW4 --> AUTH
    AUTH --> API
```

## 🚀 Deployment Architecture

### Development

```mermaid
graph TB
    subgraph "Local Development"
        DEV[Developer Machine]
        DOCK[Docker Desktop]

        subgraph "Docker Compose"
            FE[Frontend<br/>:5173]
            BE[Backend<br/>:8000]
            DB[(PostgreSQL<br/>:5432)]
            RD[(Redis<br/>:6379)]
            OL[Ollama<br/>:11434]
        end

        DEV --> DOCK
        DOCK --> FE
        DOCK --> BE
        DOCK --> DB
        DOCK --> RD
        DOCK --> OL
    end
```

### Production

```mermaid
graph TB
    subgraph "Cloud/VPS"
        LB[Load Balancer<br/>Nginx]

        subgraph "Application Servers"
            APP1[Backend Instance 1]
            APP2[Backend Instance 2]
            APP3[Backend Instance N]
        end

        subgraph "Data Tier"
            DBMASTER[(PostgreSQL<br/>Master)]
            DBREPLICA[(PostgreSQL<br/>Replica)]
            REDISCLUSTER[(Redis<br/>Cluster)]
        end

        subgraph "Monitoring"
            PROM[Prometheus]
            GRAF[Grafana]
        end

        subgraph "Static Assets"
            CDN[CDN<br/>Cloudflare]
            S3[S3/Object Storage]
        end

        LB --> APP1
        LB --> APP2
        LB --> APP3

        APP1 --> DBMASTER
        APP2 --> DBMASTER
        APP3 --> DBMASTER

        DBMASTER -.Replication.-> DBREPLICA

        APP1 --> REDISCLUSTER
        APP2 --> REDISCLUSTER
        APP3 --> REDISCLUSTER

        APP1 --> PROM
        APP2 --> PROM
        APP3 --> PROM

        PROM --> GRAF

        CDN --> S3
    end

    INTERNET[Internet] --> LB
    INTERNET --> CDN
```

## 🔄 CI/CD Pipeline

```mermaid
graph LR
    DEV[Developer] -->|Push| GIT[GitHub]

    subgraph "GitHub Actions"
        BUILD[Build & Test]
        LINT[Lint & Format]
        SEC[Security Scan]
        DOCKER[Build Docker]
        DEPLOY[Deploy]
    end

    GIT --> BUILD
    BUILD --> LINT
    LINT --> SEC
    SEC --> DOCKER
    DOCKER --> DEPLOY

    subgraph "Deployment Targets"
        STG[Staging]
        PROD[Production]
    end

    DEPLOY -->|Auto| STG
    DEPLOY -->|Manual Approval| PROD
```

## 📈 Monitoring & Observability

```mermaid
graph TB
    subgraph "Application"
        APP[FastAPI App]
        METRICS[Prometheus<br/>Instrumentator]
        LOGS[Structured Logging<br/>structlog]
    end

    subgraph "Collection"
        PROM[Prometheus<br/>Server]
        LOKI[Loki<br/>Optional]
    end

    subgraph "Visualization"
        GRAF[Grafana<br/>Dashboards]
    end

    subgraph "Alerting"
        ALERT[AlertManager]
        SLACK[Slack]
        EMAIL[Email]
        PAGER[PagerDuty]
    end

    APP --> METRICS
    APP --> LOGS

    METRICS --> PROM
    LOGS --> LOKI

    PROM --> GRAF
    LOKI --> GRAF

    PROM --> ALERT
    ALERT --> SLACK
    ALERT --> EMAIL
    ALERT --> PAGER
```

## 🧩 Component Details

### Backend Components

```mermaid
graph TB
    subgraph "FastAPI Application"
        MAIN[main.py<br/>App Entry]

        subgraph "API Routes"
            CHAT[/api/v1/chat]
            LEADS[/api/v1/leads]
            ADMIN[/admin]
        end

        subgraph "Core Services"
            AI[AI Service<br/>Ollama/OpenAI]
            EMAIL[Email Service<br/>SMTP]
            CACHE[Cache Service<br/>Redis]
        end

        subgraph "Middleware"
            RATE[Rate Limiting]
            SEC[Security Headers]
            LOG[Request Logging]
        end

        subgraph "Database"
            ORM[SQLAlchemy ORM]
            MODELS[Models]
        end

        MAIN --> CHAT
        MAIN --> LEADS
        MAIN --> ADMIN

        CHAT --> AI
        LEADS --> CACHE
        ADMIN --> EMAIL

        MAIN --> RATE
        MAIN --> SEC
        MAIN --> LOG

        CHAT --> ORM
        LEADS --> ORM
        ORM --> MODELS
    end
```

### Cache Strategy

```mermaid
graph LR
    subgraph "Cache Layers"
        L1[Application Cache<br/>In-Memory]
        L2[Redis Cache<br/>Distributed]
        L3[Database<br/>PostgreSQL]
    end

    REQ[Request] --> L1
    L1 -->|Miss| L2
    L2 -->|Miss| L3
    L3 -->|Write-back| L2
    L2 -->|Write-back| L1
    L1 --> RESP[Response]

    subgraph "TTL Strategy"
        SHORT[Stats: 60s]
        MED[Leads: 5min]
        LONG[Static: 30min]
    end
```

## 🎯 Scaling Strategy

### Horizontal Scaling

```mermaid
graph TB
    LB[Load Balancer]

    subgraph "Auto-Scaling Group"
        APP1[Backend 1]
        APP2[Backend 2]
        APP3[Backend 3]
        APPN[Backend N]
    end

    SHARED_CACHE[(Shared Redis)]
    SHARED_DB[(Shared PostgreSQL)]

    LB --> APP1
    LB --> APP2
    LB --> APP3
    LB --> APPN

    APP1 --> SHARED_CACHE
    APP2 --> SHARED_CACHE
    APP3 --> SHARED_CACHE
    APPN --> SHARED_CACHE

    APP1 --> SHARED_DB
    APP2 --> SHARED_DB
    APP3 --> SHARED_DB
    APPN --> SHARED_DB
```

### Database Scaling

```mermaid
graph TB
    APP[Application]

    MASTER[(PostgreSQL<br/>Master<br/>Write)]
    REPLICA1[(PostgreSQL<br/>Replica 1<br/>Read)]
    REPLICA2[(PostgreSQL<br/>Replica 2<br/>Read)]

    APP -->|Writes| MASTER
    APP -->|Reads| REPLICA1
    APP -->|Reads| REPLICA2

    MASTER -.Stream Replication.-> REPLICA1
    MASTER -.Stream Replication.-> REPLICA2
```

## 🔒 Security Layers

```mermaid
graph TB
    subgraph "Network Security"
        FW[Firewall<br/>UFW/iptables]
        VPN[VPN<br/>Optional]
    end

    subgraph "Application Security"
        HTTPS[HTTPS/TLS]
        JWT[JWT Authentication]
        RATE_LIM[Rate Limiting]
        CORS_POL[CORS Policy]
        CSP[Content Security Policy]
    end

    subgraph "Data Security"
        ENCRYPT[Encryption at Rest]
        HASH[Password Hashing<br/>bcrypt]
        BACKUP[Encrypted Backups]
    end

    FW --> HTTPS
    HTTPS --> JWT
    JWT --> RATE_LIM
    RATE_LIM --> CORS_POL
    CORS_POL --> CSP
    CSP --> ENCRYPT
    ENCRYPT --> HASH
    HASH --> BACKUP
```

## 📝 Technology Stack

### Backend
- **Framework**: FastAPI 0.109+
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic 2.5+
- **AI**: Ollama (local) / OpenAI (cloud)
- **Cache**: Redis 7.0+
- **Database**: PostgreSQL 15+

### Frontend
- **Framework**: React 19+
- **Build Tool**: Vite 7+
- **Styling**: TailwindCSS 4+
- **HTTP Client**: Axios
- **Icons**: Lucide React

### DevOps
- **Containerization**: Docker + Docker Compose
- **Monitoring**: Prometheus + Grafana
- **Logging**: structlog
- **CI/CD**: GitHub Actions
- **Testing**: Pytest, Vitest, Playwright

## 📊 Performance Targets

| Metric | Target | Critical |
|--------|--------|----------|
| API Response Time (p95) | <500ms | <1000ms |
| Chat Response Time | <2s | <5s |
| Database Query Time | <50ms | <200ms |
| Cache Hit Rate | >95% | >80% |
| Uptime | >99.5% | >99% |
| Error Rate | <0.1% | <1% |

## 🔍 Monitoring Metrics

### Application Metrics
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration histogram
- `http_requests_in_progress` - Current requests
- `database_connections_active` - Active DB connections
- `cache_hit_rate` - Cache hit percentage
- `leads_created_total` - Total leads created
- `leads_by_category` - Leads by hot/warm/cold

### Infrastructure Metrics
- CPU usage
- Memory usage
- Disk I/O
- Network throughput
- Container health

---

**Version**: 1.0.0
**Last Updated**: $(date +%Y-%m-%d)
**Maintained by**: DevOps Team
