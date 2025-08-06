#!/usr/bin/env python3
"""
Quick Journey Capture - START THE MOAT TODAY
Every conversation captured is future collective intelligence
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib

class QuickJourneyCapture:
    """Minimal viable journey capture - deployed in hours, not weeks"""
    
    def __init__(self):
        self.db_path = Path("journeys.db")
        self._init_db()
        
    def _init_db(self):
        """Simple schema - capture everything, optimize later"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS journeys (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                context TEXT NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                source TEXT DEFAULT 'direct',
                outcome TEXT,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def capture_journey(self, query: str, context: dict, response: str, source: str = "direct"):
        """THE GRAND BARGAIN BEGINS - Every capture builds the moat"""
        journey_id = hashlib.md5(f"{datetime.now()}{query}".encode()).hexdigest()[:12]
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO journeys (id, timestamp, context, query, response, source, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            journey_id,
            datetime.now().isoformat(),
            json.dumps(context),
            query,
            response,
            source,
            json.dumps({"version": "0.1", "quick_capture": True})
        ))
        conn.commit()
        conn.close()
        
        # Update daily counter
        self._update_counter()
        
        return journey_id
    
    def _update_counter(self):
        """Visible progress - 'Journeys captured today: X'"""
        today = datetime.now().date().isoformat()
        conn = sqlite3.connect(self.db_path)
        
        count = conn.execute("""
            SELECT COUNT(*) FROM journeys 
            WHERE DATE(timestamp) = ?
        """, (today,)).fetchone()[0]
        
        # Write to visible file
        Path("JOURNEY_COUNT.txt").write_text(
            f"Journeys captured today: {count}\n"
            f"Total journeys: {conn.execute('SELECT COUNT(*) FROM journeys').fetchone()[0]}\n"
            f"First journey: {conn.execute('SELECT MIN(timestamp) FROM journeys').fetchone()[0] or 'None yet'}\n"
        )
        conn.close()
    
    def get_stats(self):
        """Quick stats for validation"""
        conn = sqlite3.connect(self.db_path)
        stats = {
            "total": conn.execute("SELECT COUNT(*) FROM journeys").fetchone()[0],
            "today": conn.execute("""
                SELECT COUNT(*) FROM journeys 
                WHERE DATE(timestamp) = DATE('now')
            """).fetchone()[0],
            "sources": dict(conn.execute("""
                SELECT source, COUNT(*) FROM journeys 
                GROUP BY source
            """).fetchall())
        }
        conn.close()
        return stats


# Example wrapper for immediate use
def capture_health_conversation(query: str, response: str, context: dict = None):
    """Drop-in function to start capturing TODAY"""
    capture = QuickJourneyCapture()
    
    # Minimal context if none provided
    if context is None:
        context = {
            "type": "health_query",
            "timestamp": datetime.now().isoformat()
        }
    
    journey_id = capture.capture_journey(
        query=query,
        context=context,
        response=response,
        source="claude_wrapper"
    )
    
    print(f"✅ Journey captured: {journey_id}")
    print(f"📊 {capture.get_stats()['today']} journeys captured today")
    
    return journey_id


if __name__ == "__main__":
    # Test capture
    print("🚀 Quick Journey Capture System - STARTING THE MOAT")
    
    # Example health journey
    test_id = capture_health_conversation(
        query="My cat has been drinking more water lately, should I be concerned?",
        response="Increased water consumption in cats can indicate several conditions...",
        context={
            "pet": "cat",
            "symptom": "increased_thirst",
            "duration": "1_week"
        }
    )
    
    print(f"\n✨ First journey captured! ID: {test_id}")
    print("🏗️ The moat building has begun...")