#!/bin/bash
# Sustainable Vector Indexing Setup - NO SUDO EVER AGAIN!
# This creates a completely self-contained solution

set -e  # Exit on any error

echo "🚀 Setting up TRULY SUSTAINABLE vector indexing..."
echo "   Once this completes, you'll NEVER need sudo or manual commands again!"
echo ""

# Step 1: Create isolated Python environment
echo "📦 Creating isolated Python environment..."
python3 -m venv ~/venv/vector-db --clear

# Step 2: Activate and upgrade pip
echo "⬆️ Upgrading pip in virtual environment..."
source ~/venv/vector-db/bin/activate
python -m pip install --upgrade pip --quiet

# Step 3: Install packages IN THE VENV (no sudo!)
echo "📥 Installing ChromaDB and dependencies (this will take a few minutes)..."
pip install --quiet \
    chromadb>=0.4.22 \
    sentence-transformers>=2.2.2 \
    watchdog>=3.0.0 \
    schedule>=1.2.0

# Step 4: Create the sustainable indexer script
echo "🤖 Creating sustainable auto-indexer..."
cat > ~/venv/vector-db/bin/sustainable_indexer.py << 'EOF'
#!/usr/bin/env python3
"""
Sustainable Vector Indexer - Runs completely in user space
No sudo required, ever!
"""

import os
import sys
import time
import json
import logging
import schedule
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add module paths
sys.path.insert(0, str(Path.home() / "vibe-coding-system/os_modules/os_002_1_vector_search"))

# Set up logging
log_dir = Path.home() / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "vector-indexing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DocumentWatcher(FileSystemEventHandler):
    """Watches for document changes and triggers indexing"""
    
    def __init__(self, indexer):
        self.indexer = indexer
        self.last_index_time = 0
        self.pending_files = set()
        
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.md'):
            self.pending_files.add(event.src_path)
            
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            self.pending_files.add(event.src_path)
            
    def process_pending(self):
        """Process pending file changes"""
        if self.pending_files:
            current_time = time.time()
            # Only index if 5 minutes have passed since last index
            if current_time - self.last_index_time > 300:
                logger.info(f"📝 Indexing {len(self.pending_files)} changed files...")
                for file_path in self.pending_files:
                    try:
                        self.indexer.index_file(file_path)
                    except Exception as e:
                        logger.error(f"Failed to index {file_path}: {e}")
                self.pending_files.clear()
                self.last_index_time = current_time
                logger.info("✅ Incremental indexing complete!")

class SustainableIndexer:
    """Main indexer that works entirely in user space"""
    
    def __init__(self):
        # Import here to ensure venv packages are used
        import chromadb
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer
        
        self.base_path = Path.home() / "vibe-coding-system"
        self.db_path = self.base_path / "vector_db"
        self.db_path.mkdir(exist_ok=True)
        
        # Initialize ChromaDB with user-space directory
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                persist_directory=str(self.db_path)
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="organizational_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embedder
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Track indexed files
        self.index_state_file = self.db_path / "index_state.json"
        self.load_index_state()
        
    def load_index_state(self):
        """Load index state from disk"""
        if self.index_state_file.exists():
            with open(self.index_state_file, 'r') as f:
                self.index_state = json.load(f)
        else:
            self.index_state = {"files": {}, "last_full_index": None}
            
    def save_index_state(self):
        """Save index state to disk"""
        with open(self.index_state_file, 'w') as f:
            json.dump(self.index_state, f, indent=2)
            
    def index_file(self, file_path):
        """Index a single file"""
        file_path = Path(file_path)
        if not file_path.exists():
            return
            
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return
            
        # Generate embedding
        embedding = self.embedder.encode(content).tolist()
        
        # Add to collection
        doc_id = str(file_path)
        self.collection.upsert(
            ids=[doc_id],
            documents=[content],
            embeddings=[embedding],
            metadatas=[{
                "source": str(file_path),
                "indexed_at": datetime.now().isoformat()
            }]
        )
        
        # Update state
        self.index_state["files"][doc_id] = {
            "indexed_at": datetime.now().isoformat(),
            "size": len(content)
        }
        
    def full_index(self):
        """Run full indexing of all documents"""
        logger.info("🔍 Starting full document indexing...")
        
        # Find all markdown files
        md_files = list(Path.home().glob("**/*.md"))
        
        # Filter to important directories
        important_dirs = [
            "vibe-coding-system",
            "organization",
            "chief-of-staff",
            "specs",
            ".claude/agents"
        ]
        
        indexed_count = 0
        for md_file in md_files:
            # Check if in important directory
            if any(dir_name in str(md_file) for dir_name in important_dirs):
                try:
                    self.index_file(md_file)
                    indexed_count += 1
                except Exception as e:
                    logger.error(f"Failed to index {md_file}: {e}")
                    
        self.index_state["last_full_index"] = datetime.now().isoformat()
        self.save_index_state()
        
        logger.info(f"✅ Indexed {indexed_count} documents!")
        return indexed_count
        
    def search(self, query, top_k=5):
        """Search the vector database"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        return results

def main():
    """Main daemon loop"""
    logger.info("🚀 Sustainable Vector Indexer Started!")
    logger.info("   Running entirely in user space - no sudo needed!")
    
    # Initialize indexer
    indexer = SustainableIndexer()
    
    # Run initial full index
    indexed = indexer.full_index()
    logger.info(f"📊 Initial indexing complete: {indexed} documents")
    
    # Set up file watcher
    watcher = DocumentWatcher(indexer)
    observer = Observer()
    
    # Watch important directories
    watch_dirs = [
        Path.home() / "vibe-coding-system",
        Path.home() / "organization",
        Path.home() / "chief-of-staff",
        Path.home() / "specs"
    ]
    
    for watch_dir in watch_dirs:
        if watch_dir.exists():
            observer.schedule(watcher, str(watch_dir), recursive=True)
            logger.info(f"👁️ Watching: {watch_dir}")
    
    observer.start()
    
    # Schedule periodic full reindex (daily at 3 AM)
    schedule.every().day.at("03:00").do(indexer.full_index)
    
    # Schedule incremental index processing
    schedule.every(5).minutes.do(watcher.process_pending)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("👋 Indexer stopped gracefully")
    
    observer.join()

if __name__ == "__main__":
    main()
EOF

chmod +x ~/venv/vector-db/bin/sustainable_indexer.py

# Step 5: Create simple launcher commands
echo "🎯 Creating simple launcher commands..."
mkdir -p ~/.local/bin

cat > ~/.local/bin/vindex << 'EOF'
#!/bin/bash
# Vector Index - Simple command for vector database operations

source ~/venv/vector-db/bin/activate

case "$1" in
    start)
        echo "🚀 Starting vector indexer daemon..."
        nohup python ~/venv/vector-db/bin/sustainable_indexer.py > ~/logs/vector-daemon.log 2>&1 &
        echo $! > ~/logs/vector-indexer.pid
        echo "✅ Daemon started (PID: $(cat ~/logs/vector-indexer.pid))"
        ;;
    stop)
        if [ -f ~/logs/vector-indexer.pid ]; then
            kill $(cat ~/logs/vector-indexer.pid)
            rm ~/logs/vector-indexer.pid
            echo "✅ Daemon stopped"
        else
            echo "❌ No daemon running"
        fi
        ;;
    status)
        if [ -f ~/logs/vector-indexer.pid ] && ps -p $(cat ~/logs/vector-indexer.pid) > /dev/null; then
            echo "✅ Daemon is running (PID: $(cat ~/logs/vector-indexer.pid))"
        else
            echo "❌ Daemon is not running"
        fi
        ;;
    index)
        echo "📝 Running one-time indexing..."
        python -c "from sustainable_indexer import SustainableIndexer; indexer = SustainableIndexer(); print(f'Indexed {indexer.full_index()} documents')"
        ;;
    search)
        if [ -z "$2" ]; then
            echo "Usage: vindex search 'your query here'"
        else
            python -c "
from sustainable_indexer import SustainableIndexer
indexer = SustainableIndexer()
results = indexer.search('$2')
for doc in results['documents'][0][:3]:
    print(doc[:200] + '...')
    print('-' * 40)
"
        fi
        ;;
    *)
        echo "Vector Index Manager - Sustainable, no sudo required!"
        echo ""
        echo "Usage: vindex [command]"
        echo ""
        echo "Commands:"
        echo "  start   - Start the auto-indexing daemon"
        echo "  stop    - Stop the daemon"
        echo "  status  - Check daemon status"
        echo "  index   - Run one-time full indexing"
        echo "  search  - Search the vector database"
        echo ""
        echo "Example: vindex search 'triumvirate system'"
        ;;
esac
EOF

chmod +x ~/.local/bin/vindex

# Step 6: Add to PATH permanently
echo "🔧 Adding to PATH..."
if ! grep -q "/.local/bin" ~/.bashrc; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

# Step 7: Create systemd user service (optional)
echo "🔐 Creating auto-start service..."
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/vector-indexer.service << 'EOF'
[Unit]
Description=Vector Database Auto-Indexer
After=network.target

[Service]
Type=simple
ExecStart=/home/dthomas_unix/venv/vector-db/bin/python /home/dthomas_unix/venv/vector-db/bin/sustainable_indexer.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

echo ""
echo "✅ ✅ ✅ SETUP COMPLETE! ✅ ✅ ✅"
echo ""
echo "You now have a COMPLETELY SUSTAINABLE vector indexing system!"
echo ""
echo "🎉 Simple commands (NO SUDO REQUIRED):"
echo "   vindex start  - Start auto-indexing daemon"
echo "   vindex stop   - Stop the daemon"
echo "   vindex status - Check if running"
echo "   vindex index  - Run full index now"
echo "   vindex search 'query' - Search your knowledge"
echo ""
echo "🚀 To start indexing right now:"
echo "   source ~/.bashrc && vindex start"
echo ""
echo "The daemon will:"
echo "  • Index all documents on startup"
echo "  • Watch for new/changed files"
echo "  • Auto-index every 5 minutes"
echo "  • Full reindex daily at 3 AM"
echo "  • Work entirely in user space"
echo "  • NEVER require sudo!"
echo ""
echo "📝 Logs are in ~/logs/vector-indexing.log"