# ✅ Production Deployment Checklist

Use este checklist antes de cada deployment a producción para asegurar que todo está configurado correctamente.

## 📋 Pre-Deployment

### Code Quality

- [ ] Todos los tests pasan (`pytest -v`)
- [ ] Frontend tests pasan (`npm run test`)
- [ ] E2E tests pasan (`npm run test:e2e`)
- [ ] Coverage >80% backend
- [ ] Coverage >80% frontend
- [ ] No hay `TODO` o `FIXME` críticos en el código
- [ ] Código revisado por otro developer (PR review)
- [ ] Linting pasa sin errores (`flake8`, `black --check`)
- [ ] TypeScript compile sin errores (`tsc --noEmit`)

### Security

- [ ] Todas las dependencias actualizadas (sin vulnerabilidades críticas)
- [ ] `SECRET_KEY` es único y >32 caracteres
- [ ] Credenciales no están en código (solo en `.env`)
- [ ] `.env` no está en git (verificar `.gitignore`)
- [ ] HTTPS configurado y funcionando
- [ ] Certificado SSL válido y no expira pronto (<30 días)
- [ ] Security headers habilitados
- [ ] Rate limiting configurado
- [ ] CORS configurado correctamente (solo dominios necesarios)
- [ ] Admin dashboard protegido con JWT
- [ ] Contraseñas de admin cambiadas del default

### Configuration

- [ ] `.env` de producción creado y revisado
- [ ] `ENVIRONMENT=production` en `.env`
- [ ] `DEBUG=False` en producción
- [ ] Database URL apunta a PostgreSQL de producción
- [ ] Redis URL apunta a Redis de producción
- [ ] SMTP configurado con credenciales reales
- [ ] `NOTIFICATION_EMAILS` configurado
- [ ] `CORS_ORIGINS` solo incluye dominios de producción
- [ ] AI provider configurado (Ollama o OpenAI)
- [ ] Logs configurados para JSON en producción

### Infrastructure

- [ ] Servidor/VPS provisionado
- [ ] Docker y Docker Compose instalados
- [ ] PostgreSQL 15+ funcionando
- [ ] Redis funcionando
- [ ] Disco: >20GB libres
- [ ] RAM: >2GB disponibles
- [ ] CPU: >2 cores
- [ ] Firewall configurado (puertos 80, 443 abiertos)
- [ ] Backup automático configurado
- [ ] Monitoring configurado (Prometheus + Grafana)

## 🚀 Deployment Steps

### 1. Backup

- [ ] Backup de base de datos actual
  ```bash
  docker exec arqleads-postgres pg_dump -U user arqleads > backup_pre_deploy_$(date +%Y%m%d_%H%M%S).sql
  ```
- [ ] Backup de archivos de configuración
  ```bash
  cp .env .env.backup
  ```
- [ ] Backup de volúmenes Docker
  ```bash
  docker run --rm -v arqleads_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data
  ```

### 2. Pull Latest Code

- [ ] Hacer pull del código
  ```bash
  git fetch --all
  git checkout main
  git pull origin main
  ```
- [ ] Verificar version/tag correcto
  ```bash
  git log -1
  git describe --tags
  ```
- [ ] Verificar no hay cambios locales
  ```bash
  git status
  ```

### 3. Build

- [ ] Build backend image
  ```bash
  docker-compose build backend
  ```
- [ ] Build frontend (si aplica)
  ```bash
  cd frontend
  npm run build
  ```
- [ ] Verificar imágenes creadas
  ```bash
  docker images | grep arqleads
  ```

### 4. Database Migration

- [ ] Verificar migraciones pendientes
  ```bash
  docker-compose run --rm backend alembic current
  docker-compose run --rm backend alembic heads
  ```
- [ ] Aplicar migraciones
  ```bash
  docker-compose run --rm backend alembic upgrade head
  ```
- [ ] Verificar migraciones aplicadas
  ```bash
  docker-compose run --rm backend alembic current
  ```

### 5. Deploy

- [ ] Stop servicios actuales
  ```bash
  docker-compose down
  ```
- [ ] Start nuevos servicios
  ```bash
  docker-compose up -d
  ```
- [ ] Verificar todos los containers corriendo
  ```bash
  docker-compose ps
  ```
- [ ] Wait 30 segundos para warm-up
  ```bash
  sleep 30
  ```

### 6. Health Checks

- [ ] Backend health check
  ```bash
  curl http://localhost:8000/health
  # Debe retornar: {"status":"healthy","database":"connected"}
  ```
- [ ] PostgreSQL check
  ```bash
  docker exec arqleads-postgres pg_isready
  ```
- [ ] Redis check
  ```bash
  docker exec arqleads-redis redis-cli ping
  # Debe retornar: PONG
  ```
- [ ] Frontend accesible
  ```bash
  curl -I http://localhost:5173/
  # Debe retornar: 200 OK
  ```
- [ ] API docs accesibles (solo si DEBUG=True)
  ```bash
  curl http://localhost:8000/docs
  ```
- [ ] Metrics endpoint
  ```bash
  curl http://localhost:8000/metrics | grep http_requests_total
  ```

### 7. Smoke Tests

- [ ] Enviar mensaje de chat
  ```bash
  curl -X POST http://localhost:8000/api/v1/chat/message \
    -H "Content-Type: application/json" \
    -d '{"session_id":"test-123","message":"Hola","language":"es","channel":"web"}'
  ```
- [ ] Ver leads
  ```bash
  curl http://localhost:8000/api/v1/leads/
  ```
- [ ] Ver stats
  ```bash
  curl http://localhost:8000/api/v1/leads/stats
  ```
- [ ] Login admin
  ```bash
  curl -X POST http://localhost:8000/admin/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}'
  ```

### 8. Monitoring

- [ ] Prometheus scrapeando métricas
  - Acceder: http://localhost:9090
  - Query: `up{job="arqleads-backend"}`
  - Debe retornar: 1
- [ ] Grafana mostrando dashboards
  - Acceder: http://localhost:3000
  - Login: admin/admin
  - Verificar dashboard "ArqLeads System"
- [ ] Alertmanager configurado
  - Acceder: http://localhost:9093
  - Verificar no hay alertas activas
- [ ] Logs estructurados funcionando
  ```bash
  docker-compose logs backend --tail=50 | grep "request_completed"
  ```

## 🔍 Post-Deployment

### Validation (First 15 minutes)

- [ ] No hay errors en logs
  ```bash
  docker-compose logs backend | grep ERROR
  ```
- [ ] Response times <500ms (p95)
  - Verificar en Grafana
- [ ] Error rate <1%
  - Verificar en Prometheus: `rate(http_requests_total{status=~"5.."}[5m])`
- [ ] CPU usage <70%
  ```bash
  docker stats --no-stream
  ```
- [ ] Memory usage <80%
  ```bash
  free -h
  ```
- [ ] Disk usage <80%
  ```bash
  df -h
  ```

### User Acceptance (First Hour)

- [ ] Probar flujo completo de chat como usuario
- [ ] Verificar lead creado en dashboard
- [ ] Verificar email de notificación enviado (si hay lead hot)
- [ ] Verificar datos correctos en PostgreSQL
  ```sql
  SELECT count(*) FROM leads WHERE created_at > NOW() - INTERVAL '1 hour';
  ```
- [ ] Cache funcionando (verificar Redis)
  ```bash
  redis-cli KEYS "*"
  redis-cli INFO stats | grep keyspace_hits
  ```

### Documentation

- [ ] Actualizar CHANGELOG.md con cambios del release
- [ ] Crear tag de version
  ```bash
  git tag -a v1.2.3 -m "Production release 1.2.3"
  git push origin v1.2.3
  ```
- [ ] Documentar en Notion/Confluence (si aplica)
- [ ] Notificar al equipo en Slack
- [ ] Actualizar documentación de API si hubo cambios

### Communication

- [ ] Avisar a stakeholders que deployment fue exitoso
- [ ] Actualizar status page (si existe)
- [ ] Documentar issues encontrados durante deployment
- [ ] Programar post-mortem si hubo problemas

## 🚨 Rollback Plan

Si algo sale mal, seguir estos pasos:

### Quick Rollback

```bash
# 1. Stop current version
docker-compose down

# 2. Restore previous images
docker tag arqleads-backend:latest arqleads-backend:broken
docker tag arqleads-backend:v1.2.2 arqleads-backend:latest

# 3. Rollback database (si aplicaste migraciones)
docker exec -it arqleads-postgres psql -U user -d arqleads
# En psql: DELETE FROM alembic_version;
docker-compose run --rm backend alembic stamp <previous_revision>

# 4. Restore .env if needed
cp .env.backup .env

# 5. Start previous version
docker-compose up -d

# 6. Verify
curl http://localhost:8000/health
```

### When to Rollback

Rollback immediately si:
- [ ] Error rate >5% por >2 minutos
- [ ] Response time p95 >2000ms por >5 minutos
- [ ] Cualquier endpoint crítico devuelve 500
- [ ] Database corrupted o inaccessible
- [ ] Memory leak evidente (memoria sube >10% por minuto)
- [ ] CPU >95% sostenido

## 📊 Success Criteria

El deployment es exitoso cuando:

- [ ] Todos los health checks pasan
- [ ] No hay errores en logs (últimos 15 min)
- [ ] Response time p95 <500ms
- [ ] Error rate <0.5%
- [ ] Uptime 100% (primeros 15 min)
- [ ] Todas las funcionalidades críticas funcionan:
  - [ ] Chat bot responde
  - [ ] Leads se crean
  - [ ] Dashboard admin accesible
  - [ ] Emails se envían (si hay lead hot)
  - [ ] Métricas se recolectan
- [ ] No hay quejas de usuarios (primeros 60 min)

## 🔐 Security Post-Deployment

- [ ] Cambiar credenciales default si es primera instalación
- [ ] Revisar logs de acceso por IPs sospechosas
  ```bash
  tail -1000 /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn
  ```
- [ ] Verificar certificado SSL
  ```bash
  echo | openssl s_client -servername tu-dominio.com -connect tu-dominio.com:443 2>/dev/null | openssl x509 -noout -dates
  ```
- [ ] Test de penetración básico (si aplica)
- [ ] Verificar headers de seguridad
  ```bash
  curl -I https://tu-dominio.com | grep -E "Strict-Transport|X-Content-Type|X-Frame"
  ```

## 📅 Scheduled Maintenance

### Daily

- [ ] Revisar logs por errores
- [ ] Verificar backups automáticos completados
- [ ] Revisar alertas en Grafana

### Weekly

- [ ] Revisar métricas de performance
- [ ] Verificar espacio en disco >20% libre
- [ ] Actualizar dependencias con vulnerabilidades
- [ ] Revisar y limpiar logs viejos

### Monthly

- [ ] Test de restore de backup
- [ ] Revisar y actualizar documentación
- [ ] Security audit
- [ ] Performance tuning basado en métricas

## 📝 Deployment Log Template

```markdown
# Deployment Log - [DATE]

## Version
- Tag: v1.2.3
- Commit: abc123
- Deployed by: [NAME]

## Pre-Deployment
- Tests: ✅ All passed
- Code review: ✅ Approved by [REVIEWER]
- Backup: ✅ Created at [TIME]

## Deployment
- Started: [TIME]
- Completed: [TIME]
- Duration: [MINUTES]
- Issues: [NONE / LIST ISSUES]

## Post-Deployment
- Health checks: ✅ All passed
- Smoke tests: ✅ All passed
- User validation: ✅ No complaints
- Performance: ✅ Within targets

## Rollback
- Required: ❌ No
- Reason: N/A

## Notes
[Any additional notes or observations]
```

---

**Last Updated**: $(date +%Y-%m-%d)
**Version**: 1.0.0
**Maintained by**: DevOps Team
