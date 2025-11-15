# 🚨 Production Runbook - ArqLeads

## Información de Contacto de Emergencia

- **On-Call Engineer**: [Tu número]
- **Backup Engineer**: [Backup número]
- **Slack Channel**: #arqleads-incidents
- **PagerDuty**: arqleads.pagerduty.com

---

## 🔥 Incidentes Críticos (P0)

### Sistema Completamente Caído

**Síntomas**:
- `/health` devuelve 503 o timeout
- Múltiples alertas de uptime
- Usuario reportan "Service Unavailable"

**Diagnóstico Rápido**:
```bash
# 1. Verificar servicios
docker-compose ps

# 2. Ver logs
docker-compose logs --tail=100 backend

# 3. Verificar recursos
top
df -h
```

**Solución**:
```bash
# Restart completo
docker-compose restart backend

# Si persiste, rebuild
docker-compose up -d --force-recreate backend

# Verificar
curl http://localhost:8000/health
```

**Escalación**: Si no resuelve en 5min, contactar backup engineer.

---

### Base de Datos Inaccesible

**Síntomas**:
- Logs: "connection refused" o "too many connections"
- `/health` reporta database: unhealthy
- Timeouts en queries

**Diagnóstico**:
```bash
# Verificar PostgreSQL
docker-compose ps postgres

# Ver logs de DB
docker-compose logs postgres --tail=100

# Conectar manualmente
docker exec -it arqleads-postgres psql -U user -d arqleads

# Verificar conexiones
SELECT count(*) FROM pg_stat_activity;
```

**Solución**:

**Opción 1 - Too Many Connections**:
```sql
-- Ver conexiones activas
SELECT pid, usename, application_name, state, query
FROM pg_stat_activity
WHERE state = 'active';

-- Matar conexiones idle
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < current_timestamp - INTERVAL '10 minutes';
```

**Opción 2 - PostgreSQL caído**:
```bash
docker-compose restart postgres

# Wait 10 seconds
sleep 10

# Verificar
docker exec arqleads-postgres pg_isready
```

---

### Redis Caído

**Síntomas**:
- Logs: "Redis connection refused"
- Sistema funciona pero lento
- Cache misses = 100%

**Diagnóstico**:
```bash
# Verificar Redis
docker-compose ps redis

# Test de conexión
redis-cli ping
```

**Solución**:
```bash
# Restart Redis
docker-compose restart redis

# Verificar
redis-cli ping  # Debe responder "PONG"
```

**Nota**: Sistema continúa funcionando sin cache, solo más lento.

---

## ⚠️ Incidentes Mayores (P1)

### Performance Degradado (Response Time >1s)

**Diagnóstico**:
```bash
# Ver métricas en Prometheus
# Query: histogram_quantile(0.95, http_request_duration_seconds_bucket)

# Ver queries lentas en PostgreSQL
docker exec -it arqleads-postgres psql -U user -d arqleads
```

```sql
SELECT
    query,
    calls,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

**Solución**:

1. **Limpiar cache si está saturado**:
```bash
redis-cli FLUSHDB
```

2. **Restart backend pool**:
```bash
docker-compose restart backend
```

3. **VACUUM database** (si hay muchas escrituras):
```sql
VACUUM ANALYZE leads;
VACUUM ANALYZE conversations;
```

---

### Disco Lleno

**Síntomas**:
- Logs: "No space left on device"
- Writes fallan
- Docker no puede crear containers

**Diagnóstico**:
```bash
# Ver espacio
df -h

# Ver qué usa espacio
du -sh /var/lib/docker/*
du -sh logs/*
```

**Solución**:
```bash
# Limpiar logs viejos
find logs/ -name "*.log" -mtime +7 -delete

# Limpiar Docker
docker system prune -a --volumes

# Si persiste, mover DB a disco externo
```

---

### Memory Leak

**Síntomas**:
- Memoria aumenta constantemente
- OOM killer mata procesos
- Swap usage alto

**Diagnóstico**:
```bash
# Ver memoria
free -h

# Ver procesos
docker stats

# Memory profile (requiere py-spy)
py-spy top --pid <backend-pid>
```

**Solución**:
```bash
# Restart temporal
docker-compose restart backend

# Investigar código
# Ver archivo de perfiling en logs/
```

---

## 📊 Incidentes Menores (P2)

### Emails No Se Envían

**Diagnóstico**:
```bash
# Ver logs de email
docker-compose logs backend | grep "email"

# Verificar configuración
env | grep SMTP
```

**Solución**:

1. **Verificar credenciales SMTP**:
   - Gmail: Regenerar App Password
   - Verificar 2FA activo

2. **Test manual**:
```python
# En terminal Python
from app.core.services.email_service import email_service
import asyncio

asyncio.run(email_service.send_email(
    ['test@example.com'],
    'Test',
    '<h1>Test</h1>'
))
```

---

### Rate Limiting Excesivo

**Síntomas**:
- Usuarios reportan 429 errors
- Logs muestran muchos "Rate limit exceeded"

**Solución**:

1. **Temporal - Aumentar límite**:
```python
# En app/core/config.py
RATE_LIMIT_PER_MINUTE: int = 120  # Era 60
```

2. **Permanente - Whitelist IP**:
```python
# En app/core/rate_limit.py
# Añadir IP a whitelist
```

---

### SSL Certificate Expira

**Síntomas**:
- Browser muestra "Not Secure"
- Certificado expira en <7 días

**Solución**:
```bash
# Renovar Let's Encrypt
certbot renew --nginx

# Verificar
certbot certificates

# Reload nginx
systemctl reload nginx
```

---

## 🔍 Debugging Workflow

### 1. Verificar Logs

```bash
# Backend logs
docker-compose logs -f backend --tail=100

# Filtrar errors
docker-compose logs backend | grep ERROR

# Ver log de usuario específico
docker-compose logs backend | grep "session-12345"
```

### 2. Verificar Métricas

Prometheus: http://your-server:9090

Queries útiles:
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Response time p95
histogram_quantile(0.95, http_request_duration_seconds_bucket)

# Database connections
database_connections_active
```

### 3. Verificar Recursos

```bash
# CPU
top

# Memoria
free -h

# Disco
df -h

# Network
netstat -tupln
```

### 4. Verificar Base de Datos

```sql
-- Conexiones activas
SELECT count(*) FROM pg_stat_activity;

-- Queries corriendo ahora
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;

-- Tamaño de tablas
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 🛠️ Herramientas de Administración

### Acceder a Containers

```bash
# Backend shell
docker exec -it arqleads-backend bash

# PostgreSQL shell
docker exec -it arqleads-postgres psql -U user -d arqleads

# Redis CLI
docker exec -it arqleads-redis redis-cli
```

### Backup Database

```bash
# Crear backup
docker exec arqleads-postgres pg_dump -U user arqleads > backup_$(date +%Y%m%d).sql

# Restaurar backup
cat backup_20240115.sql | docker exec -i arqleads-postgres psql -U user -d arqleads
```

### Ver Estado General

```bash
# Todos los servicios
docker-compose ps

# Usar espacio
docker system df

# Logs de todos
docker-compose logs --tail=50
```

---

## 📞 Escalation Matrix

| Severity | Response Time | Escalate To | After |
|----------|--------------|-------------|-------|
| P0 (Critical) | Immediate | Backup Engineer | 5 min |
| P1 (Major) | 15 min | Team Lead | 30 min |
| P2 (Minor) | 1 hour | Next business day | 24 hours |
| P3 (Low) | 1 day | Weekly meeting | - |

---

## 📋 Rollback Procedures

### Rollback Backend

```bash
# Ver versiones disponibles
docker images | grep arqleads-backend

# Rollback a versión anterior
docker-compose down
docker tag arqleads-backend:latest arqleads-backend:broken
docker tag arqleads-backend:v1.2.3 arqleads-backend:latest
docker-compose up -d
```

### Rollback Database Migration

```bash
# Conectar a DB
docker exec -it arqleads-postgres psql -U user -d arqleads

# Ver versión actual
SELECT version_num FROM alembic_version;

# Rollback
docker exec arqleads-backend alembic downgrade -1
```

---

## 🔐 Seguridad Incidents

### Suspected Breach

1. **Immediate**: Cambiar todas las credenciales
2. **Review logs**: Buscar actividad sospechosa
3. **Notify**: Informar a stakeholders
4. **Document**: Crear post-mortem

### DDoS Attack

```bash
# Identificar IPs atacantes
tail -10000 /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -20

# Ban IP en firewall
ufw deny from 1.2.3.4

# Activar Cloudflare (si está configurado)
```

---

## 📚 Recursos Útiles

- **Logs**: `/var/log/arqleads/`
- **Backups**: `/backups/arqleads/`
- **Prometheus**: http://your-server:9090
- **Grafana**: http://your-server:3000
- **Documentation**: https://github.com/tu-user/ArqLeads/wiki

---

## 🎯 Health Checks Rápidos

```bash
# Script de verificación completa
#!/bin/bash

echo "=== ArqLeads Health Check ==="

# Backend
curl -f http://localhost:8000/health || echo "❌ Backend DOWN"

# PostgreSQL
docker exec arqleads-postgres pg_isready || echo "❌ PostgreSQL DOWN"

# Redis
docker exec arqleads-redis redis-cli ping | grep PONG || echo "❌ Redis DOWN"

# Disk Space
df -h / | awk 'NR==2 {if ($5+0 > 80) print "⚠️  Disk usage high: "$5}'

# Memory
free | awk 'NR==2 {if ($3/$2*100 > 80) print "⚠️  Memory usage high"}'

echo "=== Health Check Complete ==="
```

Guardar como `healthcheck.sh` y ejecutar cuando haya problemas.

---

**Última actualización**: $(date)
**Mantenido por**: DevOps Team
