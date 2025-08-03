# ADR-002: Data Storage Strategy

## Status
Accepted

## Context
Our data pipeline needs to store user behavior events for multiple use cases:
- Real-time analytics (last 24 hours)
- Historical analysis (up to 2 years)
- Machine learning model training
- Ad-hoc queries by data analysts
- Compliance requirements (GDPR, CCPA)

Data characteristics:
- 5TB daily raw event volume
- Semi-structured JSON events
- Write-heavy workload (50K writes/sec)
- Read patterns vary from real-time to batch

## Decision
We will implement a tiered storage strategy using multiple specialized databases:

1. **Hot Storage (0-7 days)**: DynamoDB for real-time queries
2. **Warm Storage (7-90 days)**: TimescaleDB for time-series analytics
3. **Cold Storage (90 days - 2 years)**: S3 with Parquet format
4. **Analytics Warehouse**: Redshift for business intelligence

## Consequences

### Positive
- Optimized cost per storage tier
- Best performance for each use case
- Flexible retention policies
- Easy compliance with data regulations
- Scalable to petabyte-scale

### Negative
- Complex data pipeline to maintain
- Multiple systems to monitor
- Data consistency challenges
- Higher initial development effort

## Alternatives Considered

### Single Data Warehouse (Snowflake)
- **Pros**: Unified platform, excellent performance, minimal maintenance
- **Cons**: High cost for real-time queries, vendor lock-in

### Data Lake Only (S3 + Athena)
- **Pros**: Cost-effective, serverless, infinite scale
- **Cons**: High latency for real-time queries, limited update capabilities

### NoSQL Only (DynamoDB)
- **Pros**: Excellent real-time performance, fully managed
- **Cons**: Expensive for cold storage, limited analytical capabilities

## Implementation Details

### Data Flow
```
Events → Kinesis → Lambda Router → {
  DynamoDB (real-time)
  TimescaleDB (aggregations)
  S3 (archive)
} → EMR → Redshift
```

### Storage Schemas

**DynamoDB Schema**:
```json
{
  "PK": "USER#user_id",
  "SK": "EVENT#timestamp",
  "event_type": "page_view",
  "attributes": {...},
  "ttl": 1234567890
}
```

**TimescaleDB Schema**:
```sql
CREATE TABLE events (
  time TIMESTAMPTZ NOT NULL,
  user_id UUID,
  event_type TEXT,
  attributes JSONB
);

SELECT create_hypertable('events', 'time');
```

**S3 Structure**:
```
s3://data-lake/
  events/
    year=2024/
      month=01/
        day=15/
          hour=10/
            part-00000.parquet
```

### Data Lifecycle

1. **Ingestion**: Events written to DynamoDB with TTL
2. **Aggregation**: Lambda processes events to TimescaleDB
3. **Archive**: Daily batch job converts to Parquet in S3
4. **Warehouse**: Weekly ETL loads summary data to Redshift
5. **Cleanup**: Automated deletion per retention policy

## Migration Strategy

1. Phase 1: Implement DynamoDB for new events
2. Phase 2: Add S3 archival pipeline
3. Phase 3: Deploy TimescaleDB for analytics
4. Phase 4: Migrate historical data
5. Phase 5: Deprecate legacy system

## Cost Analysis

**Monthly Estimates**:
- DynamoDB: $2,000 (on-demand mode)
- TimescaleDB: $1,500 (managed service)
- S3: $500 (with lifecycle policies)
- Redshift: $2,500 (3-node RA3 cluster)
- **Total**: ~$6,500/month

**Cost Optimizations**:
- S3 Intelligent Tiering
- DynamoDB auto-scaling
- Redshift pause/resume for dev environments
- Reserved capacity discounts

## References
- [AWS Storage Best Practices](https://aws.amazon.com/architecture/storage/)
- [Time-Series Database Comparison](https://tsdb-comparison.github.io/)
- [Data Lake Patterns](https://martinfowler.com/articles/data-lake-patterns.html)

---
**Date**: 2023-09-20  
**Author**: Data Engineering Team  
**Reviewed By**: CTO, Data Architect, Finance