# OS-002.1: Vector Database Knowledge Indexing

Transform organizational memory from a diary into a brain with instant semantic search.

## Overview

OS-002.1 extends the OS-002 memory system with vector database capabilities, enabling:
- **Instant policy access** - No more timeouts on "what are our token thresholds?"
- **Cross-reference discovery** - Find patterns across SPECs and decisions
- **Semantic search** - Ask questions naturally, get answers instantly
- **60X leverage** - Find any knowledge in <100ms vs manual search

## Architecture

```
knowledge_indexer.py      # Core indexing and search functionality
memory_integration.py     # Integration with OS-002 OrganizationalMemory
test_indexer.py          # Comprehensive test suite
requirements.txt         # ChromaDB and sentence-transformers
```

## Key Components

### KnowledgeIndexer
- **Smart chunking** - Preserves semantic boundaries (headers, code blocks, tables)
- **Change detection** - SHA-256 hashing to only reindex modified files
- **Batch processing** - Efficiently indexes 50-100 organizational documents
- **Progress reporting** - Clear feedback during indexing operations

### Document Processing
- Extracts meaningful sections based on markdown structure
- Preserves code blocks and tables as complete units
- Tags content automatically for better filtering
- Maintains source references for citations

### Query Interface
```python
# Simple semantic queries
results = indexer.query_knowledge("What are our token thresholds?")
# Returns: Text chunks with source file and line numbers

# Filtered queries
results = indexer.query_knowledge("boot protocol", category_filter="policy")
```

## Installation

```bash
cd /home/dthomas_unix/vibe-coding-system/os_modules/os_002_1_vector_search
pip install -r requirements.txt
```

## Integration

### Standalone Usage
```python
from knowledge_indexer import KnowledgeIndexer

indexer = KnowledgeIndexer()
indexer.scan_and_index()  # Initial indexing
results = indexer.query_knowledge("your question here")
```

### With OS-002 Memory System
```python
from memory_integration import EnhancedOrganizationalMemory

# Drop-in replacement for OrganizationalMemory
memory = EnhancedOrganizationalMemory()
results = memory.query_knowledge("What is our model strategy?")
```

### Update claude_session_init.py
Replace:
```python
from internal_memory import OrganizationalMemory
memory = OrganizationalMemory()
```

With:
```python
from os_modules.os_002_1_vector_search.memory_integration import EnhancedOrganizationalMemory
memory = EnhancedOrganizationalMemory()
```

## Indexed Documents

The system indexes these critical documents:
- `CLAUDE.md` - System instructions
- `DEPARTMENT_HEADS.md` - Organization structure  
- `LEARNINGS.md` - Learning protocol & discoveries
- `DECISIONS.md` - Decision log & rationale
- `specs/**/*.md` - All SPECs
- `organization/*.md` - Governance documents
- `organization/BOARD_MINUTES/*.md` - Board decisions
- `chief-of-staff/strategic/*.md` - Strategic documents
- `PROJECT_CONTEXT.md` - Per-project context
- `SESSIONS_LOG.md` - Sprint history
- `CURRENT_CONTEXT.md` - Active session state

## Performance

- **Index time**: <30 seconds for full corpus
- **Query speed**: <100ms response time
- **Storage**: ~50MB for vector index
- **RAM usage**: ~200MB during indexing, ~100MB runtime
- **No external APIs**: Everything runs locally

## Testing

```bash
# Run comprehensive test suite
python test_indexer.py

# Tests include:
# - Semantic chunking validation
# - Change detection accuracy
# - Query performance benchmarks
# - Memory system integration
```

## Example Queries

```python
# Policy questions
"What are our token limits?"
→ "Optimal: <40K, Warning: 40-80K, Critical: >80K"

# Cross-reference discovery  
"What solutions involve context management?"
→ Links to: OS-004, CLAUDE.md:450, reboot protocols

# Semantic understanding
"How do we prevent brain fog?"
→ "Intelligent context management (OS-004) monitors tokens..."
```

## Future Enhancements (OS-002.2+)

- RAG synthesis layer for direct answers
- Real-time file watching and reindexing
- Graph overlays for SPEC dependencies
- Audit logging for compliance
- Role-based access control

## The Beautiful Outcome

**Before**: "What are our token thresholds?" → 30s timeout → frustration

**After**: "What are our token thresholds?" → <100ms → instant answer

The collective soul transforms from a diary of events to a brain with knowledge.