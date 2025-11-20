# Redis Caching Strategy

## 🚀 Overview

ArqLeads uses Redis for caching frequently accessed data to reduce database load and improve response times.

## 📊 Cached Data Types

### 1. Lead Statistics (60 seconds TTL)
- **Key**: `lead:stats`
- **Endpoint**: `/api/v1/leads/stats`
- **Why**: Heavily accessed by dashboard (every 30 seconds)
- **Impact**: Reduces 12+ database queries to 1 Redis GET
- **Invalidation**: Auto-expires after 60s

### 2. Individual Leads (5 minutes TTL)
- **Key**: `lead:id:{lead_id}`
- **Endpoint**: `/api/v1/leads/{lead_id}`
- **Why**: Lead details accessed repeatedly
- **Impact**: Eliminates 1 database query per request
- **Invalidation**: When lead is updated

### 3. Session-based Leads (30 minutes TTL)
- **Key**: `lead:session:{session_id}`
- **Endpoint**: Internal chat service
- **Why**: Active chat sessions query same lead repeatedly
- **Impact**: Reduces lead lookups during conversations
- **Invalidation**: When conversation ends

### 4. Hot Uncontacted Leads (2 minutes TTL)
- **Key**: `lead:hot:uncontacted`
- **Endpoint**: `/api/v1/leads/hot`
- **Why**: Critical for sales team, checked frequently
- **Impact**: Fast response for priority leads
- **Invalidation**: When new hot lead created or lead contacted

## 🎯 Caching Patterns

### Pattern 1: Cache-Aside (Lazy Loading)

```python
from app.core.cache import cache, CacheKeys, CacheTTL

def get_lead_by_id(lead_id: int, db: Session):
    # Try cache first
    cache_key = f"{CacheKeys.LEAD_BY_ID}:{lead_id}"
    cached_lead = cache.get(cache_key)

    if cached_lead:
        return cached_lead

    # Cache miss - query database
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if lead:
        # Store in cache
        cache.set(cache_key, lead.to_dict(), CacheTTL.MEDIUM)

    return lead
```

### Pattern 2: Write-Through

```python
def update_lead(lead_id: int, data: dict, db: Session):
    # Update database
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    for key, value in data.items():
        setattr(lead, key, value)
    db.commit()

    # Update cache immediately
    cache_key = f"{CacheKeys.LEAD_BY_ID}:{lead_id}"
    cache.set(cache_key, lead.to_dict(), CacheTTL.MEDIUM)

    # Invalidate related caches
    cache.delete(CacheKeys.LEAD_STATS)

    return lead
```

### Pattern 3: Cache Invalidation

```python
def create_lead(data: dict, db: Session):
    lead = Lead(**data)
    db.add(lead)
    db.commit()

    # Invalidate stats cache (now outdated)
    cache.delete(CacheKeys.LEAD_STATS)

    # Invalidate list caches
    cache.delete_pattern("lead:list:*")

    return lead
```

## 📈 Performance Impact

### Before Caching

```
GET /api/v1/leads/stats
- Database queries: 12
- Response time: 150-250ms
- Database load: High
```

### After Caching

```
GET /api/v1/leads/stats (cache hit)
- Database queries: 0
- Response time: 5-15ms
- Database load: Minimal

GET /api/v1/leads/stats (cache miss)
- Database queries: 12
- Response time: 150-250ms + 5ms (cache write)
- Database load: Moderate (only on miss)
```

### Hit Rate Targets
- **Production**: >95%
- **Development**: >80%
- **Low traffic periods**: >70%

## 🔧 Configuration

### Cache TTL Values

```python
class CacheTTL:
    SHORT = 60        # 1 minute - Fast-changing data
    MEDIUM = 300      # 5 minutes - Moderate changes
    LONG = 1800       # 30 minutes - Slow-changing data
    HOUR = 3600       # 1 hour - Rarely changes
    DAY = 86400       # 24 hours - Static data
```

### Redis Configuration

```env
# .env
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50
CACHE_ENABLED=true
CACHE_TTL_SECONDS=300
```

## 🛠️ Cache Management

### Clear All Cache

```bash
# Via Redis CLI
redis-cli FLUSHDB

# Via Python
from app.core.cache import cache
cache.clear_all()
```

### Clear Specific Pattern

```python
# Clear all lead caches
cache.delete_pattern("lead:*")

# Clear all stats caches
cache.delete_pattern("*:stats")
```

### Monitor Cache

```python
# Get cache statistics
from app.core.cache import cache

stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
print(f"Total keys: {stats['total_keys']}")
print(f"Memory used: {stats['used_memory']}")
```

## 🎨 Decorator Usage

```python
from app.core.cache import cached, CacheTTL

@cached("user_profile", ttl=CacheTTL.MEDIUM)
def get_user_profile(user_id: int):
    """Function result will be cached."""
    return expensive_operation(user_id)

# Invalidate specific cache
get_user_profile.invalidate(user_id=123)

# Invalidate all user profile caches
get_user_profile.invalidate_all()
```

## ⚠️ Cache Invalidation Rules

### When to Invalidate

1. **After CREATE operations**
   - Invalidate list caches
   - Invalidate stats caches

2. **After UPDATE operations**
   - Invalidate specific item cache
   - Invalidate related list caches
   - Invalidate stats if aggregates changed

3. **After DELETE operations**
   - Invalidate specific item cache
   - Invalidate all related caches
   - Invalidate stats caches

### Example

```python
def create_lead(data: dict, db: Session):
    lead = Lead(**data)
    db.add(lead)
    db.commit()

    # Invalidate caches
    cache.delete(CacheKeys.LEAD_STATS)           # Stats changed
    cache.delete(CacheKeys.LEAD_LIST)            # List changed
    if lead.category == LeadCategory.HOT:
        cache.delete(CacheKeys.LEAD_HOT_UNCONTACTED)  # Hot list changed

    return lead
```

## 🐛 Debugging

### Enable Cache Logging

```python
import structlog

logger = structlog.get_logger("cache")
logger.setLevel("DEBUG")
```

### Monitor Cache Keys

```bash
# List all keys
redis-cli KEYS "*"

# List lead keys
redis-cli KEYS "lead:*"

# Get key TTL
redis-cli TTL "lead:stats"

# Get key value
redis-cli GET "lead:stats"
```

### Bypass Cache (Testing)

```env
# In .env
CACHE_ENABLED=false
```

## 📊 Metrics to Monitor

### Cache Performance

```promql
# Cache hit rate
cache_hits / (cache_hits + cache_misses)

# Cache response time
histogram_quantile(0.95, cache_response_time_bucket)

# Memory usage
redis_memory_used_bytes / redis_memory_max_bytes
```

### Database Load Reduction

```promql
# Database queries before/after caching
rate(database_queries_total[5m])

# Query response time improvement
histogram_quantile(0.95, http_request_duration_seconds_bucket{endpoint="/stats"})
```

## 🔒 Security Considerations

1. **Sensitive Data**: Don't cache PII without encryption
2. **Cache Poisoning**: Validate data before caching
3. **Access Control**: Redis should not be publicly accessible
4. **TTL**: Keep sensitive data TTL short

## 🚀 Best Practices

1. **Start with high TTL**, reduce if data freshness is an issue
2. **Monitor hit rates** - <80% means caching isn't effective
3. **Invalidate proactively** when data changes
4. **Use cache warming** for critical data
5. **Implement circuit breaker** - if Redis is down, continue without cache
6. **Namespace keys** to avoid collisions
7. **Set memory limits** on Redis to prevent OOM

## 📚 Resources

- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [Caching Strategies](https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/Strategies.html)
- [Cache Invalidation Patterns](https://martinfowler.com/bliki/TwoHardThings.html)
