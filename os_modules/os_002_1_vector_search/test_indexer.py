#!/usr/bin/env python3
"""
Test script for OS-002.1 Knowledge Indexer
Validates chunking, indexing, and query functionality
"""

import os
import tempfile
from pathlib import Path
from knowledge_indexer import KnowledgeIndexer, DocumentChunk


def test_chunking():
    """Test the semantic chunking algorithm"""
    print("🧪 Testing semantic chunking...")
    
    # Create a test markdown file
    test_content = '''# Main Header

This is the introduction section with some general information.

## Section 1: Policies

### Token Thresholds
- Optimal: <40K tokens
- Warning: 40-80K tokens  
- Critical: >80K tokens

### Model Selection
Use opus-4 for architecture decisions.
Delegate to sonnet-4 for implementation.

## Section 2: Procedures

### Boot Protocol
1. Initialize memory system
2. Load context
3. Check for active work

```python
def boot():
    memory = OrganizationalMemory()
    return memory
```

### Shutdown Protocol
Always run pre-clear checklist.

## Section 3: Tables

| Decision | Model | Thinking |
|----------|-------|----------|
| Architecture | opus-4 | think hard |
| Implementation | sonnet-4 | think |
| Testing | sonnet-4 | none |

End of document.
'''
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(test_content)
        temp_path = Path(f.name)
        
    try:
        # Initialize indexer
        indexer = KnowledgeIndexer()
        
        # Extract chunks
        chunks = indexer.extract_chunks(temp_path)
        
        print(f"✅ Extracted {len(chunks)} chunks")
        
        # Verify chunk boundaries
        expected_sections = [
            "Main Header",
            "Section 1: Policies",
            "Token Thresholds",
            "Model Selection", 
            "Section 2: Procedures",
            "Boot Protocol",
            "Shutdown Protocol",
            "Section 3: Tables"
        ]
        
        chunk_headers = [c.metadata.get('header', '') for c in chunks]
        
        for expected in expected_sections:
            if any(expected in header for header in chunk_headers):
                print(f"  ✓ Found section: {expected}")
            else:
                print(f"  ✗ Missing section: {expected}")
                
        # Check that code blocks are preserved
        code_chunk = next((c for c in chunks if '```python' in c.text), None)
        if code_chunk:
            print("  ✓ Code blocks preserved in chunks")
        else:
            print("  ✗ Code blocks not properly preserved")
            
        # Check that tables are preserved
        table_chunk = next((c for c in chunks if '|' in c.text and 'Decision' in c.text), None)
        if table_chunk:
            print("  ✓ Tables preserved in chunks")
        else:
            print("  ✗ Tables not properly preserved")
            
        # Verify tags extraction
        token_chunk = next((c for c in chunks if 'Token Thresholds' in c.text), None)
        if token_chunk and 'token' in token_chunk.tags:
            print("  ✓ Tags properly extracted")
        else:
            print("  ✗ Tag extraction needs improvement")
            
    finally:
        # Cleanup
        os.unlink(temp_path)
        

def test_hash_detection():
    """Test file change detection"""
    print("\n🧪 Testing change detection...")
    
    # Create test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("# Test Document\n\nOriginal content.")
        temp_path = Path(f.name)
        
    try:
        indexer = KnowledgeIndexer()
        
        # First index
        hash1 = indexer._hash_file(temp_path)
        indexer.document_hashes[str(temp_path)] = hash1
        
        # Should not need reindex
        if not indexer.should_reindex(temp_path):
            print("  ✓ Correctly identified unchanged file")
        else:
            print("  ✗ Incorrectly marked unchanged file for reindex")
            
        # Modify file
        with open(temp_path, 'w') as f:
            f.write("# Test Document\n\nModified content!")
            
        # Should need reindex
        if indexer.should_reindex(temp_path):
            print("  ✓ Correctly detected file change")
        else:
            print("  ✗ Failed to detect file change")
            
    finally:
        os.unlink(temp_path)
        

def test_query_performance():
    """Test query response time"""
    print("\n🧪 Testing query performance...")
    
    import time
    
    # Create test corpus
    test_docs = []
    for i in range(5):
        content = f'''# Document {i}
        
## Unique Section {i}
This document contains information about topic {i}.

## Common Section
All documents share this token threshold policy:
- Optimal: <40K tokens
- Warning: 40-80K tokens
- Critical: >80K tokens
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            test_docs.append(Path(f.name))
            
    try:
        indexer = KnowledgeIndexer()
        
        # Index all docs
        total_chunks = 0
        for doc_path in test_docs:
            chunks = indexer.index_file(doc_path)
            total_chunks += chunks
            
        print(f"  ℹ️  Indexed {total_chunks} chunks from {len(test_docs)} documents")
        
        # Test query performance
        queries = [
            "token threshold",
            "optimal tokens", 
            "warning level",
            "unique section 3",
            "common policy"
        ]
        
        response_times = []
        for query in queries:
            start = time.time()
            results = indexer.query_knowledge(query, top_k=3)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            response_times.append(elapsed)
            
            if elapsed < 100:
                print(f"  ✓ Query '{query}': {elapsed:.1f}ms")
            else:
                print(f"  ✗ Query '{query}': {elapsed:.1f}ms (exceeds 100ms target)")
                
        avg_time = sum(response_times) / len(response_times)
        if avg_time < 100:
            print(f"  ✓ Average query time: {avg_time:.1f}ms")
        else:
            print(f"  ✗ Average query time: {avg_time:.1f}ms (exceeds target)")
            
    finally:
        # Cleanup
        for doc_path in test_docs:
            os.unlink(doc_path)
            

def test_integration():
    """Test integration with memory system"""
    print("\n🧪 Testing memory system integration...")
    
    try:
        from memory_integration import EnhancedOrganizationalMemory
        
        # Initialize enhanced memory
        memory = EnhancedOrganizationalMemory()
        print("  ✓ Enhanced memory initialized")
        
        # Check if knowledge index exists
        if memory.has_knowledge_index():
            print("  ✓ Knowledge index detected")
        else:
            print("  ℹ️  No knowledge index yet (normal for first run)")
            
        # Test a query
        results = memory.query_knowledge("test query", top_k=1)
        print("  ✓ Query method accessible")
        
        # Test combined search
        combined = memory.search_memories_semantic("test", top_k=2)
        print("  ✓ Combined search functional")
        
    except ImportError as e:
        print(f"  ✗ Integration test failed: {e}")
        print("    (This is expected if dependencies aren't installed)")
        

if __name__ == "__main__":
    print("🚀 OS-002.1 Knowledge Indexer Test Suite\n")
    
    # Check if dependencies are available
    try:
        import chromadb
        import sentence_transformers
        deps_available = True
    except ImportError:
        print("⚠️  Dependencies not installed. Install with:")
        print("   pip install -r requirements.txt\n")
        deps_available = False
        
    # Run tests that don't require dependencies
    test_chunking()
    test_hash_detection()
    
    if deps_available:
        test_query_performance()
        test_integration()
    else:
        print("\n⏭️  Skipping tests that require ChromaDB/SentenceTransformers")
        
    print("\n✅ Test suite complete!")