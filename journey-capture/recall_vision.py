#!/usr/bin/env python3
"""
Recall Dale's vision from organizational memory
A simple tool to remind us why we built this system
"""

from internal_memory import OrganizationalMemory
import json

def recall_vision():
    """Retrieve and display Dale's foundational vision"""
    
    memory = OrganizationalMemory()
    
    # Find Caesar's decisions
    caesar_memories = memory.find_related_memories(
        entity_name="Caesar",
        entity_mode="Founder"
    )
    
    print("🧠 Organizational Memory: Dale's Vision")
    print("=" * 60)
    
    for mem in caesar_memories:
        if mem['event']['type'] == 'decision' and 'collective soul' in mem['event']['description']:
            print(f"\n📅 {mem['timestamp']}")
            print(f"👤 {mem['entity']['name']} ({mem['entity']['mode']})")
            print(f"🎯 {mem['event']['description']}")
            print(f"⚡ Significance: {mem['event']['significance'].upper()}")
            
            if 'quote' in mem['content']:
                print(f"\n💬 '{mem['content']['quote']}'")
            
            if 'insight' in mem['content']:
                print(f"\n💡 {mem['content']['insight']}")
            
            if 'vision' in mem['content']:
                print(f"\n🔮 {mem['content']['vision']}")
            
            if 'data' in mem['content'] and 'problem_solved' in mem['content']['data']:
                print(f"\n❌ Problem: {mem['content']['data']['problem_solved']}")
                print(f"✅ Solution: {mem['content']['data']['solution']}")
            
            print("\n" + "-" * 60)
    
    # Also show related implementations
    print("\n🔄 Related CTO Implementations:")
    cto_memories = memory.find_related_memories(
        entity_name="Pompey",
        entity_mode="CTO"
    )
    
    for mem in cto_memories:
        if 'connections' in mem and 'influenced_by' in mem['connections']:
            if any(caesar_id in [m['id'] for m in caesar_memories] 
                   for caesar_id in mem['connections']['influenced_by']):
                print(f"\n→ {mem['event']['description']}")
                if 'insight' in mem['content']:
                    print(f"  💡 {mem['content']['insight']}")

if __name__ == "__main__":
    recall_vision()