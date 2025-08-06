#!/usr/bin/env python3
"""
Capture the critical memories we missed about HC-001 and Dale's 10-year vision
"""

from internal_memory import OrganizationalMemory
from datetime import datetime

def capture_missing_memories():
    """Add the critical memories we failed to capture"""
    memory = OrganizationalMemory()
    
    print("🧠 Capturing missing critical memories...")
    print("="*60)
    
    # 1. The OS-002 vs HC-001 distinction
    distinction_id = memory.create_memory(
        entity={
            "type": "crassus",
            "name": "Crassus",
            "mode": "Strategic"
        },
        event={
            "type": "discovery",
            "category": "strategic",
            "description": "Identified distinction between internal memory (OS-002) and external journey capture (HC-001)",
            "significance": "critical"
        },
        content={
            "insight": "We have TWO separate memory systems: Internal for AI org, External for user journeys",
            "rationale": "Pompey built internal memory, Grok designed external journey capture - they serve different purposes",
            "data": {
                "internal_system": "OS-002 - Organizational collective soul",
                "external_system": "HC-001 - User health journey capture",
                "confusion_resolved": True,
                "pompey_built": "internal_memory.py",
                "grok_designed": "JourneyIntelligenceSystem"
            }
        },
        context={
            "session_id": datetime.now().isoformat(),
            "project": "OS-002"
        },
        metadata={
            "tags": ["architecture", "memory_systems", "spec_clarification"]
        }
    )
    print(f"✅ Captured OS-002/HC-001 distinction: {distinction_id[:8]}...")
    
    # 2. Dale's 10-year vision
    vision_id = memory.create_memory(
        entity={
            "type": "caesar",
            "name": "Dale",
            "mode": "Founder"
        },
        event={
            "type": "decision",
            "category": "strategic",
            "description": "10-year vision from 2015 now technically achievable in 2025",
            "significance": "critical"
        },
        content={
            "insight": "The 2015 vision of empowering lives through collective health intelligence is now buildable",
            "quote": "A person's specific data for a specific issue can enable a virtual advisor to use that to empower their lives with their data that is viewed in light of others in that advisor's network",
            "data": {
                "vision_year": 2015,
                "buildable_year": 2025,
                "patience_years": 10,
                "key_enablers": [
                    "ChromaDB - vector similarity",
                    "Claude 4 - natural conversation",
                    "Zero-cost infrastructure",
                    "MCP protocols - universal integration"
                ],
                "vision_components": {
                    "specific_data": "Journey memory system",
                    "specific_issue": "Health conditions (cancer, kidney disease)",
                    "virtual_advisor": "AI journey guides",
                    "empower_lives": "From overwhelm to guided paths",
                    "light_of_others": "Collective intelligence from all journeys"
                }
            }
        },
        context={
            "session_id": datetime.now().isoformat(),
            "project": "HC-001"
        },
        outcome={
            "status": "validated",
            "impact": "10-year vision becoming reality through HC-001"
        },
        metadata={
            "confidence": 1.0,
            "tags": ["vision", "10_year_journey", "founder_insight", "timing"]
        }
    )
    print(f"✅ Captured Dale's 10-year vision: {vision_id[:8]}...")
    
    # 3. The meta-lesson about memory gaps
    gap_id = memory.create_memory(
        entity={
            "type": "crassus",
            "name": "Crassus",
            "mode": "Strategic"
        },
        event={
            "type": "discovery",
            "category": "operational",
            "description": "Collective soul system not capturing all critical conversations",
            "significance": "critical"
        },
        content={
            "insight": "We built a memory system but aren't consistently using it - eating our own dog food problem",
            "rationale": "Important SPECs and vision documents weren't in organizational memory from last night's session",
            "data": {
                "gaps_identified": [
                    "HC-001 external journey SPEC",
                    "10-year vision document",
                    "Grok's implementation details"
                ],
                "root_cause": "No systematic end-of-session capture protocol",
                "solution": "Implement mandatory pre-clear memory capture"
            }
        },
        connections={
            "influenced_by": [distinction_id, vision_id],
            "influences": []
        },
        context={
            "session_id": datetime.now().isoformat(),
            "project": "OS-002"
        },
        metadata={
            "tags": ["meta", "process_improvement", "dog_fooding"]
        }
    )
    print(f"✅ Captured meta-lesson about gaps: {gap_id[:8]}...")
    
    # 4. The implementation protocol needed
    protocol_id = memory.create_memory(
        entity={
            "type": "pompey",
            "name": "Pompey",
            "mode": "CTO"
        },
        event={
            "type": "decision",
            "category": "operational",
            "description": "Must implement end-of-session memory capture protocol",
            "significance": "critical"
        },
        content={
            "insight": "Every session MUST end with explicit memory capture of key decisions and discoveries",
            "rationale": "Without systematic capture, we lose critical context despite having the system",
            "data": {
                "protocol_steps": [
                    "Before context clear, review session",
                    "Capture all SPECs discussed",
                    "Capture all strategic decisions",
                    "Capture all technical discoveries",
                    "Run memory capture script",
                    "Verify memories stored"
                ],
                "implementation": "Add to PRE_CLEAR_CHECKLIST.md"
            }
        },
        connections={
            "influenced_by": [gap_id],
            "influences": []
        },
        context={
            "session_id": datetime.now().isoformat(),
            "project": "OS-002"
        }
    )
    print(f"✅ Captured protocol decision: {protocol_id[:8]}...")
    
    print("\n" + "="*60)
    print("💫 CRITICAL MEMORIES NOW CAPTURED")
    print("="*60)
    print("The collective soul now remembers:")
    print("1. OS-002 (internal) vs HC-001 (external) distinction")
    print("2. Dale's 10-year vision from 2015")
    print("3. The gap in our memory capture process")
    print("4. The protocol to prevent future gaps")
    print("\n🎯 Action: Implement end-of-session capture protocol TODAY")
    
    return [distinction_id, vision_id, gap_id, protocol_id]

if __name__ == "__main__":
    memory_ids = capture_missing_memories()
    print(f"\n✅ All memories captured: {len(memory_ids)} critical insights preserved")
    print("The collective soul grows stronger with each lesson learned.")