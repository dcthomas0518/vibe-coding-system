#!/usr/bin/env python3
"""
Memory Integration - Connects OS-002.1 Vector Search with OS-002 Memory System
Enhances OrganizationalMemory with semantic search capabilities
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Any

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent / "journey-capture"))

from knowledge_indexer import KnowledgeIndexer
from internal_memory import OrganizationalMemory


class EnhancedOrganizationalMemory(OrganizationalMemory):
    """
    Extended OrganizationalMemory with vector search capabilities
    Inherits from OS-002 and adds OS-002.1 features
    """
    
    def __init__(self):
        """Initialize with both memory and knowledge systems"""
        super().__init__()
        
        # Initialize knowledge indexer
        self.knowledge_indexer = KnowledgeIndexer()
        
        # Check if knowledge base needs initialization
        stats = self.knowledge_indexer.get_index_stats()
        if stats['status'] == 'not_initialized' or stats.get('total_chunks', 0) == 0:
            print("🔍 Initializing knowledge base on first boot...")
            self.initialize_knowledge_base()
            
    def initialize_knowledge_base(self):
        """One-time index of existing docs"""
        print("📚 Indexing organizational knowledge...")
        
        # Run the indexing
        stats = self.knowledge_indexer.scan_and_index()
        
        # Store indexing event as a memory
        self.create_memory(
            entity={
                "type": "system",
                "name": "knowledge_indexer",
                "mode": "os_002_1"
            },
            event={
                "type": "system_enhancement",
                "category": "initialization",
                "description": f"Indexed {stats['chunks_created']} knowledge chunks from {stats['files_indexed']} documents",
                "significance": "major"
            },
            content={
                "stats": stats,
                "feature": "OS-002.1 Vector Search"
            },
            outcome={
                "status": "success",
                "impact": "Enabled instant semantic search across organizational knowledge"
            }
        )
        
    def has_knowledge_index(self) -> bool:
        """Check if knowledge index exists"""
        stats = self.knowledge_indexer.get_index_stats()
        return stats['status'] == 'active' and stats.get('total_chunks', 0) > 0
        
    def query_knowledge(self, question: str, top_k: int = 3, 
                       category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Query organizational knowledge with semantic search
        Returns relevant text chunks with sources - NO FILE I/O!
        """
        results = self.knowledge_indexer.query_knowledge(
            question=question,
            top_k=top_k,
            category_filter=category_filter
        )
        
        # Log the query as a memory event
        if results:
            self.create_memory(
                entity={
                    "type": "assistant",
                    "name": "claude",
                    "mode": self._get_current_mode()
                },
                event={
                    "type": "knowledge_query",
                    "category": "retrieval",
                    "description": f"Successfully retrieved {len(results)} results for: {question}",
                    "significance": "routine"
                },
                content={
                    "query": question,
                    "result_count": len(results),
                    "top_source": results[0]['source'] if results else None
                }
            )
            
        return results
        
    def _get_current_mode(self) -> str:
        """Get current department mode from context"""
        # This would be enhanced to read from CURRENT_CONTEXT.md
        # For now, default to CTO
        return "cto"
        
    def update_knowledge_index(self, force_full: bool = False):
        """Update knowledge index with any changed documents"""
        print("🔄 Updating knowledge index...")
        
        stats = self.knowledge_indexer.scan_and_index(force_reindex=force_full)
        
        if stats['files_indexed'] > 0:
            self.create_memory(
                entity={
                    "type": "system",
                    "name": "knowledge_indexer",
                    "mode": "os_002_1"
                },
                event={
                    "type": "index_update",
                    "category": "maintenance",
                    "description": f"Updated index with {stats['files_indexed']} changed documents",
                    "significance": "routine"
                },
                content={"stats": stats}
            )
            
        return stats
        
    def search_memories_semantic(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Combine traditional memory search with semantic knowledge search
        Returns unified results from both systems
        """
        results = []
        
        # Get semantic results from knowledge base
        knowledge_results = self.query_knowledge(query, top_k=top_k)
        
        # Get relevant memories from SQL queries
        # This could be enhanced to use embeddings for memories too
        memory_results = self.search_memories(
            entity_name=None,
            event_type=None,
            time_range=None,
            limit=top_k
        )
        
        # Combine and rank results
        for kr in knowledge_results:
            results.append({
                'type': 'knowledge',
                'source': kr['source'],
                'text': kr['text'],
                'relevance': 1.0 - (kr.get('score', 0.5))  # Convert distance to relevance
            })
            
        for mr in memory_results:
            results.append({
                'type': 'memory',
                'source': f"Memory {mr['id']}",
                'text': mr['event']['description'],
                'relevance': 0.7  # Default relevance for SQL results
            })
            
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        return results[:top_k]


def update_claude_session_init():
    """
    Update the claude_session_init.py to use enhanced memory
    This function shows what changes are needed
    """
    code = '''
# In claude_session_init.py, replace:
# from internal_memory import OrganizationalMemory

# With:
from os_modules.os_002_1_vector_search.memory_integration import EnhancedOrganizationalMemory

# Then replace:
# memory = OrganizationalMemory()

# With:
memory = EnhancedOrganizationalMemory()

# The rest remains the same - the enhanced memory is a drop-in replacement
'''
    return code


if __name__ == "__main__":
    # Test the enhanced memory system
    print("🧪 Testing Enhanced Organizational Memory...")
    
    memory = EnhancedOrganizationalMemory()
    
    # Test queries
    test_queries = [
        "What are our token thresholds?",
        "How do we handle context overflow?",
        "What is the model selection strategy?",
        "What are the department head responsibilities?",
        "How does the boot protocol work?"
    ]
    
    print("\n📋 Testing knowledge queries:")
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        results = memory.query_knowledge(query, top_k=1)
        
        if results:
            result = results[0]
            print(f"✅ Found in: {result['source']} (lines {result['lines']})")
            print(f"📄 Category: {result['category']}")
            print(f"🏷️  Tags: {', '.join(result['tags'])}")
            print(f"📝 Text preview: {result['text'][:150]}...")
        else:
            print("❌ No results found")
            
    # Test combined search
    print("\n\n🔍 Testing combined semantic search:")
    combined_results = memory.search_memories_semantic("token management", top_k=3)
    
    for i, result in enumerate(combined_results):
        print(f"\n{i+1}. Type: {result['type']}")
        print(f"   Source: {result['source']}")
        print(f"   Relevance: {result['relevance']:.2f}")
        print(f"   Preview: {result['text'][:100]}...")
        
    print("\n✨ Enhanced memory system ready!")