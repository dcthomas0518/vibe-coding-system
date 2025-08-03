# User Behavior Data Pipeline API Documentation

## Overview

The User Behavior Data Pipeline provides a high-performance, scalable API for ingesting user behavior events in real-time. This API supports various event types including page views, clicks, form interactions, and custom events, enabling comprehensive user behavior analytics.

## Base URL

```
Production: https://api.analytics.company.com/v1
Staging: https://api-staging.analytics.company.com/v1
```

## Authentication

### API Key Authentication

All requests must include an API key in the header:

```
X-API-Key: your_api_key_here
```

### Client SDK Authentication

For browser-based implementations, use the JavaScript SDK with a public key:

```javascript
Analytics.init({
  publicKey: 'pk_live_xxxxxxxxxxxxx',
  endpoint: 'https://api.analytics.company.com/v1'
});
```

## Rate Limiting

- **Standard tier**: 1,000 requests per minute per API key
- **Enterprise tier**: 10,000 requests per minute per API key
- **Burst capacity**: 2x sustained rate for 60 seconds

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Data Ingestion Endpoints

### 1. Send Single Event

**POST** `/events`

Ingest a single user behavior event.

#### Request Headers
```
Content-Type: application/json
X-API-Key: your_api_key_here
```

#### Request Body
```json
{
  "event_type": "page_view",
  "event_timestamp": "2024-01-15T10:30:00.000Z",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_123456",
  "device": {
    "device_id": "device_abc123",
    "device_type": "mobile",
    "os": "iOS",
    "os_version": "17.0",
    "browser": "Safari",
    "browser_version": "17.0"
  },
  "page": {
    "url": "https://example.com/products/123",
    "path": "/products/123",
    "title": "Product Details - Widget Pro",
    "referrer": "https://example.com/search"
  },
  "event_properties": {
    "load_time_ms": 245,
    "product_id": "123",
    "category": "electronics"
  }
}
```

#### Response (200 OK)
```json
{
  "event_id": "evt_2024011510300000123",
  "status": "accepted",
  "timestamp": "2024-01-15T10:30:00.123Z"
}
```

#### Error Responses

**400 Bad Request**
```json
{
  "error": {
    "code": "INVALID_EVENT",
    "message": "Invalid event data",
    "details": {
      "event_type": "Event type is required",
      "event_timestamp": "Timestamp must be in ISO 8601 format"
    }
  }
}
```

**401 Unauthorized**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing API key"
  }
}
```

**429 Too Many Requests**
```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded",
    "retry_after": 60
  }
}
```

### 2. Send Batch Events

**POST** `/events/batch`

Ingest multiple events in a single request. Maximum 500 events per batch.

#### Request Body
```json
{
  "events": [
    {
      "event_type": "page_view",
      "event_timestamp": "2024-01-15T10:30:00.000Z",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user_123456",
      "page": {
        "url": "https://example.com/home",
        "title": "Home Page"
      }
    },
    {
      "event_type": "click",
      "event_timestamp": "2024-01-15T10:30:05.000Z",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user_123456",
      "event_properties": {
        "element_id": "btn-signup",
        "element_text": "Sign Up Now",
        "position": {
          "x": 450,
          "y": 320
        }
      }
    }
  ]
}
```

#### Response (200 OK)
```json
{
  "batch_id": "batch_2024011510300000456",
  "status": "accepted",
  "events_received": 2,
  "events_accepted": 2,
  "events_rejected": 0,
  "timestamp": "2024-01-15T10:30:00.456Z"
}
```

#### Response with Partial Failures (207 Multi-Status)
```json
{
  "batch_id": "batch_2024011510300000789",
  "status": "partial",
  "events_received": 3,
  "events_accepted": 2,
  "events_rejected": 1,
  "errors": [
    {
      "index": 2,
      "error": {
        "code": "INVALID_EVENT",
        "message": "Missing required field: event_type"
      }
    }
  ]
}
```

### 3. Send Beacon Event

**POST** `/events/beacon`

Lightweight endpoint optimized for sendBeacon API. Accepts URL-encoded data.

#### Request
```
POST /events/beacon
Content-Type: application/x-www-form-urlencoded

event_type=page_exit&session_id=550e8400&page_url=https://example.com&time_on_page=45
```

#### Response (204 No Content)
No response body. Success indicated by 204 status code.

## Event Types Reference

### Core Events

#### page_view
Triggered when a user views a page.

```json
{
  "event_type": "page_view",
  "event_properties": {
    "load_time_ms": 245,
    "first_contentful_paint": 180,
    "dom_ready": 220
  }
}
```

#### click
User clicks on an element.

```json
{
  "event_type": "click",
  "event_properties": {
    "element_id": "btn-purchase",
    "element_class": "cta-button primary",
    "element_text": "Buy Now",
    "element_tag": "button",
    "position": {
      "x": 450,
      "y": 320,
      "viewport_x": 450,
      "viewport_y": 200
    }
  }
}
```

#### scroll
Scroll behavior tracking.

```json
{
  "event_type": "scroll",
  "event_properties": {
    "scroll_depth": 75,
    "scroll_velocity": 150,
    "viewport_height": 800,
    "page_height": 3200,
    "direction": "down"
  }
}
```

#### form_submit
Form submission events.

```json
{
  "event_type": "form_submit",
  "event_properties": {
    "form_id": "contact-form",
    "form_name": "Contact Us",
    "fields_count": 5,
    "submission_time_ms": 15420,
    "validation_errors": []
  }
}
```

### E-commerce Events

#### product_view
```json
{
  "event_type": "product_view",
  "event_properties": {
    "product_id": "SKU-12345",
    "product_name": "Wireless Headphones",
    "product_category": "Electronics",
    "price": 99.99,
    "currency": "USD"
  }
}
```

#### add_to_cart
```json
{
  "event_type": "add_to_cart",
  "event_properties": {
    "product_id": "SKU-12345",
    "quantity": 2,
    "price": 99.99,
    "cart_value": 249.97
  }
}
```

#### purchase
```json
{
  "event_type": "purchase",
  "event_properties": {
    "order_id": "ORD-789456",
    "revenue": 249.97,
    "tax": 24.50,
    "shipping": 9.99,
    "currency": "USD",
    "products": [
      {
        "product_id": "SKU-12345",
        "quantity": 2,
        "price": 99.99
      }
    ]
  }
}
```

### Custom Events

#### custom
For application-specific events.

```json
{
  "event_type": "custom",
  "event_properties": {
    "custom_event_name": "video_milestone",
    "video_id": "vid_123",
    "milestone": "50_percent",
    "duration_watched": 120
  }
}
```

## SDK Integration

### JavaScript SDK

#### Installation
```html
<script>
(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://cdn.analytics.company.com/analytics.min.js';
f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','analytics');

analytics('init', 'pk_live_xxxxxxxxxxxxx');
</script>
```

#### Basic Usage
```javascript
// Track page view
analytics.page();

// Track custom event
analytics.track('button_clicked', {
  button_id: 'header-cta',
  button_text: 'Get Started'
});

// Identify user
analytics.identify('user_123456', {
  email: 'user@example.com',
  plan: 'premium'
});
```

#### Advanced Configuration
```javascript
analytics.init({
  publicKey: 'pk_live_xxxxxxxxxxxxx',
  endpoint: 'https://api.analytics.company.com/v1',
  batchSize: 50,
  flushInterval: 5000,
  enableCookies: true,
  trackingOptions: {
    ip: false,
    geolocation: true,
    deviceInfo: true
  },
  onError: function(error) {
    console.error('Analytics error:', error);
  }
});
```

### Server-side SDKs

#### Python
```python
from analytics import Client

client = Client(api_key="sk_live_xxxxxxxxxxxxx")

# Track event
client.track(
    user_id="user_123456",
    event="Order Completed",
    properties={
        "order_id": "ORD-789456",
        "revenue": 249.97
    }
)

# Flush events
client.flush()
```

#### Node.js
```javascript
const Analytics = require('analytics-node');
const analytics = new Analytics('sk_live_xxxxxxxxxxxxx');

// Track event
analytics.track({
  userId: 'user_123456',
  event: 'Order Completed',
  properties: {
    order_id: 'ORD-789456',
    revenue: 249.97
  }
});

// Flush events
await analytics.flush();
```

## Data Validation

### Required Fields

All events must include:
- `event_type`: String, valid event type
- `event_timestamp`: ISO 8601 timestamp
- `session_id`: UUID format

### Field Constraints

| Field | Type | Max Length | Format |
|-------|------|------------|--------|
| event_type | string | 50 | alphanumeric + underscore |
| user_id | string | 255 | any |
| session_id | string | 36 | UUID |
| device_id | string | 255 | any |
| url | string | 2048 | valid URL |
| custom properties | string | 1000 | any |
| numeric properties | number | - | float64 |

### Timestamp Requirements

- Must be in ISO 8601 format with timezone
- Cannot be more than 7 days in the past
- Cannot be more than 1 hour in the future

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Specific field error"
    },
    "request_id": "req_xxxxxxxxxxxxx"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_EVENT | 400 | Event data validation failed |
| MISSING_FIELD | 400 | Required field is missing |
| INVALID_FORMAT | 400 | Field format is invalid |
| UNAUTHORIZED | 401 | Missing or invalid API key |
| FORBIDDEN | 403 | API key lacks permission |
| NOT_FOUND | 404 | Endpoint not found |
| RATE_LIMITED | 429 | Rate limit exceeded |
| PAYLOAD_TOO_LARGE | 413 | Request body exceeds limit |
| INTERNAL_ERROR | 500 | Server error |
| SERVICE_UNAVAILABLE | 503 | Temporary service issue |

### Retry Strategy

For 5xx errors and 429 (rate limited):
- Use exponential backoff: 1s, 2s, 4s, 8s, 16s
- Add jitter: ±20% random delay
- Maximum 5 retry attempts
- Honor `Retry-After` header

## Best Practices

### 1. Batching Events

Batch events to improve performance:
- Client-side: Batch up to 50 events or 5 seconds
- Server-side: Batch up to 500 events or 100KB

### 2. Session Management

- Generate session ID on first page view
- Expire sessions after 30 minutes of inactivity
- Store session ID in localStorage or cookie

### 3. User Identification

- Use consistent user IDs across platforms
- Hash emails before sending: `sha256(email.toLowerCase())`
- Implement proper consent management

### 4. Error Recovery

```javascript
// Example retry logic
async function sendEventWithRetry(event, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await sendEvent(event);
    } catch (error) {
      if (error.status >= 500 || error.status === 429) {
        const delay = Math.pow(2, i) * 1000;
        await sleep(delay);
        continue;
      }
      throw error;
    }
  }
  throw new Error('Max retries exceeded');
}
```

### 5. Data Quality

- Validate events client-side before sending
- Implement sampling for high-volume events
- Use consistent naming conventions
- Document custom event schemas

## API Changelog

### v1.2.0 (2024-01-15)
- Added beacon endpoint for lightweight tracking
- Increased batch size limit to 500 events
- Added support for custom event properties

### v1.1.0 (2023-11-01)
- Added e-commerce event types
- Improved error response details
- Added rate limit headers

### v1.0.0 (2023-09-01)
- Initial release
- Core event tracking
- Batch API support