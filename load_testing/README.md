# Load Testing para ArqLeads

Tests de carga usando Locust para validar la capacidad del sistema bajo tráfico intenso.

## 🚀 Setup

```bash
cd load_testing
pip install -r requirements.txt
```

## 📊 Ejecutar Tests

### Test Básico (Desarrollo)

```bash
locust -f locustfile.py --host=http://localhost:8000
```

Luego abre http://localhost:8089 y configura:
- **Number of users**: 10
- **Spawn rate**: 2 users/second

### Test Moderado (Pre-Producción)

```bash
locust -f locustfile.py --host=http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --headless
```

### Test de Estrés (Validar Límites)

```bash
locust -f locustfile.py --host=http://localhost:8000 \
  --users 200 \
  --spawn-rate 10 \
  --run-time 10m \
  --headless \
  --only-summary
```

### Test Específico (Solo Chat)

```bash
locust -f locustfile.py --host=http://localhost:8000 \
  --users 30 \
  --spawn-rate 3 \
  --class-name ChatUser
```

## 📈 Métricas a Monitorear

Durante los tests, monitorea:

### En Locust UI
- **RPS** (Requests per second): >100 RPS es bueno
- **Response time p50**: <200ms
- **Response time p95**: <500ms
- **Failure rate**: <1%

### En Prometheus/Grafana
- CPU usage: <70%
- Memory usage: <80%
- Database connections: <max pool size
- Redis connections: <max connections

### En Backend Logs
```bash
# Monitorear logs en tiempo real
docker-compose logs -f backend | grep ERROR
```

## 🎯 Objetivos de Performance

### Development
- **Users**: 10-20 concurrentes
- **RPS**: 20-50
- **Response time p95**: <1000ms
- **Uptime**: >95%

### Production
- **Users**: 100-200 concurrentes
- **RPS**: 100-200
- **Response time p95**: <500ms
- **Uptime**: >99.5%

## 🔧 Escenarios de Test

### 1. Normal Load (Baseline)

```bash
locust -f locustfile.py --host=http://localhost:8000 \
  --users 20 \
  --spawn-rate 2 \
  --run-time 5m \
  --headless
```

**Esperado**:
- 0% error rate
- <200ms p95 response time
- CPU <50%

### 2. Peak Load (Hora punta)

```bash
locust -f locustfile.py --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --headless
```

**Esperado**:
- <1% error rate
- <500ms p95 response time
- CPU <70%

### 3. Stress Test (Buscar límites)

```bash
locust -f locustfile.py --host=http://localhost:8000 \
  --users 500 \
  --spawn-rate 50 \
  --run-time 5m \
  --headless \
  --class-name StressTestUser
```

**Esperado**:
- Sistema no debe crashear
- Rate limiting debe activarse
- Errores 429 (too many requests) son aceptables

### 4. Soak Test (Estabilidad largo plazo)

```bash
locust -f locustfile.py --host=http://localhost:8000 \
  --users 30 \
  --spawn-rate 3 \
  --run-time 1h \
  --headless
```

**Esperado**:
- Sin memory leaks
- Performance consistente
- CPU estable

## 📊 Generar Reportes

### HTML Report

```bash
locust -f locustfile.py --host=http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --headless \
  --html report.html
```

### CSV Report

```bash
locust -f locustfile.py --host=http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --headless \
  --csv results
```

Genera:
- `results_stats.csv`
- `results_stats_history.csv`
- `results_failures.csv`

## 🐛 Troubleshooting

### Error: Connection refused

```bash
# Verificar que backend esté corriendo
curl http://localhost:8000/health
```

### Rate Limiting activado

```bash
# Reducir spawn rate
locust -f locustfile.py --host=http://localhost:8000 \
  --users 10 \
  --spawn-rate 1
```

### Timeout errors

```bash
# Aumentar timeout en locustfile.py
class ChatUser(HttpUser):
    connection_timeout = 30.0
    network_timeout = 30.0
```

## 📝 Interpretando Resultados

### Bueno ✅
- Response time p50: <100ms
- Response time p95: <300ms
- Failure rate: <0.5%
- RPS: >50

### Aceptable ⚠️
- Response time p50: <200ms
- Response time p95: <500ms
- Failure rate: <2%
- RPS: >30

### Malo ❌
- Response time p50: >500ms
- Response time p95: >1000ms
- Failure rate: >5%
- RPS: <20

## 🔄 CI/CD Integration

Añade esto a `.github/workflows/ci.yml`:

```yaml
- name: Load Test
  run: |
    cd load_testing
    pip install -r requirements.txt
    locust -f locustfile.py --host=http://localhost:8000 \
      --users 20 \
      --spawn-rate 2 \
      --run-time 2m \
      --headless \
      --exit-code-on-error 1
```

## 📚 Recursos

- [Locust Docs](https://docs.locust.io/)
- [Performance Testing Best Practices](https://docs.locust.io/en/stable/writing-a-locustfile.html)
- [Understanding Metrics](https://docs.locust.io/en/stable/retrieving-stats.html)
