#!/usr/bin/env python3
"""Debug broken code blocks in chunking"""

from pathlib import Path
from knowledge_indexer import KnowledgeIndexer

indexer = KnowledgeIndexer()
claude_path = Path("/home/dthomas_unix/CLAUDE.md")

chunks = indexer.extract_chunks(claude_path)

print("Analyzing chunks with broken code blocks...\n")

broken_chunks = []
for i, chunk in enumerate(chunks):
    open_code = chunk.text.count('```')
    if open_code % 2 != 0:
        broken_chunks.append((i, chunk))
        
for idx, chunk in broken_chunks[:3]:  # Show first 3
    print(f"Chunk {idx}: {chunk.metadata.get('header', 'No header')}")
    print(f"Lines {chunk.start_line}-{chunk.end_line}")
    print("Content preview:")
    print("-" * 40)
    lines = chunk.text.split('\n')
    for line in lines:
        if '```' in line:
            print(f">>> {line}")
    print("-" * 40)
    print()