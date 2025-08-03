# ADR-004: Security and Privacy Architecture

## Status
Accepted

## Context
As we collect and process user behavior data, we must:
- Comply with GDPR, CCPA, and other privacy regulations
- Protect sensitive user information
- Prevent data breaches and unauthorized access
- Enable user rights (access, deletion, portability)
- Maintain audit trails for compliance
- Balance privacy with analytics needs

Key requirements:
- PII must be encrypted at rest and in transit
- Users must be able to request data deletion
- Data retention must be configurable per region
- Access must be role-based and audited

## Decision
We will implement a privacy-first architecture with:

1. **Data Minimization**: Collect only necessary data
2. **Encryption Everywhere**: AES-256 at rest, TLS 1.3 in transit
3. **Pseudonymization**: Replace PII with hashed identifiers
4. **Consent Management**: Explicit consent tracking
5. **Zero Trust Security**: Assume breach, verify everything
6. **Privacy by Design**: Built-in, not bolted-on

## Consequences

### Positive
- Regulatory compliance by default
- Reduced risk of data breaches
- User trust and transparency
- Simplified audit processes
- Competitive advantage through privacy

### Negative
- Increased system complexity
- Higher computational costs
- Potential impact on analytics capabilities
- Additional development effort
- Ongoing compliance overhead

## Implementation Details

### Data Classification

**Sensitivity Levels**:
```yaml
PUBLIC:
  - Page URLs (without query params)
  - Event types
  - Timestamps
  
INTERNAL:
  - Session IDs
  - Device information
  - Geographic data (country/region)
  
CONFIDENTIAL:
  - User IDs
  - IP addresses
  - Detailed geographic data
  
RESTRICTED:
  - Email addresses
  - Payment information
  - Any direct PII
```

### Encryption Strategy

**At Rest**:
```python
# KMS key hierarchy
Root KMS Key (Hardware Security Module)
  └── Data Encryption Key (DEK) - Rotated monthly
      └── Field-level encryption keys - Per sensitive field

# S3 encryption
aws s3api put-bucket-encryption \
  --bucket company-events-prod \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:region:account:key/xxx"
      }
    }]
  }'
```

**In Transit**:
- TLS 1.3 minimum for all connections
- Certificate pinning for mobile SDKs
- mTLS for service-to-service communication

### PII Handling

**Pseudonymization Pipeline**:
```python
def pseudonymize_user_data(event):
    # Hash user ID with salt
    user_salt = get_user_salt(event['user_id'])
    event['user_id'] = hashlib.sha256(
        f"{event['user_id']}{user_salt}".encode()
    ).hexdigest()
    
    # Tokenize email if present
    if 'email' in event:
        event['email_token'] = tokenize_email(event['email'])
        del event['email']
    
    # Reduce IP precision
    if 'ip_address' in event:
        event['ip_country'] = get_country(event['ip_address'])
        event['ip_hash'] = hash_ip(event['ip_address'])
        del event['ip_address']
    
    return event
```

**Tokenization Service**:
```yaml
Service: PII Tokenization Vault
Storage: Separate encrypted database
Access: Restricted API with audit logging
Retention: Configurable per data type
```

### Consent Management

**Consent Tracking**:
```sql
CREATE TABLE user_consent (
    user_id UUID PRIMARY KEY,
    analytics_consent BOOLEAN DEFAULT FALSE,
    marketing_consent BOOLEAN DEFAULT FALSE,
    consent_timestamp TIMESTAMP NOT NULL,
    consent_version VARCHAR(10) NOT NULL,
    ip_country VARCHAR(2),
    withdrawal_timestamp TIMESTAMP
);

-- Audit all consent changes
CREATE TABLE consent_audit (
    audit_id UUID DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL,
    previous_state JSONB,
    new_state JSONB,
    timestamp TIMESTAMP DEFAULT NOW(),
    source VARCHAR(50)
);
```

**Consent Enforcement**:
```javascript
// SDK implementation
class Analytics {
  async track(event) {
    const consent = await this.getConsent();
    
    if (!consent.analytics) {
      // Only track anonymous, necessary data
      return this.trackMinimal(event);
    }
    
    // Full tracking with consent
    return this.trackFull(event);
  }
  
  trackMinimal(event) {
    // Remove all PII
    const minimal = {
      event_type: event.type,
      timestamp: event.timestamp,
      page_category: this.categorizeUrl(event.url),
      session_id: this.hashSession(event.session)
    };
    return this.send(minimal);
  }
}
```

### Access Control

**IAM Role Structure**:
```yaml
Roles:
  DataScientist:
    - Read anonymized data
    - No PII access
    - Time-limited queries
    
  DataEngineer:
    - Read/write pipeline access
    - No direct PII access
    - Audit logged
    
  PrivacyOfficer:
    - User data export
    - Deletion requests
    - Consent management
    
  SecurityAdmin:
    - Full audit access
    - Key management
    - Access control
```

**Zero Trust Implementation**:
```python
# Every service call requires authentication
@require_auth
@validate_permissions
@audit_log
def access_user_data(user_id, requester):
    # Verify purpose
    if not has_valid_purpose(requester):
        raise UnauthorizedError("No valid purpose")
    
    # Check data minimization
    fields = get_allowed_fields(requester.role)
    
    # Time-based access
    if not within_access_window(requester):
        raise UnauthorizedError("Outside access window")
    
    # Return only permitted data
    return fetch_user_data(user_id, fields)
```

### Data Rights Implementation

**Right to Access**:
```python
def export_user_data(user_id):
    # Collect from all systems
    data = {
        'profile': get_profile_data(user_id),
        'events': get_event_history(user_id),
        'consents': get_consent_history(user_id),
        'processing': get_processing_purposes(user_id)
    }
    
    # Package securely
    encrypted = encrypt_for_user(data, user_id)
    signed_url = generate_download_url(encrypted)
    
    # Audit
    log_data_export(user_id, requester)
    
    return signed_url
```

**Right to Deletion**:
```python
def delete_user_data(user_id, verification_token):
    # Verify request
    if not verify_deletion_request(user_id, verification_token):
        raise InvalidRequestError()
    
    # Create deletion job
    job = DeletionJob(
        user_id=user_id,
        systems=['dynamodb', 's3', 'redshift'],
        retention_override=get_legal_holds(user_id)
    )
    
    # Execute with confirmation
    results = job.execute()
    
    # Maintain deletion record
    record_deletion(user_id, results)
    
    return results
```

### Security Monitoring

**Threat Detection**:
```yaml
CloudWatch Rules:
  - Multiple failed auth attempts
  - Unusual data access patterns
  - Geographic anomalies
  - Privilege escalation attempts
  
GuardDuty:
  - Cryptocurrency mining
  - Malicious IP communication
  - Compromised credentials
  
Macie:
  - PII in wrong locations
  - Unencrypted sensitive data
  - Policy violations
```

**Incident Response**:
```python
class SecurityIncidentHandler:
    def handle_data_breach(self, incident):
        # 1. Contain
        self.isolate_affected_systems(incident.systems)
        self.revoke_compromised_credentials(incident.credentials)
        
        # 2. Assess
        impact = self.assess_data_impact(incident)
        affected_users = self.identify_affected_users(impact)
        
        # 3. Notify
        if self.requires_notification(impact):
            self.notify_authorities(impact)  # Within 72 hours
            self.notify_users(affected_users)
        
        # 4. Remediate
        self.patch_vulnerabilities(incident.vulnerabilities)
        self.strengthen_controls(incident.attack_vector)
```

### Compliance Automation

**Automated Compliance Checks**:
```python
# Daily compliance validation
def validate_compliance():
    checks = {
        'encryption': validate_encryption_everywhere(),
        'retention': validate_retention_policies(),
        'access': validate_access_controls(),
        'consent': validate_consent_enforcement(),
        'audit': validate_audit_completeness()
    }
    
    report = generate_compliance_report(checks)
    
    if report.has_violations():
        alert_compliance_team(report)
        initiate_remediation(report.violations)
    
    store_compliance_record(report)
```

## Privacy-Preserving Analytics

**Differential Privacy**:
```python
def add_differential_privacy(query_result, epsilon=1.0):
    # Add calibrated noise to preserve privacy
    sensitivity = calculate_sensitivity(query_result)
    noise = numpy.random.laplace(0, sensitivity/epsilon)
    
    private_result = query_result + noise
    
    # Ensure non-negative
    return max(0, private_result)
```

**K-Anonymity**:
```sql
-- Ensure no group has fewer than K users
CREATE VIEW anonymous_events AS
SELECT 
    DATE_TRUNC('hour', event_timestamp) as hour,
    SUBSTRING(ip_hash, 1, 8) as ip_prefix,
    event_type,
    COUNT(*) as event_count
FROM events
GROUP BY 1, 2, 3
HAVING COUNT(DISTINCT user_id) >= 5;  -- K=5
```

## Testing and Validation

**Security Testing**:
- Penetration testing quarterly
- Automated vulnerability scanning
- Static code analysis
- Dependency scanning
- Compliance validation

**Privacy Testing**:
```python
def test_pii_leakage():
    # Send event with PII
    test_event = create_test_event_with_pii()
    processed = process_event(test_event)
    
    # Verify no PII in output
    assert not contains_email(processed)
    assert not contains_ip(processed)
    assert is_properly_hashed(processed['user_id'])
```

## References
- [GDPR Compliance Guide](https://gdpr.eu/)
- [NIST Privacy Framework](https://www.nist.gov/privacy-framework)
- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---
**Date**: 2023-10-01  
**Author**: Security Team  
**Reviewed By**: CTO, Legal, Privacy Officer