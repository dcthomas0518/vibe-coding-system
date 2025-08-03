# ADR-003: API Design Patterns for Event Ingestion

## Status
Accepted

## Context
We need to design APIs that can:
- Handle 50,000+ events per second
- Support both real-time and batch ingestion
- Work across web, mobile, and server environments
- Maintain <100ms p99 latency
- Provide reliable delivery guarantees
- Support multiple authentication methods

## Decision
We will implement three complementary API patterns:

1. **REST API** for standard HTTP clients
2. **Beacon API** for fire-and-forget browser events
3. **gRPC API** for high-performance server-to-server communication

All APIs will follow these design principles:
- Idempotent operations using client-generated UUIDs
- Async processing with immediate acknowledgment
- Schema validation at edge
- Automatic retries with exponential backoff

## Consequences

### Positive
- Optimal protocol for each use case
- Better performance and reliability
- Simplified client implementations
- Strong typing with gRPC
- Graceful degradation with Beacon API

### Negative
- Multiple API surfaces to maintain
- More complex testing requirements
- Additional documentation needs
- Higher initial development cost

## Alternatives Considered

### GraphQL Only
- **Pros**: Flexible queries, single endpoint, strong typing
- **Cons**: Overhead for simple event tracking, complex caching

### WebSocket/SSE
- **Pros**: Real-time bidirectional communication
- **Cons**: Complex connection management, not suitable for fire-and-forget

### REST Only
- **Pros**: Simple, well-understood, broad client support
- **Cons**: Not optimal for all use cases, higher overhead

## Implementation Details

### REST API Design

**Endpoint Structure**:
```
POST /v1/events          # Single event
POST /v1/events/batch    # Batch events (max 500)
GET  /v1/health         # Health check
GET  /v1/stats          # Client statistics
```

**Request/Response Flow**:
```
Client → CloudFront → API Gateway → Lambda → Kinesis
                ↓
            WAF Rules
```

**Example Request**:
```http
POST /v1/events
Content-Type: application/json
X-API-Key: pk_live_xxxxx

{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "page_view",
  "event_timestamp": "2024-01-15T10:30:00.000Z",
  "properties": {...}
}

Response:
HTTP/1.1 202 Accepted
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "accepted"
}
```

### Beacon API Design

**Optimized for**:
- Page unload events
- Non-critical tracking
- Minimal client code

**Implementation**:
```javascript
// Client SDK
function sendBeacon(event) {
  const data = new URLSearchParams({
    e: event.type,
    t: Date.now(),
    s: sessionId,
    p: JSON.stringify(event.properties)
  });
  
  navigator.sendBeacon('/v1/events/beacon', data);
}
```

### gRPC API Design

**Protocol Buffers Definition**:
```protobuf
syntax = "proto3";

service EventIngestion {
  rpc SendEvent(Event) returns (EventResponse);
  rpc SendEventStream(stream Event) returns (StreamResponse);
  rpc SendBatch(EventBatch) returns (BatchResponse);
}

message Event {
  string event_id = 1;
  string event_type = 2;
  google.protobuf.Timestamp timestamp = 3;
  map<string, google.protobuf.Value> properties = 4;
}
```

### Error Handling Strategy

**Error Codes**:
```json
{
  "4001": "Invalid event schema",
  "4002": "Missing required field",
  "4003": "Invalid timestamp",
  "4291": "Rate limit exceeded",
  "5001": "Internal processing error",
  "5002": "Downstream service unavailable"
}
```

**Retry Logic**:
```python
def retry_with_backoff(func, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            return func()
        except RetryableError as e:
            if attempt == max_attempts - 1:
                raise
            delay = min(300, (2 ** attempt) + random.uniform(0, 1))
            time.sleep(delay)
```

### Rate Limiting

**Token Bucket Algorithm**:
- Standard: 1,000 requests/minute
- Burst: 2,000 requests/minute for 60 seconds
- Enterprise: 10,000 requests/minute

**Implementation**:
```python
class RateLimiter:
    def __init__(self, rate, burst):
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
    
    def allow_request(self):
        now = time.time()
        self.tokens += (now - self.last_update) * self.rate
        self.tokens = min(self.tokens, self.burst)
        self.last_update = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
```

### Security Measures

1. **API Key Validation**
   - Public keys for client-side (domain-restricted)
   - Private keys for server-side (IP-restricted)

2. **Request Signing**
   ```python
   signature = hmac.new(
       secret_key.encode(),
       f"{timestamp}{request_body}".encode(),
       hashlib.sha256
   ).hexdigest()
   ```

3. **Input Validation**
   - JSON schema validation
   - Field length limits
   - Malicious pattern detection

4. **DDoS Protection**
   - CloudFront rate limiting
   - AWS WAF rules
   - Geographic restrictions

## Performance Optimizations

1. **Connection Pooling**
   - Keep-alive connections
   - Connection reuse
   - Optimal pool sizing

2. **Request Batching**
   - Client-side buffering
   - Compressed payloads
   - Optimal batch sizes

3. **Edge Processing**
   - Lambda@Edge validation
   - Early rejection of invalid requests
   - Response caching

## Monitoring and Observability

**Key Metrics**:
- Request rate by endpoint
- Latency percentiles (p50, p95, p99)
- Error rates by type
- Payload sizes
- Client SDK versions

**Distributed Tracing**:
```
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Trace-ID: 1-5e1b3c4d-5e6f7g8h9i0j1k2l3m4n5o6p
```

## References
- [Google API Design Guide](https://cloud.google.com/apis/design)
- [AWS API Gateway Best Practices](https://docs.aws.amazon.com/apigateway/latest/developerguide/best-practices.html)
- [gRPC Performance Best Practices](https://grpc.io/docs/guides/performance/)

---
**Date**: 2023-09-25  
**Author**: API Platform Team  
**Reviewed By**: CTO, Security Team, Frontend Team