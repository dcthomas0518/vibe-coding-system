# Vector Index Maintenance Protocol
*Version 1.0 | OS-002.1 Component | Last Updated: 2025-08-07*

## Overview

This protocol ensures the vector knowledge base remains current, accurate, and performant as organizational knowledge evolves. The system uses intelligent change detection to minimize reindexing overhead while maintaining <100ms query performance.

## Maintenance Strategy

### 1. Boot-Time Indexing (Primary)
**When**: Every session initialization via `claude_session_init.py`
**What**: Check and index changed HIGH PRIORITY files
**How**:
```python
# Automatically runs during boot
cd ~/vibe-coding-system/journey-capture
python3 claude_session_init.py
# This now includes vector indexing checks
```

### 2. On-Demand Reindexing
**When**: After major documentation updates or new content creation
**Command**:
```bash
cd ~/vibe-coding-system/os_modules/os_002_1_vector_search
python3 index_organizational_knowledge.py
```

### 3. Incremental Updates
**When**: Real-time as files are modified
**Mechanism**: MD5 hash comparison prevents redundant indexing

## File Priority Tiers

### Tier 1: HIGH PRIORITY (Check Every Boot)
- System instructions (CLAUDE.md files)
- Organizational structure documents
- Board protocols and minutes
- Agent definitions
- Active SPECs
- Strategic documents

**Update Frequency**: Every session start
**Performance Impact**: Minimal (<5 seconds)

### Tier 2: MEDIUM PRIORITY (Check Daily)
- Project context files
- Session logs
- Development documentation
- Journey capture files

**Update Frequency**: First boot of the day
**Performance Impact**: Low (<10 seconds)

### Tier 3: LOW PRIORITY (Check Weekly)
- Historical logs
- Sprint history
- Archive documents
- Reference materials

**Update Frequency**: Weekly maintenance window
**Performance Impact**: Moderate (<30 seconds)

## Change Detection System

### Hash-Based Detection
The system maintains a hash cache at `~/.vector_index_hashes.json`:
```json
{
  "/home/dthomas_unix/CLAUDE.md": "abc123...",
  "/home/dthomas_unix/organization/SUBAGENT_REGISTRY.md": "def456..."
}
```

**Process**:
1. Calculate MD5 hash of current file
2. Compare with cached hash
3. If different, reindex and update cache
4. If same, skip file

### Benefits:
- Only changed files are reindexed
- Preserves compute resources
- Maintains index freshness
- Fast boot times

## Integration Points

### 1. Boot Protocol Integration
Add to `claude_session_init.py`:
```python
# After loading organizational memory
from os_modules.os_002_1_vector_search.index_organizational_knowledge import (
    OrganizationalKnowledgeIndexer
)

# Quick index check for HIGH priority files only
indexer = OrganizationalKnowledgeIndexer()
high_priority_patterns = indexer.HIGH_PRIORITY_PATTERNS
# Index only changed files
for category, patterns in high_priority_patterns.items():
    files = indexer.expand_patterns(patterns)
    indexer.index_files(files, "HIGH", category)
```

### 2. Pre-Clear Protocol Integration
Before context clears, ensure index is current:
```bash
# Add to PRE_CLEAR_CHECKLIST.md
- [ ] Run vector index update for modified files
- [ ] Verify index integrity
- [ ] Document any indexing issues
```

### 3. Git Hook Integration
For automatic indexing on commits:
```bash
# .git/hooks/post-commit
#!/bin/bash
python3 ~/vibe-coding-system/os_modules/os_002_1_vector_search/index_organizational_knowledge.py
```

## Monitoring & Health Checks

### Daily Health Check
```python
# Test query performance
python3 -c "
from vector_search import VectorKnowledgeBase
import time
kb = VectorKnowledgeBase()
start = time.time()
results = kb.search('token thresholds', top_k=3)
elapsed = (time.time() - start) * 1000
print(f'Query time: {elapsed:.1f}ms')
assert elapsed < 100, 'Performance degradation detected!'
"
```

### Weekly Validation
Run test queries to ensure accuracy:
```bash
cd ~/vibe-coding-system/os_modules/os_002_1_vector_search
python3 index_organizational_knowledge.py --test
```

### Monthly Optimization
1. Review query logs for failed searches
2. Identify missing content patterns
3. Adjust chunking strategies
4. Update indexing priorities

## Troubleshooting Guide

### Issue: Slow Query Performance
**Symptoms**: Queries taking >100ms
**Solutions**:
1. Check index size: `du -sh ~/.chroma_db`
2. Rebuild index: `rm -rf ~/.chroma_db && python3 index_organizational_knowledge.py`
3. Verify embeddings model is loaded

### Issue: Missing Search Results
**Symptoms**: Known content not found
**Solutions**:
1. Check if file is in indexing patterns
2. Verify file has .md extension
3. Force reindex: Delete hash from `~/.vector_index_hashes.json`
4. Check file permissions

### Issue: Index Corruption
**Symptoms**: Errors when searching
**Solutions**:
```bash
# Complete rebuild
rm -rf ~/.chroma_db
rm ~/.vector_index_hashes.json
python3 index_organizational_knowledge.py
```

### Issue: Boot Time Degradation
**Symptoms**: Slow session initialization
**Solutions**:
1. Reduce HIGH PRIORITY file count
2. Move stable docs to MEDIUM priority
3. Implement async indexing

## Performance Metrics

### Target Metrics
- **Index Time**: <30 seconds for full index
- **Incremental Update**: <5 seconds for changed files
- **Query Response**: <100ms for 95% of queries
- **Index Size**: <100MB on disk
- **Memory Usage**: <200MB during indexing

### Monitoring Commands
```bash
# Check index size
du -sh ~/.chroma_db

# Count indexed documents
python3 -c "
from vector_search import VectorKnowledgeBase
kb = VectorKnowledgeBase()
print(f'Documents indexed: {kb.collection.count()}')
"

# View recent changes
tail ~/.vector_index_hashes.json
```

## Maintenance Schedule

### Continuous (Every Boot)
- [x] Index changed HIGH priority files
- [x] Update hash cache
- [x] Log indexing statistics

### Daily
- [ ] Full MEDIUM priority reindex
- [ ] Performance health check
- [ ] Query accuracy spot check

### Weekly
- [ ] LOW priority content review
- [ ] Failed query analysis
- [ ] Index optimization check

### Monthly
- [ ] Complete index rebuild
- [ ] Pattern review and updates
- [ ] Performance trend analysis
- [ ] Storage cleanup

## Automation Scripts

### Auto-Index on File Save (VSCode)
```json
// .vscode/settings.json
{
  "runOnSave.commands": [
    {
      "match": ".*\\.md$",
      "command": "cd ${workspaceFolder}/os_modules/os_002_1_vector_search && python3 index_organizational_knowledge.py",
      "runIn": "terminal"
    }
  ]
}
```

### Cron Job for Daily Updates
```bash
# Add to crontab -e
0 6 * * * cd /home/dthomas_unix/vibe-coding-system/os_modules/os_002_1_vector_search && python3 index_organizational_knowledge.py >> /tmp/vector_index.log 2>&1
```

## Success Indicators

### Green Flags ✅
- All test queries return results <100ms
- Hash cache prevents redundant indexing
- Index size remains stable (<100MB)
- No timeout errors in search
- Boot indexing completes <5 seconds

### Warning Signs ⚠️
- Query times approaching 100ms
- Index size growing rapidly
- Frequent reindexing of same files
- Memory usage during indexing >500MB

### Red Flags 🚨
- Query timeouts
- Index corruption errors
- Boot indexing >30 seconds
- Missing critical documents in search

## Conclusion

This maintenance protocol ensures the vector knowledge base remains the authoritative source for instant organizational knowledge retrieval. By following these procedures, we maintain Dale's vision of zero amnesia with <100ms access to any organizational knowledge.

**Remember**: The goal is instant, accurate answers to any question about how our organization works, what we've decided, and why we've made those choices.

---
*Protocol approved by: Pompey (CTO)*
*Next review date: 2025-09-07*