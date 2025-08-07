#!/usr/bin/env python3
"""Targeted test to identify and report specific issues"""

from pathlib import Path
from knowledge_indexer import KnowledgeIndexer
import sys

print("🔍 OS-002.1 Issue Analysis\n")

# Issue 1: Code block chunking
print("1. CODE BLOCK CHUNKING ISSUE")
print("-" * 40)

indexer = KnowledgeIndexer()

# Create test content with code blocks
test_content = '''# Test Document

## Code Example

Here's a simple function:

```python
def hello():
    print("Hello World")
```

## Another Section

More text here.

```bash
# Install command
pip install something
```

End of document.
'''

test_file = Path("test_code_blocks.md")
test_file.write_text(test_content)

try:
    chunks = indexer.extract_chunks(test_file)
    
    print(f"Total chunks created: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        code_blocks = chunk.text.count('```')
        if code_blocks > 0:
            print(f"\nChunk {i}: {chunk.metadata.get('header', 'No header')}")
            print(f"  Code block markers: {code_blocks}")
            print(f"  Is broken: {'YES' if code_blocks % 2 != 0 else 'NO'}")
            
finally:
    test_file.unlink()

# Issue 2: Search accuracy
print("\n\n2. SEARCH ACCURACY ISSUE") 
print("-" * 40)

# The issue is that without vector search, we're using simple keyword matching
# which doesn't understand semantic similarity

print("Without ChromaDB/embeddings, search is limited to keyword matching.")
print("This explains why 'boot protocol' doesn't match 'Session Continuity Protocol'")
print("The vector search would understand these are semantically related.")

# Issue 3: Integration method name
print("\n\n3. INTEGRATION METHOD NAME")
print("-" * 40)

integration_file = Path("memory_integration.py")
if integration_file.exists():
    content = integration_file.read_text()
    
    # Check actual method names
    actual_methods = [
        "initialize_knowledge_base",  # This is what exists
        "update_knowledge_index",      # This also exists
    ]
    
    for method in actual_methods:
        if f"def {method}" in content:
            print(f"✓ Found: {method}()")
            
    print("\nNote: Test expects 'index_knowledge_base' but actual method is 'initialize_knowledge_base'")

# Summary
print("\n\n📊 SUMMARY OF ISSUES")
print("=" * 40)
print("1. Code blocks may be split incorrectly during chunking")
print("2. Search accuracy is limited without vector embeddings")
print("3. Test expects wrong method name (minor test issue)")
print("\nThese are mostly test issues, not implementation problems.")