# Operations Runbook

## Table of Contents

1. [System Overview](#system-overview)
2. [Critical Services](#critical-services)
3. [Monitoring & Alerts](#monitoring--alerts)
4. [Common Operations](#common-operations)
5. [Incident Response](#incident-response)
6. [Disaster Recovery](#disaster-recovery)
7. [Maintenance Procedures](#maintenance-procedures)
8. [Performance Tuning](#performance-tuning)
9. [Security Operations](#security-operations)
10. [Escalation Procedures](#escalation-procedures)

## System Overview

### Architecture Summary

The User Behavior Data Pipeline is a distributed system processing millions of events per day across multiple AWS regions.

**Key Metrics:**
- Average throughput: 50,000 events/second
- Peak throughput: 200,000 events/second
- Data retention: 7 days (hot), 90 days (warm), 2 years (cold)
- SLA: 99.9% availability

### Infrastructure Layout

```
Primary Region: us-east-1
DR Region: us-west-2
Edge Locations: Global CloudFront

Components:
├── Ingestion Layer (API Gateway + Lambda)
├── Streaming Layer (Kinesis Data Streams)
├── Processing Layer (ECS Fargate + EMR)
├── Storage Layer (S3 + DynamoDB + Redshift)
└── Analytics Layer (Athena + QuickSight)
```

## Critical Services

### Service Inventory

| Service | Type | Criticality | Dependencies | Health Check |
|---------|------|-------------|--------------|--------------|
| Ingestion API | ECS Service | Critical | ALB, Kinesis | `/health` |
| Stream Processor | ECS Service | Critical | Kinesis, S3 | `/health` |
| Event Validator | Lambda | Critical | API Gateway | CloudWatch |
| Real-time Aggregator | Lambda | High | DynamoDB | CloudWatch |
| Batch Processor | EMR | Medium | S3, Redshift | EMR Console |
| Data API | ECS Service | High | Redshift, Cache | `/health` |

### Service URLs

**Production:**
- API Endpoint: `https://api.analytics.company.com`
- Dashboard: `https://dashboard.analytics.company.com`
- Monitoring: `https://monitoring.analytics.company.com`

**Internal:**
- Grafana: `https://grafana.internal.company.com`
- Kibana: `https://kibana.internal.company.com`
- Jaeger: `https://jaeger.internal.company.com`

## Monitoring & Alerts

### Key Dashboards

#### 1. System Health Dashboard

URL: `https://cloudwatch.amazonaws.com/dashboard/pipeline-health`

**Critical Metrics:**
- API Success Rate (Target: >99.9%)
- API Latency p99 (Target: <100ms)
- Stream Processing Lag (Target: <30s)
- Error Rate (Target: <0.1%)

#### 2. Business Metrics Dashboard

URL: `https://cloudwatch.amazonaws.com/dashboard/business-metrics`

**Key Indicators:**
- Events Per Second
- Daily Active Users
- Data Quality Score
- Revenue Attribution

### Alert Configuration

#### Critical Alerts (PagerDuty)

| Alert | Condition | Action | Runbook |
|-------|-----------|--------|---------|
| API Down | 3 failed health checks in 5 min | Page on-call | [Link](#api-down) |
| High Error Rate | Error rate >5% for 5 min | Page on-call | [Link](#high-error-rate) |
| Stream Backup | Lag >5 minutes | Page on-call | [Link](#stream-backup) |
| Data Loss | Events dropped >1000/min | Page on-call | [Link](#data-loss) |

#### Warning Alerts (Slack)

| Alert | Condition | Channel | Action |
|-------|-----------|---------|--------|
| High Latency | p99 >200ms for 10 min | #ops-alerts | Investigate |
| Disk Usage | >80% utilization | #ops-alerts | Clean up |
| Cost Spike | Daily spend >120% avg | #ops-alerts | Review usage |

### Monitoring Commands

```bash
# Check service health
aws ecs describe-services --cluster prod-cluster --services ingestion-api

# View recent alarms
aws cloudwatch describe-alarms --state-value ALARM

# Check Kinesis metrics
aws kinesis describe-stream-summary --stream-name user-events-prod

# Database connections
aws rds describe-db-instances --db-instance-identifier prod-analytics-db
```

## Common Operations

### 1. Scaling Operations

#### Auto-scaling ECS Service

```bash
# Scale up ingestion API
aws ecs update-service \
  --cluster prod-cluster \
  --service ingestion-api \
  --desired-count 20

# Update auto-scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/prod-cluster/ingestion-api \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

#### Scaling Kinesis Shards

```bash
# Check current shard count
aws kinesis describe-stream-summary --stream-name user-events-prod

# Update shard count
aws kinesis update-shard-count \
  --stream-name user-events-prod \
  --target-shard-count 100 \
  --scaling-type UNIFORM_SCALING
```

### 2. Deployment Operations

#### Blue-Green Deployment

```bash
# 1. Create new task definition
aws ecs register-task-definition --cli-input-json file://task-def.json

# 2. Update service to use new task definition
aws ecs update-service \
  --cluster prod-cluster \
  --service ingestion-api \
  --task-definition ingestion-api:25

# 3. Monitor deployment
watch -n 5 aws ecs describe-services \
  --cluster prod-cluster \
  --services ingestion-api \
  --query 'services[0].deployments'

# 4. Rollback if needed
aws ecs update-service \
  --cluster prod-cluster \
  --service ingestion-api \
  --task-definition ingestion-api:24
```

#### Lambda Deployment

```bash
# Deploy new Lambda version
aws lambda update-function-code \
  --function-name event-validator \
  --s3-bucket company-lambda-artifacts \
  --s3-key event-validator-v1.2.0.zip

# Update alias to new version
aws lambda update-alias \
  --function-name event-validator \
  --name production \
  --function-version 15

# Gradual rollout with weighted alias
aws lambda update-alias \
  --function-name event-validator \
  --name production \
  --function-version 15 \
  --routing-config AdditionalVersionWeights={14=0.9,15=0.1}
```

### 3. Data Operations

#### Backfill Historical Data

```python
#!/usr/bin/env python3
# scripts/backfill_data.py

import boto3
from datetime import datetime, timedelta

def backfill_events(start_date, end_date):
    """Backfill events for date range"""
    s3 = boto3.client('s3')
    
    current_date = start_date
    while current_date <= end_date:
        source_key = f"raw-events/year={current_date.year}/month={current_date.month:02d}/day={current_date.day:02d}/"
        
        # List all event files for the day
        response = s3.list_objects_v2(
            Bucket='company-events-archive',
            Prefix=source_key
        )
        
        for obj in response.get('Contents', []):
            # Trigger reprocessing
            process_historical_file(obj['Key'])
        
        current_date += timedelta(days=1)

if __name__ == "__main__":
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 7)
    backfill_events(start, end)
```

#### Data Quality Checks

```sql
-- Check for data completeness
WITH hourly_counts AS (
  SELECT 
    DATE_TRUNC('hour', event_timestamp) as hour,
    COUNT(*) as event_count
  FROM events
  WHERE event_timestamp >= NOW() - INTERVAL '24 hours'
  GROUP BY 1
)
SELECT 
  hour,
  event_count,
  LAG(event_count) OVER (ORDER BY hour) as prev_hour_count,
  CASE 
    WHEN event_count < LAG(event_count) OVER (ORDER BY hour) * 0.5 
    THEN 'ANOMALY: 50% drop'
    ELSE 'OK'
  END as status
FROM hourly_counts
ORDER BY hour DESC;

-- Check for duplicate events
SELECT 
  event_id,
  COUNT(*) as duplicate_count
FROM events
WHERE event_timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY event_id
HAVING COUNT(*) > 1;
```

## Incident Response

### Incident Severity Levels

| Level | Description | Response Time | Examples |
|-------|-------------|---------------|----------|
| SEV1 | Complete outage | 15 minutes | API down, data loss |
| SEV2 | Major degradation | 30 minutes | High error rate, processing delays |
| SEV3 | Minor degradation | 2 hours | Slow queries, partial feature loss |
| SEV4 | Low impact | Next business day | Non-critical bugs |

### Incident Response Procedures

#### API Down

**Symptoms:**
- Health checks failing
- 5xx errors from ALB
- No events being processed

**Immediate Actions:**
1. Check ECS service status
   ```bash
   aws ecs describe-services --cluster prod-cluster --services ingestion-api
   ```

2. Review recent deployments
   ```bash
   aws ecs describe-task-definition --task-definition ingestion-api
   ```

3. Check ALB target health
   ```bash
   aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:xxx
   ```

4. Scale up if needed
   ```bash
   aws ecs update-service --cluster prod-cluster --service ingestion-api --desired-count 10
   ```

5. Check logs
   ```bash
   aws logs tail /ecs/ingestion-api --follow
   ```

**Root Cause Analysis:**
- Memory leaks
- Database connection exhaustion
- Bad deployment
- AWS service issues

#### High Error Rate

**Symptoms:**
- Error rate >5%
- Increased 4xx/5xx responses
- Customer complaints

**Immediate Actions:**
1. Identify error patterns
   ```bash
   aws logs filter-log-events \
     --log-group-name /ecs/ingestion-api \
     --filter-pattern "ERROR" \
     --start-time $(date -u -d '1 hour ago' +%s)000
   ```

2. Check recent changes
   ```bash
   git log --since="2 hours ago" --oneline
   ```

3. Review error metrics
   ```sql
   SELECT 
     error_type,
     COUNT(*) as count,
     MIN(timestamp) as first_seen,
     MAX(timestamp) as last_seen
   FROM error_logs
   WHERE timestamp > NOW() - INTERVAL '1 hour'
   GROUP BY error_type
   ORDER BY count DESC;
   ```

4. Enable debug logging if needed
   ```bash
   aws ecs update-service \
     --cluster prod-cluster \
     --service ingestion-api \
     --task-definition ingestion-api:debug
   ```

#### Stream Backup

**Symptoms:**
- Kinesis consumer lag increasing
- Processing delays
- Memory pressure on consumers

**Immediate Actions:**
1. Check consumer lag
   ```bash
   aws kinesis describe-stream-consumer \
     --stream-arn arn:aws:kinesis:xxx \
     --consumer-name stream-processor
   ```

2. Scale up processors
   ```bash
   aws ecs update-service \
     --cluster prod-cluster \
     --service stream-processor \
     --desired-count 20
   ```

3. Check for poison messages
   ```python
   # scripts/check_poison_messages.py
   import boto3
   import json
   
   kinesis = boto3.client('kinesis')
   
   response = kinesis.get_records(
       ShardIterator=shard_iterator,
       Limit=100
   )
   
   for record in response['Records']:
       try:
           data = json.loads(record['Data'])
           # Validate event
       except Exception as e:
           print(f"Invalid record: {record['SequenceNumber']}")
   ```

4. Skip problematic records if needed
   ```bash
   # Update checkpoint to skip records
   aws dynamodb update-item \
     --table-name kinesis-checkpoints \
     --key '{"ShardId": {"S": "shardId-000000000000"}}' \
     --update-expression "SET SequenceNumber = :seq" \
     --expression-attribute-values '{":seq": {"S": "49234567890123456789"}}'
   ```

## Disaster Recovery

### DR Strategy

**RTO:** 15 minutes for critical services
**RPO:** 5 minutes for event data

### Failover Procedures

#### 1. Regional Failover

```bash
#!/bin/bash
# scripts/dr_failover.sh

# 1. Update Route53 to point to DR region
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.analytics.company.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z0987654321XYZ",
          "DNSName": "dr-alb.us-west-2.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'

# 2. Enable DR Kinesis streams
aws kinesis enable-stream-encryption \
  --stream-name user-events-dr \
  --region us-west-2

# 3. Start DR processing services
aws ecs update-service \
  --cluster dr-cluster \
  --service ingestion-api \
  --desired-count 10 \
  --region us-west-2

# 4. Verify health
curl https://api-dr.analytics.company.com/health
```

#### 2. Database Failover

```bash
# Promote read replica to primary
aws rds promote-read-replica \
  --db-instance-identifier analytics-db-replica-1 \
  --backup-retention-period 7

# Update connection strings
aws secretsmanager update-secret \
  --secret-id prod/database/connection \
  --secret-string '{"host":"analytics-db-replica-1.xxx.rds.amazonaws.com"}'

# Verify connections
psql -h analytics-db-replica-1.xxx.rds.amazonaws.com -U admin -d analytics
```

### Backup Verification

```bash
# Daily backup verification script
#!/bin/bash

# Check S3 backups
aws s3 ls s3://company-backups/daily/$(date +%Y/%m/%d)/ \
  || alert "S3 backup missing for $(date +%Y/%m/%d)"

# Verify DynamoDB backups
aws dynamodb list-backups \
  --table-name real-time-events \
  --time-range-lower-bound $(date -u -d '1 day ago' +%s) \
  || alert "DynamoDB backup missing"

# Test restore procedure
aws dynamodb restore-table-from-backup \
  --target-table-name test-restore-$(date +%s) \
  --backup-arn arn:aws:dynamodb:xxx:backup/xxx
```

## Maintenance Procedures

### Scheduled Maintenance

#### Weekly Tasks

**Monday: Capacity Review**
```bash
# Review last week's usage
./scripts/capacity_report.sh

# Plan for upcoming events
# Update auto-scaling policies if needed
```

**Wednesday: Security Updates**
```bash
# Scan for vulnerabilities
./scripts/security_scan.sh

# Apply patches to non-production
./scripts/apply_patches.sh staging
```

**Friday: Backup Verification**
```bash
# Test restore procedures
./scripts/test_restore.sh

# Verify cross-region replication
./scripts/verify_replication.sh
```

### Database Maintenance

#### Index Optimization

```sql
-- Analyze query performance
SELECT 
  query,
  calls,
  mean_time,
  total_time
FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY mean_time DESC
LIMIT 20;

-- Create missing indexes
CREATE INDEX CONCURRENTLY idx_events_user_timestamp 
ON events(user_id, event_timestamp)
WHERE event_timestamp > NOW() - INTERVAL '7 days';

-- Remove unused indexes
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND indexrelname NOT LIKE '%_pkey';
```

#### Vacuum Operations

```bash
# Schedule vacuum during low traffic
0 3 * * * psql -U admin -d analytics -c "VACUUM ANALYZE events;"

# Monitor vacuum progress
SELECT 
  pid,
  now() - query_start as duration,
  query
FROM pg_stat_activity
WHERE query LIKE 'VACUUM%';
```

### Certificate Renewal

```bash
# Check certificate expiry
openssl x509 -enddate -noout -in /etc/ssl/certs/api.crt

# Renew certificate (30 days before expiry)
certbot renew --nginx

# Update ALB certificate
aws elbv2 add-listener-certificates \
  --listener-arn arn:aws:elasticloadbalancing:xxx \
  --certificates CertificateArn=arn:aws:acm:xxx
```

## Performance Tuning

### Application Tuning

#### API Performance

```javascript
// Optimize connection pooling
const pool = new Pool({
  max: 20, // Maximum connections
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Enable response compression
app.use(compression({
  filter: (req, res) => {
    if (req.headers['x-no-compression']) {
      return false;
    }
    return compression.filter(req, res);
  }
}));

// Implement caching
const cache = new NodeCache({ 
  stdTTL: 600, // 10 minutes
  checkperiod: 120 
});
```

#### Stream Processing

```python
# Optimize batch processing
class BatchProcessor:
    def __init__(self):
        self.batch_size = 1000
        self.batch_timeout = 5  # seconds
        
    def process_records(self, records):
        # Process in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for batch in self.chunk_records(records, self.batch_size):
                future = executor.submit(self.process_batch, batch)
                futures.append(future)
            
            # Wait for completion
            concurrent.futures.wait(futures)
```

### Database Tuning

```sql
-- Optimize Redshift performance
-- Set distribution style
ALTER TABLE events
ALTER DISTKEY user_id;

-- Set sort keys
ALTER TABLE events
ALTER SORTKEY (event_timestamp, user_id);

-- Analyze statistics
ANALYZE events;

-- Configure workload management
CREATE USER GROUP analytics_heavy;
CREATE USER GROUP analytics_light;

-- Set query priorities
ALTER GROUP analytics_heavy SET query_group TO 'heavy';
ALTER GROUP analytics_light SET query_group TO 'light';
```

### Infrastructure Optimization

```bash
# Right-size instances
./scripts/analyze_instance_usage.sh

# Enable S3 intelligent tiering
aws s3api put-bucket-intelligent-tiering-configuration \
  --bucket company-events-prod \
  --id archive-old-data \
  --intelligent-tiering-configuration file://tiering-config.json

# Optimize data transfer costs
# Use VPC endpoints
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-12345678 \
  --service-name com.amazonaws.us-east-1.s3
```

## Security Operations

### Security Monitoring

```bash
# Monitor for suspicious activity
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=DeleteBucket \
  --start-time $(date -u -d '1 day ago' +%s)

# Check for exposed credentials
git secrets --scan

# Review IAM permissions
aws iam get-account-authorization-details \
  | jq '.Policies[] | select(.PolicyName | contains("Admin"))'
```

### Incident Response

#### Data Breach Response

1. **Contain**
   ```bash
   # Revoke potentially compromised credentials
   aws iam delete-access-key --access-key-id AKIAXXXXXXXXXXXXXXXX
   
   # Block suspicious IPs
   aws wafv2 update-ip-set \
     --scope REGIONAL \
     --id xxxxx \
     --addresses 192.0.2.1/32
   ```

2. **Investigate**
   ```bash
   # Review access logs
   aws s3 sync s3://company-access-logs/$(date +%Y/%m/%d)/ ./incident/
   
   # Analyze with athena
   aws athena start-query-execution \
     --query-string "SELECT * FROM access_logs WHERE ip_address = '192.0.2.1'"
   ```

3. **Remediate**
   ```bash
   # Rotate all secrets
   ./scripts/rotate_all_secrets.sh
   
   # Force password reset
   aws cognito-idp admin-reset-user-password \
     --user-pool-id us-east-1_xxxxxxxxx \
     --username affected-user
   ```

### Compliance Checks

```bash
# GDPR compliance - data deletion
./scripts/delete_user_data.sh user_id

# Data retention compliance
DELETE FROM events
WHERE event_timestamp < NOW() - INTERVAL '2 years';

# Audit trail verification
SELECT 
  action,
  user_id,
  timestamp,
  ip_address
FROM audit_logs
WHERE timestamp > NOW() - INTERVAL '90 days'
ORDER BY timestamp DESC;
```

## Escalation Procedures

### Escalation Matrix

| Severity | Initial Response | Escalation Time | Escalation To |
|----------|-----------------|-----------------|---------------|
| SEV1 | On-call Engineer | Immediate | Team Lead + Sr. Engineer |
| SEV1 | Team Lead | 30 minutes | Engineering Manager + CTO |
| SEV2 | On-call Engineer | 30 minutes | Team Lead |
| SEV2 | Team Lead | 2 hours | Engineering Manager |
| SEV3 | On-call Engineer | 2 hours | Team Lead |
| SEV4 | On-call Engineer | Next day | Team Lead |

### Contact Information

**On-Call Rotation:**
- Primary: Check PagerDuty
- Secondary: Check PagerDuty
- Manager: John Smith (+1-555-0123)

**Vendor Support:**
- AWS Support: [AWS Console](https://console.aws.amazon.com/support)
- Datadog Support: support@datadoghq.com
- PagerDuty: support@pagerduty.com

**Internal Teams:**
- Security Team: security@company.com
- Network Team: network-ops@company.com
- Database Team: database-ops@company.com

### Communication Templates

#### Incident Start
```
Subject: [SEV1] Data Pipeline Incident - [Brief Description]

Status: Investigating
Start Time: [Time]
Impact: [User impact description]
Actions: [Current actions being taken]

Updates will be provided every 15 minutes.
```

#### Status Update
```
Subject: [SEV1] Update - [Brief Description]

Status: [Investigating/Mitigating/Resolved]
Duration: [Time since start]
Impact: [Current impact]
Progress: [What's been done]
Next Steps: [What's planned]
ETA: [Resolution estimate]
```

#### Post-Mortem
```
Subject: [RESOLVED] Post-Mortem - [Incident Description]

Incident Duration: [Start] - [End]
Impact: [Detailed impact]
Root Cause: [Technical explanation]
Resolution: [How it was fixed]
Action Items: [Prevention measures]
```

---

**Document Version:** 2.0
**Last Updated:** January 15, 2024
**Next Review:** April 15, 2024
**Owner:** Platform Engineering Team