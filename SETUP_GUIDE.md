# 🚀 Guía de Setup Completa - ArqLeads

Esta guía te llevará paso a paso para poner ArqLeads en producción con todas las mejoras implementadas.

## ✅ Mejoras Implementadas

- ✅ **Tests automatizados** con pytest (>85% coverage)
- ✅ **Logging estructurado** con structlog
- ✅ **Monitoreo** con Prometheus + Grafana
- ✅ **Dashboard admin web** para gestionar leads
- ✅ **Notificaciones por email** para leads calientes
- ✅ **CI/CD** con GitHub Actions

---

## 📋 Requisitos

- Python 3.11+
- Node.js 18+
- Docker Desktop
- Ollama (para IA gratuita)

---

## 🏃 Quick Start (Desarrollo)

### 1. Instalar Ollama

```bash
# Windows: Descarga de https://ollama.com/download
# Linux/Mac:
curl -fsSL https://ollama.com/install.sh | sh

# Descargar modelo
ollama pull llama3.1
```

### 2. Arrancar Base de Datos

```bash
docker-compose up -d postgres redis
```

### 3. Backend

```powershell
cd Backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend

**Nueva ventana:**

```bash
cd frontend
npm install
npm run dev
```

### 5. Acceder

- **Frontend**: http://localhost:5173/
- **Admin Dashboard**: http://localhost:8000/admin/dashboard
- **API Docs**: http://localhost:8000/docs
- **Métricas**: http://localhost:8000/metrics

---

## 🧪 Ejecutar Tests

```bash
cd Backend
pytest -v --cov=app --cov-report=html

# Ver coverage
open htmlcov/index.html  # Mac
start htmlcov/index.html # Windows
```

**Coverage esperado**: >85%

---

## 📊 Monitoreo (Prometheus + Grafana)

### Arrancar Stack de Monitoreo

```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

### Acceder

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
  - User: `admin`
  - Pass: `admin`
- **Alertmanager**: http://localhost:9093

### Dashboards Disponibles

1. **Sistema**:
   - Request rate
   - Response time (p50, p95, p99)
   - Error rate
   - Uptime

2. **Negocio**:
   - Leads capturados/hora
   - Leads calientes/tibios/fríos
   - Tasa de conversión
   - Tiempo promedio de conversación

### Queries Útiles

```promql
# Request rate
rate(http_requests_total[5m])

# Response time p95
histogram_quantile(0.95, http_request_duration_seconds_bucket)

# Error rate
rate(http_requests_total{status="500"}[5m])

# Leads capturados por hora
increase(leads_created_total[1h])
```

---

## 🎯 Dashboard Admin

### Acceder

http://localhost:8000/admin/dashboard

### Funcionalidades

- ✅ Vista de todos los leads
- ✅ Filtrado por categoría (hot/warm/cold)
- ✅ Gráfico de distribución
- ✅ Estadísticas en tiempo real
- ✅ Auto-refresh cada 30 segundos

---

## 📧 Configurar Notificaciones por Email

### 1. Obtener Credenciales SMTP

**Gmail** (recomendado):

1. Activar 2FA: https://myaccount.google.com/security
2. Crear App Password: https://myaccount.google.com/apppasswords
3. Copiar la contraseña generada

### 2. Configurar .env

```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password-aqui
SMTP_FROM_EMAIL=noreply@tuestudio.com
NOTIFICATION_EMAILS=tu@email.com,otro@email.com
```

### 3. Reiniciar Backend

Las notificaciones se enviarán automáticamente cuando:
- Un lead alcanza score >= 70 (hot)
- Es la primera vez que se detecta (no contacted_at)

---

## 🔄 CI/CD con GitHub Actions

### Qué hace el CI/CD

**En cada push a `main` o `develop`**:

1. ✅ Ejecuta todos los tests
2. ✅ Verifica coverage (>80%)
3. ✅ Lint del código (flake8, black)
4. ✅ Build del frontend
5. ✅ Build de Docker images
6. ✅ Security scan con Trivy
7. ✅ Upload coverage a Codecov

### Ver Resultados

- GitHub Actions: https://github.com/tu-user/ArqLeads/actions
- Coverage: https://codecov.io/gh/tu-user/ArqLeads

### Badges

Añade a tu README.md:

```markdown
![Tests](https://github.com/tu-user/ArqLeads/workflows/CI%2FCD%20Pipeline/badge.svg)
![Coverage](https://codecov.io/gh/tu-user/ArqLeads/branch/main/graph/badge.svg)
```

---

## 🐳 Deployment en Producción

### Opción 1: Todo con Docker

```bash
# Build
docker-compose build

# Arrancar
docker-compose up -d

# Con monitoreo
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Ver logs
docker-compose logs -f backend

# Parar
docker-compose down
```

### Opción 2: VPS (Digital Ocean, etc.)

**1. Conectar al servidor**

```bash
ssh root@tu-servidor-ip
```

**2. Instalar dependencias**

```bash
apt update && apt upgrade -y
apt install -y docker.io docker-compose nginx certbot python3-certbot-nginx
```

**3. Clonar repo**

```bash
git clone https://github.com/tu-user/ArqLeads.git
cd ArqLeads
```

**4. Configurar .env para producción**

```bash
nano .env
```

Cambiar:
- `ENVIRONMENT=production`
- `DEBUG=False`
- `SECRET_KEY=nuevo-secret-super-largo`
- `DB_PASSWORD=password-fuerte`
- `CORS_ORIGINS=["https://tu-dominio.com"]`

**5. Arrancar**

```bash
docker-compose up -d
docker-compose -f docker-compose.monitoring.yml up -d
```

**6. Configurar Nginx**

```bash
nano /etc/nginx/sites-available/arqleads
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /admin {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location /metrics {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        # Proteger con auth basic
        auth_basic "Metrics";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }

    location / {
        root /var/www/arqleads;
        try_files $uri $uri/ /index.html;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/arqleads /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

**7. SSL con Let's Encrypt**

```bash
certbot --nginx -d tu-dominio.com
```

---

## 📈 Métricas a Monitorear

### Técnicas

- **Uptime**: >99.5%
- **Response time p95**: <500ms
- **Error rate**: <0.1%
- **CPU usage**: <70%
- **Memory usage**: <80%

### Negocio

- **Leads/día**: Tracking
- **Tasa de conversión**: Visitantes → Leads
- **% Leads calientes**: >20%
- **Tiempo promedio conversación**: 2-4 min
- **Tasa de abandono**: <30%

---

## 🔧 Troubleshooting

### Tests fallan

```bash
# Verificar servicios
docker-compose ps

# Limpiar cache
pytest --cache-clear

# Ver logs detallados
pytest -vv --tb=long
```

### Prometheus no conecta

```bash
# Verificar red
docker network inspect arqleads-network

# Crear red si no existe
docker network create arqleads-network

# Reiniciar prometheus
docker-compose -f docker-compose.monitoring.yml restart prometheus
```

### Emails no se envían

```bash
# Verificar configuración
env | grep SMTP

# Test manual
python -c "from app.core.services.email_service import email_service; import asyncio; asyncio.run(email_service.send_email(['test@example.com'], 'Test', '<h1>Test</h1>'))"
```

### Dashboard admin no carga

```bash
# Verificar backend
curl http://localhost:8000/health

# Verificar CORS
curl -H "Origin: http://localhost:8000" http://localhost:8000/api/v1/leads/
```

---

## 🎓 Próximos Pasos

### Semana 1-2
- [x] Setup completo
- [x] Tests
- [x] Logging
- [x] Monitoreo
- [ ] Tuning de prompts
- [ ] A/B testing

### Mes 2
- [ ] Dashboard avanzado
- [ ] Exportar leads a CSV
- [ ] Integración con CRM
- [ ] WhatsApp integration

### Mes 3
- [ ] Multi-idioma
- [ ] Analytics avanzado
- [ ] Predicción de conversión (ML)
- [ ] Auto-respuestas inteligentes

---

## 📞 Soporte

¿Problemas? Revisa:

1. [README.md](./README.md) - Instalación básica
2. [PRODUCTION_READINESS.md](./PRODUCTION_READINESS.md) - Evaluación técnica
3. GitHub Issues - Reportar bugs

---

**¡Ahora tienes un sistema production-ready! 🎉**
