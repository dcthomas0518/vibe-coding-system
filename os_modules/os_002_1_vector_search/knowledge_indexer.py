#!/usr/bin/env python3
"""
Knowledge Indexer - OS-002.1: Vector Database Knowledge Indexing
Indexes organizational knowledge for instant semantic retrieval
"""

import os
import re
import json
import hashlib
import glob
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
import logging
from dataclasses import dataclass

# Third-party imports (will be installed via requirements.txt)
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("⚠️  Missing dependencies. Install with: pip install chromadb sentence-transformers")
    chromadb = None
    SentenceTransformer = None


@dataclass
class DocumentChunk:
    """Represents a semantic chunk of a document"""
    text: str
    source_file: str
    start_line: int
    end_line: int
    category: str
    tags: List[str]
    metadata: Dict[str, any]


class KnowledgeIndexer:
    """Indexes organizational docs for semantic search"""
    
    # Critical documents to index (relative to vibe-coding-system root)
    CRITICAL_DOCS = [
        '../../CLAUDE.md',                          # System instructions
        '../../DEPARTMENT_HEADS.md',                # Org structure
        '../../LEARNINGS.md',                       # Learning protocol & discoveries
        '../../DECISIONS.md',                       # Decision log & rationale
        '../../chief-of-staff/strategic/specs/**/*.md',  # All SPECs
        '../../organization/*.md',                  # Governance
        '../../organization/BOARD_MINUTES/*.md',    # Board decisions
        '../../chief-of-staff/strategic/*.md',      # Strategic docs
        '../../chief-of-staff/observations/*.md',   # Strategic insights
        '**/PROJECT_CONTEXT.md',                    # Per-project context
        '**/SESSIONS_LOG.md',                       # Sprint history
        '**/TECHNICAL_CONTEXT.md',                  # Technical decisions
        '../../CURRENT_CONTEXT.md',                 # Active session state
    ]
    
    # Document categories for better filtering
    CATEGORY_PATTERNS = {
        'policy': ['CLAUDE.md', 'DEPARTMENT_HEADS.md', 'BOARD_PROTOCOL.md'],
        'spec': ['SPEC_*.md', 'specs/**/*.md'],
        'strategic': ['strategic/*.md', 'observations/*.md'],
        'governance': ['organization/*.md', 'BOARD_MINUTES/*.md'],
        'project': ['PROJECT_CONTEXT.md', 'TECHNICAL_CONTEXT.md'],
        'history': ['SESSIONS_LOG.md', 'SPRINT_HISTORY.md'],
    }
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize the knowledge indexer"""
        self.base_path = base_path or Path(__file__).parent.parent.parent
        self.db_path = self.base_path / "state" / "knowledge_index"
        self.hash_file = self.db_path / "document_hashes.json"
        
        # Create directories if they don't exist
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        if chromadb:
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="organizational_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
        else:
            self.chroma_client = None
            self.collection = None
            
        # Initialize embedding model
        if SentenceTransformer:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.embedder = None
            
        # Load document hashes
        self.document_hashes = self._load_hashes()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _load_hashes(self) -> Dict[str, str]:
        """Load stored document hashes"""
        if self.hash_file.exists():
            with open(self.hash_file, 'r') as f:
                return json.load(f)
        return {}
        
    def _save_hashes(self):
        """Save document hashes to disk"""
        with open(self.hash_file, 'w') as f:
            json.dump(self.document_hashes, f, indent=2)
            
    def _hash_file(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
        
    def should_reindex(self, file_path: Path) -> bool:
        """Check if file has changed since last index"""
        str_path = str(file_path)
        current_hash = self._hash_file(file_path)
        stored_hash = self.document_hashes.get(str_path, '')
        return current_hash != stored_hash
        
    def add_document(self, file_path: Path, force: bool = False) -> bool:
        """Add a document to the vector index"""
        if not self.collection or not self.embedder:
            self.logger.warning("ChromaDB or embedder not initialized")
            return False
            
        # Check if document needs reindexing
        if not force and not self.should_reindex(file_path):
            return False
            
        try:
            # Read document content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Create chunks
            chunks = self._chunk_document(content)
            
            # Generate embeddings and metadata for each chunk
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_path}_{i}"
                
                # Create metadata
                metadata = {
                    "source": str(file_path),
                    "chunk_index": i,
                    "category": self._categorize_document(file_path),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add to collection
                self.collection.add(
                    documents=[chunk],
                    metadatas=[metadata],
                    ids=[chunk_id]
                )
            
            # Update hash
            self.document_hashes[str(file_path)] = self._hash_file(file_path)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add document {file_path}: {e}")
            return False
    
    def _chunk_document(self, content: str, chunk_size: int = 1000) -> List[str]:
        """Split document into chunks for indexing"""
        # Simple chunking by paragraphs or size
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line)
            if current_size + line_size > chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
            
        return chunks if chunks else [content]
    
    def index_all_documents(self) -> int:
        """Index all critical documents"""
        indexed_count = 0
        
        for pattern in self.CRITICAL_DOCS:
            # Convert pattern to absolute path
            if pattern.startswith('**'):
                # Recursive glob
                files = list(self.base_path.glob(pattern))
            else:
                # Regular glob from base path
                search_path = self.base_path / pattern.lstrip('/')
                if '*' in str(search_path):
                    files = list(search_path.parent.glob(search_path.name))
                elif search_path.exists() and search_path.is_file():
                    files = [search_path]
                else:
                    files = []
            
            for file_path in files:
                if file_path.suffix == '.md' and self.add_document(file_path):
                    indexed_count += 1
                    
        # Save hashes after indexing
        self._save_hashes()
        return indexed_count
    
    @property
    def persist_directory(self) -> str:
        """Get the persistence directory path"""
        return str(self.db_path)
    
    def _categorize_document(self, file_path: Path) -> str:
        """Determine document category based on path patterns"""
        str_path = str(file_path)
        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if pattern in str_path or file_path.match(pattern):
                    return category
        return 'general'
        
    def _extract_tags(self, text: str, file_path: Path) -> List[str]:
        """Extract relevant tags from document content"""
        tags = []
        
        # Extract from filename
        filename = file_path.stem.lower()
        tags.extend(filename.split('_'))
        
        # Common keywords to look for
        keywords = ['token', 'model', 'context', 'memory', 'boot', 'reboot', 
                   'threshold', 'limit', 'policy', 'protocol', 'spec', 'architecture']
        
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                tags.append(keyword)
                
        # Look for technical terms
        tech_patterns = [
            r'opus[-\s]?4',
            r'sonnet[-\s]?4',
            r'claude',
            r'chromadb',
            r'vector',
            r'embedding',
        ]
        
        for pattern in tech_patterns:
            if re.search(pattern, text_lower):
                tags.append(pattern.replace(r'[-\s]?', ''))
                
        return list(set(tags))  # Remove duplicates
        
    def extract_chunks(self, file_path: Path) -> List[DocumentChunk]:
        """Extract semantic chunks from a markdown file"""
        chunks = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        category = self._categorize_document(file_path)
        relative_path = file_path.relative_to(self.base_path.parent.parent)
        
        # Track current section
        current_section = []
        section_start = 0
        current_header = ""
        header_level = 0
        
        for i, line in enumerate(lines):
            # Check for headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if header_match:
                # Save previous section if it has content
                if current_section and any(line.strip() for line in current_section):
                    chunk_text = '\n'.join(current_section)
                    tags = self._extract_tags(chunk_text, file_path)
                    
                    chunks.append(DocumentChunk(
                        text=chunk_text,
                        source_file=str(relative_path),
                        start_line=section_start + 1,  # 1-indexed
                        end_line=i,
                        category=category,
                        tags=tags,
                        metadata={
                            'header': current_header,
                            'header_level': header_level,
                            'last_indexed': datetime.now().isoformat()
                        }
                    ))
                
                # Start new section
                new_level = len(header_match.group(1))
                current_header = header_match.group(2)
                header_level = new_level
                current_section = [line]
                section_start = i
                
            else:
                # Continue building current section
                current_section.append(line)
                
                # Special handling for code blocks and tables
                if line.strip().startswith('```'):
                    # Include entire code block in current chunk
                    in_code_block = True
                    while i + 1 < len(lines) and in_code_block:
                        i += 1
                        current_section.append(lines[i])
                        if lines[i].strip() == '```':
                            in_code_block = False
                            
        # Don't forget the last section
        if current_section and any(line.strip() for line in current_section):
            chunk_text = '\n'.join(current_section)
            tags = self._extract_tags(chunk_text, file_path)
            
            chunks.append(DocumentChunk(
                text=chunk_text,
                source_file=str(relative_path),
                start_line=section_start + 1,
                end_line=len(lines),
                category=category,
                tags=tags,
                metadata={
                    'header': current_header,
                    'header_level': header_level,
                    'last_indexed': datetime.now().isoformat()
                }
            ))
            
        return chunks
        
    def index_file(self, file_path: Path) -> int:
        """Index a single file, returning number of chunks indexed"""
        if not self.collection or not self.embedder:
            self.logger.warning("ChromaDB or embedder not initialized")
            return 0
            
        try:
            # Extract chunks
            chunks = self.extract_chunks(file_path)
            
            if not chunks:
                return 0
                
            # Prepare data for ChromaDB
            texts = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                # Create unique ID based on file and location
                chunk_id = f"{chunk.source_file}:{chunk.start_line}-{chunk.end_line}"
                
                texts.append(chunk.text)
                ids.append(chunk_id)
                
                # Prepare metadata
                metadata = {
                    'source_file': chunk.source_file,
                    'lines': f"{chunk.start_line}-{chunk.end_line}",
                    'category': chunk.category,
                    'tags': ','.join(chunk.tags),
                    'last_indexed': chunk.metadata['last_indexed'],
                    'header': chunk.metadata.get('header', ''),
                    'header_level': chunk.metadata.get('header_level', 0)
                }
                metadatas.append(metadata)
                
            # Generate embeddings
            embeddings = self.embedder.encode(texts).tolist()
            
            # Upsert to ChromaDB (will update if exists)
            self.collection.upsert(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            # Update hash
            self.document_hashes[str(file_path)] = self._hash_file(file_path)
            
            return len(chunks)
            
        except Exception as e:
            self.logger.error(f"Error indexing {file_path}: {e}")
            return 0
            
    def scan_and_index(self, force_reindex: bool = False) -> Dict[str, int]:
        """Scan all critical documents and index them"""
        stats = {
            'files_scanned': 0,
            'files_indexed': 0,
            'chunks_created': 0,
            'errors': 0
        }
        
        print("📚 Scanning organizational knowledge...")
        
        for pattern in self.CRITICAL_DOCS:
            # Resolve pattern relative to base path
            full_pattern = str(self.base_path / pattern)
            
            # Find matching files
            for file_path in glob.glob(full_pattern, recursive=True):
                path = Path(file_path)
                
                # Skip non-markdown files
                if not path.suffix == '.md':
                    continue
                    
                stats['files_scanned'] += 1
                
                # Check if needs reindexing
                if force_reindex or self.should_reindex(path):
                    print(f"  📄 Indexing: {path.name}")
                    chunks = self.index_file(path)
                    
                    if chunks > 0:
                        stats['files_indexed'] += 1
                        stats['chunks_created'] += chunks
                    else:
                        stats['errors'] += 1
                        
        # Save updated hashes
        self._save_hashes()
        
        print(f"✅ Indexing complete:")
        print(f"   - Files scanned: {stats['files_scanned']}")
        print(f"   - Files indexed: {stats['files_indexed']}")
        print(f"   - Chunks created: {stats['chunks_created']}")
        print(f"   - Errors: {stats['errors']}")
        
        return stats
        
    def query_knowledge(self, question: str, top_k: int = 3, 
                       category_filter: Optional[str] = None) -> List[Dict[str, any]]:
        """Query the knowledge base for relevant information"""
        if not self.collection or not self.embedder:
            self.logger.warning("ChromaDB or embedder not initialized")
            return []
            
        try:
            # Generate embedding for query
            query_embedding = self.embedder.encode([question])[0].tolist()
            
            # Build where clause for filtering
            where = {}
            if category_filter:
                where['category'] = category_filter
                
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where if where else None
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    
                    formatted_results.append({
                        'text': doc,
                        'source': metadata['source_file'],
                        'lines': metadata['lines'],
                        'category': metadata['category'],
                        'tags': metadata['tags'].split(',') if metadata['tags'] else [],
                        'header': metadata.get('header', ''),
                        'score': results['distances'][0][i] if 'distances' in results else None
                    })
                    
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error querying knowledge: {e}")
            return []
            
    def get_index_stats(self) -> Dict[str, any]:
        """Get statistics about the knowledge index"""
        if not self.collection:
            return {'status': 'not_initialized'}
            
        count = self.collection.count()
        
        # Get category distribution
        all_items = self.collection.get()
        category_counts = {}
        
        if all_items['metadatas']:
            for metadata in all_items['metadatas']:
                category = metadata.get('category', 'unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
                
        return {
            'status': 'active',
            'total_chunks': count,
            'indexed_files': len(self.document_hashes),
            'categories': category_counts,
            'last_update': datetime.now().isoformat()
        }


# Integration helper for OS-002
def integrate_with_memory_system():
    """Helper to integrate with existing OrganizationalMemory"""
    indexer = KnowledgeIndexer()
    
    # Check if index exists
    stats = indexer.get_index_stats()
    
    if stats['status'] == 'not_initialized' or stats.get('total_chunks', 0) == 0:
        print("🔍 No knowledge index found. Creating initial index...")
        indexer.scan_and_index()
    else:
        print(f"📚 Knowledge index found with {stats['total_chunks']} chunks")
        # Only reindex changed files
        indexer.scan_and_index(force_reindex=False)
        
    return indexer


if __name__ == "__main__":
    # Test the indexer
    indexer = KnowledgeIndexer()
    
    # Run initial indexing
    stats = indexer.scan_and_index()
    
    # Test some queries
    test_queries = [
        "What are our token thresholds?",
        "How do we handle model selection?",
        "What is the boot protocol?",
        "Who are the department heads?",
        "What is OS-004?"
    ]
    
    print("\n🧪 Testing queries:")
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = indexer.query_knowledge(query, top_k=1)
        if results:
            result = results[0]
            print(f"✓ Found in: {result['source']} (lines {result['lines']})")
            print(f"  Text preview: {result['text'][:200]}...")
        else:
            print("✗ No results found")