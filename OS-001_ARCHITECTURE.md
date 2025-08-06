# OS-001: Organizational Memory System Architecture

## Executive Summary

The Organizational Memory System (OMS) provides persistent context management across Claude sessions, enabling seamless continuity for health journey tracking and other long-term conversations. Built on a zero-cost stack (ChromaDB + Google Drive + SQLite), it achieves <30 second context loads while maintaining API-first design for future MCP integration.

## Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
├─────────────────────────────────────┬───────────────────────────┤
│        Claude Desktop               │      Future MCP Clients    │
│    (Primary Interface)              │    (API Consumption)       │
└────────────────┬────────────────────┴────────────┬──────────────┘
                 │                                 │
┌────────────────▼─────────────────────────────────▼──────────────┐
│                         API Gateway                              │
│                    FastAPI REST Service                          │
│              /api/v1/memory/* endpoints                          │
└────────────────┬─────────────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────────────┐
│                    Memory Service Layer                          │
├─────────────────┬──────────────────┬────────────────────────────┤
│  Context Manager│  Journey Tracker  │   Search Engine           │
│  (Load/Save)    │  (Health Events)  │   (Semantic + Full-text) │
└─────────────────┴──────────────────┴────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────────────┐
│                    Storage Abstraction Layer                     │
├──────────────┬──────────────────┬─────────────────────────────┤
│   Metadata   │   Vector Store   │    Document Store           │
│   (SQLite)   │   (ChromaDB)     │    (Google Drive)           │
└──────────────┴──────────────────┴─────────────────────────────┘
```

## Component Design

### 1. API Gateway (FastAPI)

**Purpose**: RESTful interface for all memory operations

**Key Endpoints**:
```
POST   /api/v1/memory/context/save
GET    /api/v1/memory/context/load/{session_id}
POST   /api/v1/memory/journey/event
GET    /api/v1/memory/journey/timeline
POST   /api/v1/memory/search
GET    /api/v1/memory/health
```

**Design Decisions**:
- Async/await for non-blocking I/O
- Request validation with Pydantic models
- JWT authentication ready (disabled for Phase 1)
- OpenAPI documentation auto-generated
- CORS configured for local Claude Desktop

### 2. Context Manager

**Purpose**: Orchestrates context persistence and retrieval

**Key Features**:
- Intelligent context summarization
- Delta compression for incremental updates
- Priority-based loading (most relevant first)
- Context size management (token counting)

**Data Model**:
```python
class Context:
    session_id: str
    timestamp: datetime
    summary: str  # AI-generated summary
    full_content: str  # Complete conversation
    embeddings: List[float]  # For semantic search
    metadata: Dict[str, Any]  # Tags, categories, etc.
    token_count: int
    priority_score: float  # Relevance scoring
```

### 3. Journey Tracker

**Purpose**: Specialized health event tracking with temporal awareness

**Event Types**:
- Symptoms reported
- Treatments discussed
- Progress milestones
- Provider interactions
- Medication changes

**Data Model**:
```python
class JourneyEvent:
    event_id: str
    timestamp: datetime
    event_type: EventType
    description: str
    severity: Optional[int]  # 1-10 scale
    related_events: List[str]  # Event linking
    attachments: List[str]  # Document references
    tags: List[str]
```

### 4. Storage Layer

#### SQLite (Metadata Store)
- Session metadata
- Journey events
- Search indices
- Configuration
- Performance metrics

**Schema**:
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    summary TEXT,
    token_count INTEGER,
    priority_score REAL,
    tags TEXT  -- JSON array
);

CREATE TABLE journey_events (
    event_id TEXT PRIMARY KEY,
    session_id TEXT,
    timestamp TIMESTAMP,
    event_type TEXT,
    description TEXT,
    severity INTEGER,
    metadata TEXT  -- JSON
);

CREATE INDEX idx_sessions_updated ON sessions(updated_at);
CREATE INDEX idx_events_timestamp ON journey_events(timestamp);
```

#### ChromaDB (Vector Store)
- Conversation embeddings
- Semantic search capabilities
- Similarity matching
- Context clustering

**Collection Structure**:
```python
collection = {
    "name": "conversation_memory",
    "metadata": {"hnsw:space": "cosine"},
    "embedding_function": "sentence-transformers/all-MiniLM-L6-v2"
}
```

#### Google Drive (Document Store)
- Full conversation archives
- Large attachments
- Backup redundancy
- Version history

**Folder Structure**:
```
/OMS_Storage/
├── contexts/
│   ├── 2024/
│   │   ├── 01/
│   │   │   └── session_abc123.json
│   │   └── 02/
│   └── current/
│       └── active_session.json
├── journeys/
│   └── health/
│       └── events.jsonl
└── backups/
    └── daily/
```

## Data Flow Diagram

### Context Save Flow
```
1. Claude Session → API POST /context/save
2. API → Context Manager: Process conversation
3. Context Manager → Summarizer: Generate summary
4. Context Manager → Embedder: Create vectors
5. Parallel writes:
   a. SQLite: Metadata + indices
   b. ChromaDB: Embeddings
   c. Google Drive: Full content
6. API → Claude: Confirmation + session_id
```

### Context Load Flow (<30s target)
```
1. Claude Startup → API GET /context/load
2. API → SQLite: Recent sessions query (< 100ms)
3. API → ChromaDB: Similarity search (< 1s)
4. API → Priority Ranker: Score contexts
5. API → Google Drive: Fetch top N contexts (< 10s)
6. API → Assembler: Build coherent narrative
7. API → Claude: Structured context response
```

### Journey Search Flow
```
1. Query: "headaches in January"
2. API → Parser: Extract time + symptom
3. Parallel search:
   a. SQLite: Date range filter
   b. ChromaDB: Semantic "headache" search
4. API → Merger: Combine results
5. API → Ranker: Score by relevance
6. API → Response: Timeline view
```

## Performance Strategy

### 1. Cold Start Optimization (<30s)

**Techniques**:
- **Lazy Loading**: Start with metadata, fetch content on-demand
- **Progressive Enhancement**: Return partial results immediately
- **Smart Caching**: LRU cache for recent contexts
- **Parallel I/O**: Concurrent storage queries
- **Pre-warming**: Background refresh of likely contexts

**Implementation**:
```python
async def fast_load_context(session_id: Optional[str] = None):
    # Step 1: Quick metadata (< 100ms)
    metadata = await sqlite.get_recent_sessions(limit=10)
    
    # Step 2: Return preview immediately
    yield {"preview": metadata, "status": "loading"}
    
    # Step 3: Parallel fetch (< 5s)
    context_tasks = [
        chromadb.search_similar(session_id),
        gdrive.fetch_recent(metadata.ids)
    ]
    contexts = await asyncio.gather(*context_tasks)
    
    # Step 4: Stream results as ready
    for ctx in contexts:
        yield {"context": ctx, "status": "partial"}
    
    # Step 5: Final assembly (< 2s)
    final = await assemble_narrative(contexts)
    yield {"context": final, "status": "complete"}
```

### 2. Storage Optimization

**SQLite**:
- WAL mode for concurrent reads
- Prepared statements
- Connection pooling
- Index optimization

**ChromaDB**:
- Batch insertions
- Appropriate embedding dimensions
- HNSW tuning for recall/speed
- Periodic compaction

**Google Drive**:
- Resumable uploads
- Batch operations API
- Exponential backoff
- Local cache for hot data

### 3. Caching Strategy

**Multi-tier Cache**:
```
L1: In-memory LRU (last 5 sessions) - < 1ms
L2: Local disk cache (last 50 sessions) - < 10ms  
L3: Full storage fetch - < 30s
```

**Cache Invalidation**:
- TTL-based expiry (24 hours)
- Event-based updates
- Manual refresh option

## Phase 1 Implementation Plan

### Week 1: Foundation
- [ ] Set up project structure
- [ ] Implement SQLite schema
- [ ] Create base API endpoints
- [ ] Simple save/load functionality

### Week 2: Storage Integration  
- [ ] ChromaDB setup and embedding pipeline
- [ ] Google Drive API integration
- [ ] Basic search functionality
- [ ] Error handling and retries

### Week 3: Performance
- [ ] Implement caching layers
- [ ] Add async/streaming responses
- [ ] Optimize query patterns
- [ ] Load testing < 30s

### Week 4: Journey Features
- [ ] Journey event models
- [ ] Timeline visualization API
- [ ] Health-specific search
- [ ] Basic analytics

### Week 5: Polish & Testing
- [ ] Comprehensive error handling
- [ ] API documentation
- [ ] Integration tests
- [ ] Performance benchmarks
- [ ] Deployment scripts

## Security Considerations

### Phase 1 (Local Only)
- File system permissions
- Local API binding only
- No authentication required
- Data encryption at rest (optional)

### Future Phases
- JWT authentication
- API key management  
- TLS for API endpoints
- Google Drive OAuth2
- Data anonymization options

## Monitoring & Observability

### Metrics to Track
- Context load time (p50, p95, p99)
- Storage operation latency
- Cache hit rates
- API request duration
- Error rates by component

### Logging Strategy
```python
logger.info("context_load", {
    "session_id": session_id,
    "duration_ms": duration,
    "contexts_loaded": len(contexts),
    "cache_hit": cache_hit,
    "storage_calls": storage_calls
})
```

## Future Extensibility

### MCP Integration Points
- Standardized API contracts
- Plugin architecture for storage backends
- Event streaming for real-time sync
- Federation support for multi-instance

### Potential Enhancements
- Multi-user support
- Collaborative memory sharing
- Advanced NLP summarization
- Predictive context pre-loading
- Mobile companion app

## Success Criteria

1. **Performance**: Cold start < 30 seconds consistently
2. **Reliability**: 99.9% uptime for local instance
3. **Usability**: Zero friction context persistence
4. **Scalability**: Handles 1000+ sessions efficiently
5. **Extensibility**: Clean API for MCP integration

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Google Drive API limits | High | Local cache, exponential backoff |
| ChromaDB scaling | Medium | Pagination, collection sharding |
| Large context sizes | High | Compression, summarization |
| Data corruption | High | Checksums, backup strategy |
| Slow embeddings | Medium | Batch processing, smaller models |