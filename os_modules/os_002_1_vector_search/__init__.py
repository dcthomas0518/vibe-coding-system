"""
OS-002.1: Vector Database Knowledge Indexing
Instant semantic search across organizational knowledge
"""

from .knowledge_indexer import KnowledgeIndexer, DocumentChunk, integrate_with_memory_system
from .memory_integration import EnhancedOrganizationalMemory

__version__ = "0.1.0"
__all__ = [
    "KnowledgeIndexer",
    "DocumentChunk", 
    "EnhancedOrganizationalMemory",
    "integrate_with_memory_system"
]