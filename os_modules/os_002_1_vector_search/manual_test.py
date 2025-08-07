#!/usr/bin/env python3
"""
Manual test script for OS-002.1 without dependencies
Tests core functionality that doesn't require ChromaDB
"""

import sys
import time
from pathlib import Path
from knowledge_indexer import KnowledgeIndexer

def test_real_file_chunking():
    """Test chunking on actual CLAUDE.md file"""
    print("🧪 Testing chunking on real CLAUDE.md file...")
    
    indexer = KnowledgeIndexer()
    claude_path = Path("/home/dthomas_unix/CLAUDE.md")
    
    if not claude_path.exists():
        print("  ✗ CLAUDE.md not found")
        return
        
    try:
        chunks = indexer.extract_chunks(claude_path)
        print(f"  ✓ Extracted {len(chunks)} chunks from CLAUDE.md")
        
        # Look for specific sections we know exist
        expected_sections = [
            "Session & Memory Management",
            "Model Selection Strategy", 
            "Context Management",
            "Quality Standards",
            "Pre-Clear Protocol"
        ]
        
        found_sections = set()
        for chunk in chunks:
            header = chunk.metadata.get('header', '')
            for section in expected_sections:
                if section in header:
                    found_sections.add(section)
                    
        print(f"  ✓ Found {len(found_sections)}/{len(expected_sections)} expected sections")
        for section in expected_sections:
            if section in found_sections:
                print(f"    ✓ {section}")
            else:
                print(f"    ✗ {section}")
                
        # Check chunk sizes
        chunk_sizes = [len(chunk.text) for chunk in chunks]
        avg_size = sum(chunk_sizes) / len(chunk_sizes)
        print(f"  ℹ️  Average chunk size: {avg_size:.0f} chars")
        print(f"  ℹ️  Min/Max chunk size: {min(chunk_sizes)}/{max(chunk_sizes)} chars")
        
        # Check tag extraction
        all_tags = set()
        for chunk in chunks:
            all_tags.update(chunk.tags)
        print(f"  ℹ️  Unique tags extracted: {len(all_tags)}")
        sample_tags = list(all_tags)[:10]
        print(f"    Sample: {', '.join(sample_tags)}")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_specific_queries():
    """Test chunking with specific query examples from SPEC"""
    print("\n🧪 Testing semantic boundary detection...")
    
    indexer = KnowledgeIndexer()
    
    # Create test content with clear semantic boundaries
    test_file = Path("/home/dthomas_unix/vibe-coding-system/os_modules/os_002_1_vector_search/test_doc.md")
    test_content = '''# Context Management

## Intelligent Context Management (OS-004)
**NEW**: Automatic peak performance maintenance through intelligent reboots
- Natural breakpoint detection
- Work complexity protection  
- State preservation and resumption
- Dale-friendly maintenance notifications

## Context Thresholds
- Optimal: <40K tokens (peak performance)
- Warning: 40-80K tokens (monitor closely)
- Critical: >80K tokens (brain fog risk)
- Emergency: >100K tokens (forced reboot)
- Action: Intelligent reboots at natural breakpoints

## Model Selection Strategy

### Dynamic Model Selection (Anthropic 50% Opus Limit)

To maintain peak performance while respecting Anthropic's 5-hour usage windows:

#### Usage Phases
- **Phase 1 (0-30%)**: Liberal Opus usage for all complex tasks
- **Phase 2 (30-45%)**: Selective Opus, delegate more to Sonnet sub-agents
- **Phase 3 (45-50%)**: Preserve Opus for critical work only
'''
    
    try:
        # Write test file
        test_file.write_text(test_content)
        
        # Extract chunks
        chunks = indexer.extract_chunks(test_file)
        print(f"  ✓ Created {len(chunks)} chunks from test document")
        
        # Verify each major section got its own chunk
        chunk_headers = [c.metadata.get('header', '') for c in chunks]
        
        expected_boundaries = [
            "Context Management",
            "Intelligent Context Management",
            "Context Thresholds", 
            "Model Selection Strategy",
            "Dynamic Model Selection"
        ]
        
        for boundary in expected_boundaries:
            if any(boundary in header for header in chunk_headers):
                print(f"  ✓ Semantic boundary preserved: {boundary}")
            else:
                print(f"  ✗ Semantic boundary missed: {boundary}")
                
        # Check that related content stays together
        threshold_chunk = next((c for c in chunks if "Context Thresholds" in c.metadata.get('header', '')), None)
        if threshold_chunk:
            if "<40K tokens" in threshold_chunk.text and ">100K tokens" in threshold_chunk.text:
                print("  ✓ Related threshold info kept together")
            else:
                print("  ✗ Threshold info was split incorrectly")
                
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def test_hash_performance():
    """Test file change detection performance"""
    print("\n🧪 Testing change detection performance...")
    
    indexer = KnowledgeIndexer()
    
    # Test on multiple real files
    test_files = [
        Path("/home/dthomas_unix/CLAUDE.md"),
        Path("/home/dthomas_unix/CURRENT_CONTEXT.md"),
        Path("/home/dthomas_unix/PRE_CLEAR_CHECKLIST.md")
    ]
    
    existing_files = [f for f in test_files if f.exists()]
    print(f"  ℹ️  Testing with {len(existing_files)} files")
    
    # First pass - hash all files
    start_time = time.time()
    for file_path in existing_files:
        hash_val = indexer._hash_file(file_path)
        indexer.document_hashes[str(file_path)] = hash_val
    hash_time = (time.time() - start_time) * 1000
    
    print(f"  ✓ Initial hashing completed in {hash_time:.1f}ms")
    
    # Second pass - check if reindex needed (should be fast)
    start_time = time.time()
    reindex_checks = 0
    for file_path in existing_files:
        if indexer.should_reindex(file_path):
            reindex_checks += 1
    check_time = (time.time() - start_time) * 1000
    
    print(f"  ✓ Change detection completed in {check_time:.1f}ms")
    print(f"  ℹ️  Files needing reindex: {reindex_checks}/{len(existing_files)}")


def simulate_query_matching():
    """Simulate how queries would match chunks"""
    print("\n🧪 Simulating query matching (without vector DB)...")
    
    indexer = KnowledgeIndexer()
    claude_path = Path("/home/dthomas_unix/CLAUDE.md")
    
    if not claude_path.exists():
        print("  ✗ CLAUDE.md not found")
        return
        
    chunks = indexer.extract_chunks(claude_path)
    
    # Test queries from SPEC
    test_queries = [
        ("What are our token thresholds?", ["token", "threshold", "40k", "80k"]),
        ("How do we handle model selection?", ["model", "selection", "opus", "sonnet"]),
        ("What is the boot protocol?", ["boot", "protocol", "initialize", "session"])
    ]
    
    for query, keywords in test_queries:
        print(f"\n  Query: '{query}'")
        
        # Simple keyword matching simulation
        matching_chunks = []
        for chunk in chunks:
            chunk_lower = chunk.text.lower()
            score = sum(1 for kw in keywords if kw.lower() in chunk_lower)
            if score > 0:
                matching_chunks.append((chunk, score))
                
        # Sort by score
        matching_chunks.sort(key=lambda x: x[1], reverse=True)
        
        if matching_chunks:
            best_match = matching_chunks[0][0]
            print(f"    ✓ Found {len(matching_chunks)} matching chunks")
            print(f"    Best match: {best_match.metadata.get('header', 'Unknown')}")
            print(f"    Preview: {best_match.text[:100]}...")
        else:
            print(f"    ✗ No matching chunks found")


if __name__ == "__main__":
    print("🚀 OS-002.1 Manual Test Suite (No Dependencies)\n")
    
    test_real_file_chunking()
    test_specific_queries()
    test_hash_performance()
    simulate_query_matching()
    
    print("\n✅ Manual test suite complete!")
    print("\nNote: Full vector search functionality requires ChromaDB installation")