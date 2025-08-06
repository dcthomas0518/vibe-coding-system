#!/usr/bin/env python3
"""
Internal Memory System - The Collective Soul of the AI Organization
Where CTO discoveries flow to Creative Director, Crassus wisdom influences Pompey
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import jsonschema

class OrganizationalMemory:
    """The collective soul where all entities share knowledge"""
    
    def __init__(self):
        self.db_path = Path("organizational_memory.db")
        self.schema_path = Path("schemas/internal_memory_schema_v01.json")
        self.schema = self._load_schema()
        self._init_db()
        
    def _load_schema(self) -> dict:
        """Load and validate the memory schema"""
        with open(self.schema_path) as f:
            return json.load(f)
    
    def _init_db(self):
        """Initialize the collective memory database"""
        conn = sqlite3.connect(self.db_path)
        
        # Main memory table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                version TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_name TEXT NOT NULL,
                entity_mode TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_category TEXT NOT NULL,
                event_description TEXT NOT NULL,
                event_significance TEXT DEFAULT 'routine',
                session_id TEXT,
                project TEXT,
                memory_json TEXT NOT NULL
            )
        """)
        
        # Connections table for memory relationships
        conn.execute("""
            CREATE TABLE IF NOT EXISTS connections (
                from_memory TEXT NOT NULL,
                to_memory TEXT NOT NULL,
                connection_type TEXT NOT NULL,
                FOREIGN KEY (from_memory) REFERENCES memories(id),
                FOREIGN KEY (to_memory) REFERENCES memories(id)
            )
        """)
        
        # Entity relationships
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entity_relationships (
                memory_id TEXT NOT NULL,
                entity_name TEXT NOT NULL,
                relationship TEXT NOT NULL,
                FOREIGN KEY (memory_id) REFERENCES memories(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_memory(self, 
                     entity: Dict[str, str],
                     event: Dict[str, str],
                     content: Optional[Dict] = None,
                     context: Optional[Dict] = None,
                     connections: Optional[Dict] = None,
                     outcome: Optional[Dict] = None,
                     metadata: Optional[Dict] = None) -> str:
        """Create a new organizational memory"""
        
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Build memory object
        memory = {
            "id": memory_id,
            "timestamp": timestamp,
            "version": "0.1.0",
            "entity": entity,
            "event": event,
            "connections": connections or {"influences": [], "influenced_by": []},
            "context": context or {},
            "content": content or {},
            "outcome": outcome or {"status": "pending"},
            "metadata": metadata or {}
        }
        
        # Validate against schema
        jsonschema.validate(memory, self.schema)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO memories (
                id, timestamp, version, entity_type, entity_name, entity_mode,
                event_type, event_category, event_description, event_significance,
                session_id, project, memory_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory_id, timestamp, memory["version"],
            entity["type"], entity["name"], entity["mode"],
            event["type"], event["category"], event["description"],
            event.get("significance", "routine"),
            context.get("session_id"),
            context.get("project"),
            json.dumps(memory)
        ))
        
        # Store connections
        if connections:
            for influenced_id in connections.get("influences", []):
                conn.execute("""
                    INSERT INTO connections (from_memory, to_memory, connection_type)
                    VALUES (?, ?, 'influences')
                """, (memory_id, influenced_id))
            
            for influenced_by_id in connections.get("influenced_by", []):
                conn.execute("""
                    INSERT INTO connections (from_memory, to_memory, connection_type)
                    VALUES (?, ?, 'influenced_by')
                """, (influenced_by_id, memory_id))
        
        conn.commit()
        conn.close()
        
        # Update visible metrics
        self._update_metrics()
        
        return memory_id
    
    def _update_metrics(self):
        """Update visible memory metrics"""
        conn = sqlite3.connect(self.db_path)
        
        # Get stats
        total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        
        entities = conn.execute("""
            SELECT entity_name, entity_mode, COUNT(*) as count 
            FROM memories 
            GROUP BY entity_name, entity_mode
        """).fetchall()
        
        event_types = conn.execute("""
            SELECT event_type, COUNT(*) as count 
            FROM memories 
            GROUP BY event_type
        """).fetchall()
        
        # Write metrics file
        metrics_text = f"""ORGANIZATIONAL MEMORY METRICS
============================
Total Memories: {total}
Generated: {datetime.now().isoformat()}

Memories by Entity:
"""
        for entity_name, entity_mode, count in entities:
            metrics_text += f"  {entity_name} ({entity_mode}): {count}\n"
        
        metrics_text += "\nMemories by Type:\n"
        for event_type, count in event_types:
            metrics_text += f"  {event_type}: {count}\n"
        
        Path("MEMORY_METRICS.txt").write_text(metrics_text)
        conn.close()
    
    def find_related_memories(self, entity_name: str = None, 
                            entity_mode: str = None,
                            project: str = None) -> List[Dict]:
        """Find memories that might influence current context"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT memory_json FROM memories WHERE 1=1"
        params = []
        
        if entity_name:
            query += " AND entity_name = ?"
            params.append(entity_name)
        
        if entity_mode:
            query += " AND entity_mode = ?"
            params.append(entity_mode)
        
        if project:
            query += " AND project = ?"
            params.append(project)
        
        query += " ORDER BY timestamp DESC LIMIT 20"
        
        results = conn.execute(query, params).fetchall()
        conn.close()
        
        return [json.loads(row[0]) for row in results]
    
    def capture_strategic_pivot(self):
        """Capture THIS conversation as our first organizational memory"""
        return self.create_memory(
            entity={
                "type": "pompey",
                "name": "Pompey",
                "mode": "CTO"
            },
            event={
                "type": "discovery",
                "category": "strategic",
                "description": "Strategic pivot to build Internal Memory System first - OS collective soul before external journeys",
                "significance": "critical"
            },
            content={
                "insight": "The OS needs a collective soul where knowledge flows between entities and modes",
                "rationale": "Internal memory enables CTO discoveries to flow to Creative Director, Crassus wisdom to influence implementations",
                "data": {
                    "pivot_order": [
                        "Internal Memory System (collective soul)",
                        "Cat nutrition journeys",
                        "Cancer therapy scale",
                        "Never: general health"
                    ]
                }
            },
            context={
                "session_id": "2025-08-05-evening",
                "project": "OS-001",
                "external_references": [
                    "schemas/internal_memory_schema_v01.json",
                    "schemas/journey_schema_v01.json"
                ]
            },
            metadata={
                "confidence": 1.0,
                "tags": ["strategic_pivot", "internal_memory", "collective_soul"]
            }
        )


# Example: Memory flow between modes
def demonstrate_memory_flow():
    """Show how memories flow between CTO and Creative Director modes"""
    memory = OrganizationalMemory()
    
    # 1. CTO discovers something
    cto_memory_id = memory.create_memory(
        entity={"type": "pompey", "name": "Pompey", "mode": "CTO"},
        event={
            "type": "discovery",
            "category": "technical",
            "description": "Journey capture system can start collecting data immediately with simple SQLite"
        },
        content={
            "insight": "Quick wins build momentum - deploy basic capture TODAY",
            "data": {"implementation": "quick_capture.py", "first_journey": "70176757a84d"}
        },
        context={"session_id": "demo", "project": "OS-001"}
    )
    
    # 2. Creative Director uses CTO's discovery
    creative_memory_id = memory.create_memory(
        entity={"type": "pompey", "name": "Pompey", "mode": "Creative_Director"},
        event={
            "type": "creation",
            "category": "creative",
            "description": "Create content showing journey capture building the moat in real-time"
        },
        connections={
            "influenced_by": [cto_memory_id],
            "influences": []
        },
        content={
            "insight": "Visual demonstration of moat-building resonates with audience",
            "rationale": "CTO's quick capture system provides perfect content hook"
        },
        context={"session_id": "demo", "project": "OS-001"}
    )
    
    print(f"✅ CTO Memory: {cto_memory_id}")
    print(f"✅ Creative Memory: {creative_memory_id}")
    print(f"🔄 Knowledge flowed from CTO → Creative Director!")
    
    # Show related memories
    related = memory.find_related_memories(entity_name="Pompey")
    print(f"\n📚 Found {len(related)} Pompey memories across all modes")


if __name__ == "__main__":
    print("🧠 Organizational Memory System - Building the Collective Soul")
    
    # Capture our strategic pivot
    memory = OrganizationalMemory()
    pivot_id = memory.capture_strategic_pivot()
    print(f"\n✨ First organizational memory captured: {pivot_id}")
    
    # Demonstrate memory flow
    print("\n🔄 Demonstrating memory flow between modes...")
    demonstrate_memory_flow()