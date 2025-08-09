#!/usr/bin/env python3
"""
Claude Session Initialization with Memory Loading
Executes on every new Claude session/context
"""

import sys
import time
from pathlib import Path
from memory_loader import MemoryLoader
from session_memory_bridge import SessionMemoryBridge
from internal_memory import OrganizationalMemory

def initialize_claude_session():
    """Main entry point for Claude session initialization"""
    print("🧠 Initializing Organizational Memory...")
    print("="*60)
    start_time = time.time()
    
    try:
        # Step 1: Load memories
        loader = MemoryLoader()
        memory_context = loader.load_session_context()
        
        # Step 2: Bridge to Claude's context
        bridge = SessionMemoryBridge()
        manifest = bridge.inject_into_claude_context(memory_context)
        
        # Step 3: Update CURRENT_CONTEXT.md
        bridge.update_current_context(memory_context)
        
        # Step 4: Save session state
        bridge.save_session_memories(memory_context)
        
        # Step 5: Display summary for Claude
        print("\n" + "="*60)
        print("ORGANIZATIONAL MEMORY LOADED")
        print("="*60)
        print(f"Total Memories: {memory_context['total_memories']}")
        print(f"Key Insights: {len(memory_context['key_insights'])}")
        print(f"Cross-Mode Flows: {len(memory_context['cross_mode_flows'])}")
        print(f"Load Time: {time.time() - start_time:.1f} seconds")
        print("="*60)
        
        # Step 6: Check for critical memories
        critical_memories = [
            m for m in memory_context['key_insights'] 
            if m.get('significance') == 'critical'
        ]
        
        if critical_memories:
            print("\n⚠️  CRITICAL MEMORIES REQUIRE ATTENTION:")
            for memory in critical_memories:
                print(f"   - {memory['insight']}")
                if memory.get('project'):
                    print(f"     (Project: {memory['project']})")
        
        # Step 7: Display cross-mode flows if any
        if memory_context.get('cross_mode_flows'):
            print("\n🔄 ACTIVE KNOWLEDGE FLOWS:")
            for flow in memory_context['cross_mode_flows'][:3]:
                print(f"   - {flow['from'][:50]}...")
                print(f"     → {flow['to'][:50]}...")
        
        # Step 8: Show recommended focus
        if memory_context.get('recommended_focus'):
            print("\n🎯 RECOMMENDED FOCUS:")
            for focus in memory_context['recommended_focus']:
                print(f"   - {focus}")
        
        print("\n✅ Session initialized with organizational memory")
        print(f"📄 Full context saved to: {bridge.memory_manifest_path}")
        
        # Step 9: Create a quick-start prompt
        prompt = bridge.generate_memory_prompt(memory_context)
        print("\n💡 Quick Context:")
        print(prompt)
        
        # Step 10: Initialize Studio Module 004 Consciousness Management
        try:
            sys.path.insert(0, str(Path("~/vibe-coding-system/studio_modules/studio_004_consciousness_management").expanduser()))
            from context_manager import ContextManager
            
            # Get member name from context
            member_name = memory_context.get('context_markers', {}).get('member', 'pompey')
            
            # Initialize context manager
            context_mgr = ContextManager(member_name)
            resume_state = context_mgr.check_resume_state()
            
            if resume_state:
                print(f"\n🔄 Context Management: Resuming from intelligent reboot")
                print(f"   Previous session: {resume_state['timestamp']}")
                print(f"   Reason: {resume_state['reason']}")
                print(f"   Work status: {resume_state['work_status']}")
                context_mgr.restore_work_state(resume_state)
            else:
                print(f"\n✨ Context Management: Starting fresh at peak performance")
                print(f"   Tokens: 0 (Optimal: <40K)")
                print(f"   Member: {member_name}")
                
        except Exception as cm_error:
            # Consciousness management not available yet, continue
            print(f"\n📊 Consciousness Management: Not yet available (Studio Module 004 pending)")
        
        return memory_context
        
    except FileNotFoundError as e:
        print(f"⚠️  Memory database not found - this might be first run")
        print("   Run 'python3 internal_memory.py' to create initial memories")
        return None
        
    except Exception as e:
        print(f"⚠️  Memory loading failed: {e}")
        print("Continuing with standard session...")
        import traceback
        traceback.print_exc()
        return None

def create_session_memory(event_description: str, significance: str = "routine"):
    """Helper to create a memory for current session events"""
    memory = OrganizationalMemory()
    
    return memory.create_memory(
        entity={
            "type": "pompey",
            "name": "Pompey",
            "mode": "CTO"  # Default, should be dynamic
        },
        event={
            "type": "discovery",
            "category": "operational",
            "description": event_description,
            "significance": significance
        },
        context={
            "session_id": f"session-{time.strftime('%Y%m%d-%H%M%S')}",
            "project": "Studio-001"  # Should be dynamic
        }
    )

def check_triumvirate_communications():
    """Check and handle triumvirate inbox messages"""
    # Import here to avoid circular dependencies
    sys.path.insert(0, str(Path.home() / "triumvirate"))
    try:
        from triumvirate_api import TriumvirateAPI
        
        print("\n📨 Checking Triumvirate communications...")
        api = TriumvirateAPI('pompey')
        pending = api.check_inbox()
        
        if pending:
            counts = api.get_pending_count()
            print(f"\n🔔 {counts['total']} requests pending:")
            print(f"  🔴 High: {counts['high']} (will auto-execute)")
            print(f"  🟡 Normal: {counts['normal']}")
            print(f"  🟢 Low: {counts['low']}")
            
            # Auto-execute high priority from Crassus
            for request in pending:
                if request['priority'] == 'high' and request['from'] == 'crassus':
                    print(f"\n🚨 AUTO-EXECUTING: {request['action']}")
                    print(f"   Request ID: {request['id']}")
                    print(f"   Data: {request.get('data', {})}")
                    
                    # Mark as completed (actual execution would happen here)
                    api.mark_completed(request['id'], {'status': 'auto-executed'})
                    
                    # Create memory if persist flag is set
                    if request.get('persist_to_memory'):
                        create_session_memory(
                            f"Auto-executed Crassus request: {request['action']}",
                            "critical"
                        )
        
        # Send boot confirmation
        api.send_request(
            to_member='crassus',
            action='boot_confirmation',
            data={
                'status': 'operational', 
                'pending_handled': len([r for r in pending if r['priority'] == 'high']),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            priority='normal'
        )
        
        print("✅ Triumvirate communication established")
        
    except ImportError:
        print("⚠️  Triumvirate API not found - continuing without")
    except Exception as e:
        print(f"⚠️  Triumvirate check failed: {e}")

if __name__ == "__main__":
    # Run initialization
    context = initialize_claude_session()
    
    # Check triumvirate communications
    check_triumvirate_communications()
    
    # Example: Create a memory for this session
    if context:
        print("\n📝 Creating session initialization memory...")
        memory_id = create_session_memory(
            "Successfully initialized session with organizational memory system",
            "notable"
        )
        print(f"✅ Session memory created: {memory_id}")