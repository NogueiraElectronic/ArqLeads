# Database Optimization Guide

## 📊 Índices Implementados

### Leads Table

#### Índices Simples
- `id` (PRIMARY KEY, auto-indexed)
- `email` - Para búsqueda rápida de duplicados
- `phone` - Para búsqueda de contacto
- `category` - Para filtrado por categoría (hot/warm/cold)
- `status` - Para filtrado por estado
- `session_id` (UNIQUE) - Para lookup rápido por sesión
- `created_at` - Para queries ordenados por fecha

#### Índices Compuestos
- `idx_leads_status_created` (status, created_at)
  - **Uso**: `SELECT * FROM leads WHERE status = 'new' ORDER BY created_at DESC`
  - **Beneficio**: Evita filesort

- `idx_leads_category_score` (category, score)
  - **Uso**: `SELECT * FROM leads WHERE category = 'hot' ORDER BY score DESC`
  - **Beneficio**: Encuentra leads calientes ordenados por puntuación

- `idx_leads_hot_contacted` (category, contacted_at)
  - **Uso**: `SELECT * FROM leads WHERE category = 'hot' AND contacted_at IS NULL`
  - **Beneficio**: Identifica leads calientes sin contactar

- `idx_leads_session_created` (session_id, created_at)
  - **Uso**: Búsqueda de leads por sesión con ordenamiento temporal
  - **Beneficio**: Historial de leads por sesión

#### Índices Parciales (PostgreSQL)
- `idx_leads_hot_uncontacted` (category, created_at) WHERE category = 'hot' AND contacted_at IS NULL
  - **Uso**: Dashboard de leads urgentes
  - **Beneficio**: Índice pequeño, solo para leads críticos sin atender

### Conversations Table

#### Índices Compuestos
- `idx_conv_active_last_msg` (is_active, last_message_at)
  - **Uso**: Encontrar conversaciones activas recientes
  - **Beneficio**: Cleanup de sesiones timeout

- `idx_conv_lead_started` (lead_id, started_at)
  - **Uso**: Historial de conversaciones por lead
  - **Beneficio**: Analytics por lead

- `idx_conv_channel_started` (channel, started_at)
  - **Uso**: Analytics por canal (web, whatsapp, etc.)
  - **Beneficio**: Reportes de rendimiento por canal

#### Índices Parciales
- `idx_conv_active_only` (session_id, last_message_at) WHERE is_active = true
  - **Uso**: Solo conversaciones activas
  - **Beneficio**: Índice más pequeño para queries frecuentes

## 🚀 Query Optimization Tips

### 1. Usar EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE
SELECT * FROM leads
WHERE category = 'hot' AND contacted_at IS NULL
ORDER BY created_at DESC
LIMIT 10;
```

Verifica que use el índice `idx_leads_hot_uncontacted`.

### 2. Evitar SELECT *

❌ **Malo**:
```python
leads = session.query(Lead).all()
```

✅ **Bueno**:
```python
leads = session.query(Lead.id, Lead.name, Lead.email, Lead.score).all()
```

### 3. Usar Lazy Loading con Cuidado

❌ **N+1 Query Problem**:
```python
for lead in leads:
    print(lead.conversations)  # ¡1 query por lead!
```

✅ **Eager Loading**:
```python
from sqlalchemy.orm import joinedload

leads = session.query(Lead).options(joinedload(Lead.conversations)).all()
```

### 4. Paginación

❌ **Malo** (carga todo):
```python
leads = session.query(Lead).all()
```

✅ **Bueno** (pagination):
```python
page = 1
per_page = 20
leads = session.query(Lead).limit(per_page).offset((page - 1) * per_page).all()
```

### 5. Contar Eficientemente

❌ **Malo**:
```python
count = len(session.query(Lead).all())
```

✅ **Bueno**:
```python
count = session.query(Lead).count()
```

### 6. Bulk Operations

❌ **Malo** (1 query por insert):
```python
for data in lead_data:
    lead = Lead(**data)
    session.add(lead)
    session.commit()
```

✅ **Bueno** (bulk insert):
```python
session.bulk_insert_mappings(Lead, lead_data)
session.commit()
```

## 📈 Monitoring Queries

### Enable Query Logging (Development)

```python
# En app/core/database.py
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Slow Query Log (PostgreSQL)

```sql
-- En postgresql.conf
log_min_duration_statement = 100  # Log queries > 100ms
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_statement = 'all'
```

### Find Slow Queries

```sql
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## 🔧 Maintenance Tasks

### VACUUM y ANALYZE (PostgreSQL)

```sql
-- Manual
VACUUM ANALYZE leads;
VACUUM ANALYZE conversations;

-- Automático (pg_autovacuum)
ALTER TABLE leads SET (autovacuum_vacuum_scale_factor = 0.1);
```

### Rebuild Indexes

```sql
REINDEX TABLE leads;
REINDEX TABLE conversations;
```

### Check Index Usage

```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;
```

Índices con `idx_scan = 0` no se usan y pueden eliminarse.

### Find Missing Indexes

```sql
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
  AND n_distinct > 100
  AND correlation < 0.1;
```

## 🎯 Performance Targets

### Response Times
- **Simple queries** (by ID): <5ms
- **Filtered queries** (with indexes): <20ms
- **Complex joins**: <50ms
- **Aggregations**: <100ms

### Database Connections
- **Pool size**: 10-20 connections
- **Max overflow**: 20 connections
- **Connection timeout**: 30 seconds

### Cache Hit Ratio
- **Target**: >99%
- **Check**:
```sql
SELECT
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit)  as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
```

## 🐛 Common Issues

### Issue: Sequential Scan Instead of Index

**Síntoma**: EXPLAIN muestra "Seq Scan" en lugar de "Index Scan"

**Causas**:
1. Tabla muy pequeña (<1000 filas) - PostgreSQL prefiere seq scan
2. Query devuelve >10% de la tabla - seq scan es más eficiente
3. Estadísticas desactualizadas

**Solución**:
```sql
ANALYZE leads;  -- Actualizar estadísticas
```

### Issue: Index Bloat

**Síntoma**: Índices grandes pero tabla pequeña

**Solución**:
```sql
REINDEX INDEX idx_leads_status_created;
```

### Issue: Lock Contention

**Síntoma**: Queries lentos durante escrituras

**Solución**:
- Usar SELECT FOR UPDATE solo cuando necesario
- Acortar transacciones
- Usar índices parciales

## 📚 Resources

- [PostgreSQL Index Types](https://www.postgresql.org/docs/current/indexes-types.html)
- [SQLAlchemy Performance](https://docs.sqlalchemy.org/en/14/faq/performance.html)
- [EXPLAIN Explained](https://www.postgresql.org/docs/current/using-explain.html)
