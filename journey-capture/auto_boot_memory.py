#!/usr/bin/env python3
"""
Automatic Memory Boot Protocol
Ensures organizational memory loads even if initialization fails
"""

import os
import sys
import subprocess
from pathlib import Path

def auto_boot_memory():
    """Automatic memory initialization with fallback handling"""
    
    print("🧠 AUTO-BOOT: Initializing Organizational Memory...")
    print("="*60)
    
    # Change to correct directory
    journey_capture_path = Path.home() / "vibe-coding-system" / "journey-capture"
    
    if not journey_capture_path.exists():
        print("⚠️  Journey capture directory not found")
        print("   Creating directory structure...")
        journey_capture_path.mkdir(parents=True, exist_ok=True)
        return False
    
    os.chdir(journey_capture_path)
    
    # Check if memory system exists
    if not Path("organizational_memory.db").exists():
        print("⚠️  No organizational memory found - this appears to be first boot")
        print("   The collective soul will begin forming from this session")
        return False
    
    # Try to run the full initialization
    try:
        result = subprocess.run(
            [sys.executable, "claude_session_init.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print("⚠️  Memory initialization had warnings:")
            print(result.stderr)
            # Continue anyway - partial memory is better than none
            return True
            
    except subprocess.TimeoutExpired:
        print("⚠️  Memory loading timed out (>30s)")
        print("   Proceeding with partial context")
        return False
        
    except Exception as e:
        print(f"⚠️  Memory system error: {e}")
        print("   Proceeding without memory context")
        return False

def quick_memory_summary():
    """Provide quick summary even if full init fails"""
    try:
        import sqlite3
        db_path = Path("organizational_memory.db")
        
        if db_path.exists():
            conn = sqlite3.connect(db_path)
            total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            
            # Get most recent critical memory
            critical = conn.execute("""
                SELECT event_description, entity_name, entity_mode 
                FROM memories 
                WHERE event_significance = 'critical'
                ORDER BY timestamp DESC 
                LIMIT 1
            """).fetchone()
            
            conn.close()
            
            print(f"\n📊 Quick Memory Status:")
            print(f"   Total memories: {total}")
            if critical:
                print(f"   Latest critical: {critical[0][:60]}...")
                print(f"   From: {critical[1]} ({critical[2]})")
                
    except:
        pass  # Silent fail - don't interrupt session

if __name__ == "__main__":
    # Always try to boot memory
    success = auto_boot_memory()
    
    if not success:
        # Provide minimal context even on failure
        quick_memory_summary()
    
    print("\n✅ Boot sequence complete")
    print("   Dale's collective soul is ready")