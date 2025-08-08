#!/usr/bin/env python3
"""
Index Organizational Knowledge for OS-002.1 Vector Search
Implements the audit recommendations to eliminate organizational amnesia
"""

import os
import sys
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import glob

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent))

from knowledge_indexer import VectorKnowledgeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OrganizationalKnowledgeIndexer:
    """Index all organizational knowledge based on audit recommendations"""
    
    # High Priority Content Patterns
    HIGH_PRIORITY_PATTERNS = {
        "system_instructions": [
            "~/CLAUDE.md",
            "~/vibe-coding-system/CLAUDE.md",
            "~/vibe-coding-system/PRE_CLEAR_CHECKLIST.md",
            "~/vibe-coding-system/docs/OPERATIONS_RUNBOOK.md",
            "~/chief-of-staff/CRASSUS_SYSTEM_INSTRUCTIONS.md"
        ],
        "organizational_structure": [
            "~/organization/*.md",
            "~/organization/BOARD_MINUTES/*.md",
            "~/.claude/agents/*.md"
        ],
        "domain_expertise": [
            "~/cat-food-project/COMPLETE_NUTRIENT_SYSTEM.md",
            "~/cat-food-project/THERAPEUTIC_KNOWLEDGE_SYSTEM.md",
            "~/cat-food-project/TRUE_USDA_DATA_FINDINGS.md",
            "~/cat-food-project/HOW_TO_ADD_INGREDIENTS.md",
            "~/cat-food-project/docs/SENATE_PROTOCOL.md",
            "~/cat-food-project/TECHNICAL_CONTENT.md"
        ],
        "technical_architecture": [
            "~/vibe-coding-system/OS-001_ARCHITECTURE.md",
            "~/vibe-coding-system/os_modules/*/README.md",
            "~/vibe-coding-system/docs/adr/*.md",
            "~/vibe-coding-system/docs/API_DOCUMENTATION.md",
            "~/vibe-coding-system/task-management-api-spec.md",
            "~/vibe-coding-system/user-behavior-data-pipeline-design.md",
            "~/specs/**/*.md"
        ],
        "strategic_insights": [
            "~/chief-of-staff/STRATEGIC_OBSERVATIONS.md",
            "~/chief-of-staff/FOUNDER_PROFILE_DRAFT.md",
            "~/chief-of-staff/DEPT_NOTES/*.md"
        ]
    }
    
    # Medium Priority Content Patterns
    MEDIUM_PRIORITY_PATTERNS = {
        "project_context": [
            "~/*/PROJECT_CONTEXT.md",
            "~/*/TECHNICAL_CONTEXT.md",
            "~/*/SESSIONS_LOG.md"
        ],
        "journey_capture": [
            "~/vibe-coding-system/journey-capture/BOOT_PROTOCOL.md",
            "~/vibe-coding-system/journey-capture/MEMORY_MANIFEST.md",
            "~/vibe-coding-system/journey-capture/README_COLLECTIVE_SOUL.md"
        ],
        "development_docs": [
            "~/vibe-coding-system/docs/DEVELOPER_GETTING_STARTED.md",
            "~/vibe-coding-system/IMPLEMENTATION_CHECKLIST.md",
            "~/vibe-coding-system/TASK_API_TEST_PLAN.md",
            "~/vibe-coding-system/devops-infrastructure-plan.md",
            "~/vibe-coding-system/ENHANCEMENT_ROADMAP.md",
            "~/vibe-coding-system/TEAM_STRUCTURE_V2.md"
        ]
    }
    
    # Low Priority Content Patterns  
    LOW_PRIORITY_PATTERNS = {
        "historical": [
            "~/vibe-coding-system/SPRINT_HISTORY.md",
            "~/vibe-coding-system/journey-capture/*_BACKUP.md"
        ],
        "reference": [
            "~/vibe-coding-system/BEST_PRACTICES_ANALYSIS.md",
            "~/vibe-coding-system/COMPACT_SUMMARY.md"
        ]
    }
    
    def __init__(self):
        """Initialize the indexer with vector knowledge base"""
        self.kb = VectorKnowledgeBase()
        self.indexed_files = set()
        self.hash_cache_file = Path.home() / ".vector_index_hashes.json"
        self.load_hash_cache()
        
    def load_hash_cache(self):
        """Load cached file hashes to detect changes"""
        if self.hash_cache_file.exists():
            with open(self.hash_cache_file, 'r') as f:
                self.hash_cache = json.load(f)
        else:
            self.hash_cache = {}
    
    def save_hash_cache(self):
        """Save file hashes for change detection"""
        with open(self.hash_cache_file, 'w') as f:
            json.dump(self.hash_cache, f, indent=2)
    
    def get_file_hash(self, file_path: str) -> str:
        """Get MD5 hash of file content"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def should_index_file(self, file_path: str) -> bool:
        """Check if file needs indexing based on hash"""
        if not os.path.exists(file_path):
            return False
            
        current_hash = self.get_file_hash(file_path)
        cached_hash = self.hash_cache.get(file_path)
        
        if cached_hash != current_hash:
            self.hash_cache[file_path] = current_hash
            return True
        return False
    
    def expand_patterns(self, patterns: List[str]) -> List[str]:
        """Expand glob patterns to actual file paths"""
        expanded_files = []
        home = str(Path.home())
        
        for pattern in patterns:
            # Expand tilde to home directory
            pattern = pattern.replace("~", home)
            
            # Use glob to expand wildcards
            matches = glob.glob(pattern, recursive=True)
            
            # Filter to only .md files
            md_files = [f for f in matches if f.endswith('.md') and os.path.isfile(f)]
            expanded_files.extend(md_files)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_files = []
        for f in expanded_files:
            if f not in seen:
                seen.add(f)
                unique_files.append(f)
        
        return unique_files
    
    def index_files(self, files: List[str], priority: str, category: str) -> int:
        """Index a list of files with given priority and category"""
        indexed_count = 0
        
        for file_path in files:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue
            
            # Skip if already indexed and unchanged
            if not self.should_index_file(file_path):
                logger.debug(f"Skipping unchanged file: {file_path}")
                continue
            
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Skip empty files
                if not content.strip():
                    logger.debug(f"Skipping empty file: {file_path}")
                    continue
                
                # Prepare metadata
                metadata = {
                    "source": file_path,
                    "priority": priority,
                    "category": category,
                    "indexed_at": datetime.now().isoformat(),
                    "file_size": os.path.getsize(file_path),
                    "last_modified": datetime.fromtimestamp(
                        os.path.getmtime(file_path)
                    ).isoformat()
                }
                
                # Add to knowledge base
                self.kb.add_document(
                    text=content,
                    metadata=metadata,
                    doc_id=file_path
                )
                
                self.indexed_files.add(file_path)
                indexed_count += 1
                logger.info(f"✅ Indexed: {file_path} ({priority}/{category})")
                
            except Exception as e:
                logger.error(f"❌ Failed to index {file_path}: {e}")
        
        return indexed_count
    
    def run_full_index(self):
        """Run complete indexing based on audit recommendations"""
        logger.info("=" * 60)
        logger.info("🚀 Starting Organizational Knowledge Indexing")
        logger.info("=" * 60)
        
        total_indexed = 0
        
        # Phase 1: High Priority Content
        logger.info("\n📌 PHASE 1: HIGH PRIORITY CONTENT")
        logger.info("-" * 40)
        
        for category, patterns in self.HIGH_PRIORITY_PATTERNS.items():
            logger.info(f"\n📁 Indexing {category}...")
            files = self.expand_patterns(patterns)
            logger.info(f"   Found {len(files)} files to process")
            count = self.index_files(files, "HIGH", category)
            total_indexed += count
            logger.info(f"   ✅ Indexed {count} new/changed files")
        
        # Phase 2: Medium Priority Content
        logger.info("\n📌 PHASE 2: MEDIUM PRIORITY CONTENT")
        logger.info("-" * 40)
        
        for category, patterns in self.MEDIUM_PRIORITY_PATTERNS.items():
            logger.info(f"\n📁 Indexing {category}...")
            files = self.expand_patterns(patterns)
            logger.info(f"   Found {len(files)} files to process")
            count = self.index_files(files, "MEDIUM", category)
            total_indexed += count
            logger.info(f"   ✅ Indexed {count} new/changed files")
        
        # Phase 3: Low Priority Content (Optional)
        logger.info("\n📌 PHASE 3: LOW PRIORITY CONTENT")
        logger.info("-" * 40)
        
        for category, patterns in self.LOW_PRIORITY_PATTERNS.items():
            logger.info(f"\n📁 Indexing {category}...")
            files = self.expand_patterns(patterns)
            logger.info(f"   Found {len(files)} files to process")
            count = self.index_files(files, "LOW", category)
            total_indexed += count
            logger.info(f"   ✅ Indexed {count} new/changed files")
        
        # Save hash cache for next run
        self.save_hash_cache()
        
        # Final statistics
        logger.info("\n" + "=" * 60)
        logger.info("✨ INDEXING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"📊 Total files indexed: {total_indexed}")
        logger.info(f"📊 Total unique files in index: {len(self.indexed_files)}")
        logger.info(f"💾 Index saved to: {self.kb.persist_directory}")
        logger.info("🔍 Knowledge base ready for <100ms semantic search!")
        
        return total_indexed
    
    def test_queries(self):
        """Test the index with sample queries"""
        logger.info("\n" + "=" * 60)
        logger.info("🧪 TESTING VECTOR SEARCH")
        logger.info("=" * 60)
        
        test_queries = [
            "What are our token thresholds?",
            "Who handles security reviews?",
            "How do we calculate cat protein requirements?",
            "What is the boot protocol?",
            "What's our model selection strategy?",
            "Who is Dale and what are his strengths?",
            "What are the strategic applications?",
            "How does the triumvirate work?",
            "What is OS-004?",
            "How do we handle context management?"
        ]
        
        for query in test_queries:
            logger.info(f"\n❓ Query: {query}")
            results = self.kb.search(query, top_k=1)
            if results:
                result = results[0]
                logger.info(f"✅ Found: {result['metadata']['source']}")
                logger.info(f"   Score: {result['score']:.3f}")
                logger.info(f"   Category: {result['metadata']['category']}")
                # Show first 200 chars of content
                preview = result['text'][:200].replace('\n', ' ')
                logger.info(f"   Preview: {preview}...")
            else:
                logger.warning("❌ No results found")
    
def main():
    """Main entry point for indexing script"""
    indexer = OrganizationalKnowledgeIndexer()
    
    # Run full indexing
    indexed_count = indexer.run_full_index()
    
    if indexed_count > 0:
        # Test the index with sample queries
        indexer.test_queries()
    else:
        logger.info("\n✅ All files already indexed and up-to-date!")
        logger.info("💡 Run test queries? Use: python index_organizational_knowledge.py --test")
    
    # Handle command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        indexer.test_queries()

if __name__ == "__main__":
    main()