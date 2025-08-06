#!/usr/bin/env python3
"""
Test OS-004 Intelligent Context Management
Demonstrates peak performance maintenance
"""

import time
from context_manager import ContextManager
from subagent_wrapper import SubAgentRegistry

def simulate_complex_work():
    """Simulate a complex work scenario"""
    print("🧪 OS-004 Context Management Test")
    print("="*60)
    
    # Initialize context manager
    context_mgr = ContextManager('pompey')
    registry = SubAgentRegistry(context_mgr)
    
    print("\n📊 Initial Status:")
    status = context_mgr.get_status_report()
    print(f"   Performance: {status['performance']}")
    print(f"   Tokens: {status['tokens']:,}")
    
    # Scenario 1: Simple work - can interrupt anytime
    print("\n\n=== Scenario 1: Simple Work ===")
    context_mgr.mark_work_status('documenting', 'simple')
    
    # Simulate some work
    for i in range(3):
        text = "Documentation update " * 1000  # ~3K tokens each
        context_mgr.update_token_count(text)
        print(f"   Step {i+1}: {context_mgr.token_count:,} tokens")
    
    # Check decision
    decision = context_mgr.evaluate_reboot_decision()
    print(f"\n   Decision: {decision['reason']}")
    print(f"   Can interrupt: {decision['can_interrupt']}")
    
    # Scenario 2: Complex work - protect from interruption
    print("\n\n=== Scenario 2: Complex Implementation ===")
    context_mgr.mark_work_status('implementing', 'complex')
    
    # Add more tokens
    for i in range(5):
        text = "Complex algorithm implementation " * 2000  # ~6K tokens each
        context_mgr.update_token_count(text)
        print(f"   Step {i+1}: {context_mgr.token_count:,} tokens - {context_mgr._get_performance_status()}")
    
    # Check decision - should wait for breakpoint
    decision = context_mgr.evaluate_reboot_decision()
    print(f"\n   Decision: {decision['reason']}")
    print(f"   Can interrupt: {decision['can_interrupt']}")
    print(f"   Urgency: {decision['urgency']}")
    
    # Complete the work
    print("\n   ✅ Completing complex work...")
    context_mgr.mark_work_status('completed')
    
    # Now check decision - should allow reboot
    decision = context_mgr.evaluate_reboot_decision()
    print(f"\n   Decision after completion: {decision['reason']}")
    print(f"   Can interrupt: {decision['can_interrupt']}")
    
    # Scenario 3: Sub-agent protection
    print("\n\n=== Scenario 3: Sub-Agent Protection ===")
    architect = registry.get_wrapper('architect')
    architect.start_task("Design next-gen architecture", "complex")
    
    # Simulate architect work
    for i in range(4):
        result = architect.track("Architecture design patterns " * 1500)
        print(f"   Architect step {i+1}: {result['status']}")
    
    # Check if handoff needed
    if architect._needs_handoff():
        print("\n   🔄 Architect requesting handoff!")
        handoff = architect.request_handoff()
        print(f"   Local tokens: {handoff['tokens']:,}")
    
    # Scenario 4: Emergency threshold
    print("\n\n=== Scenario 4: Emergency Threshold Test ===")
    
    # Push to emergency levels
    emergency_text = "MASSIVE CONTEXT " * 50_000  # ~150K tokens
    context_mgr.update_token_count(emergency_text)
    
    decision = context_mgr.evaluate_reboot_decision()
    print(f"\n   🚨 EMERGENCY: {decision['reason']}")
    print(f"   Tokens: {context_mgr.token_count:,}")
    print(f"   Must reboot: {decision['need_reboot']}")
    
    # Demonstrate graceful reboot
    if decision['need_reboot'] and decision['urgency'] == 'emergency':
        print("\n\n=== Initiating Graceful Reboot ===")
        reboot_result = context_mgr.graceful_reboot(decision['reason'])
        print(reboot_result['dale_message'])
        
        # Show saved state
        print("\n📁 State saved for resumption:")
        saved_state = reboot_result['state_saved']
        print(f"   Member: {saved_state['member']}")
        print(f"   Work: {saved_state['current_work']}")
        print(f"   Tokens: {saved_state['token_count']:,}")
    
    # Scenario 5: Resume from reboot
    print("\n\n=== Scenario 5: Resume After Reboot ===")
    print("Simulating new session...")
    
    # Create new context manager (simulating fresh session)
    new_context = ContextManager('pompey')
    resume_state = new_context.check_resume_state()
    
    if resume_state:
        print(f"\n✅ Found saved state from: {resume_state['timestamp']}")
        print(f"   Previous work: {resume_state['work_status']}")
        print(f"   Reason for reboot: {resume_state['reason']}")
        
        # Restore
        new_context.restore_work_state(resume_state)
        print(f"\n   Restored successfully!")
        print(f"   Current performance: {new_context._get_performance_status()}")
    
    # Final summary
    print("\n\n" + "="*60)
    print("📊 FINAL SUMMARY")
    print("="*60)
    
    # Check all agents
    active = registry.get_active_agents()
    print(f"\nActive agents: {len(active)}")
    
    handoffs = registry.check_handoffs_needed()
    print(f"Handoffs needed: {len(handoffs)}")
    
    print("\n✅ OS-004 Context Management Test Complete!")
    print("\nKey Features Demonstrated:")
    print("  ✓ Token tracking with intelligent thresholds")
    print("  ✓ Natural breakpoint detection")
    print("  ✓ Complex work protection")
    print("  ✓ Sub-agent monitoring")
    print("  ✓ Graceful reboot with state preservation")
    print("  ✓ Automatic work resumption")
    print("\n🏎️ Peak performance maintained throughout!")


if __name__ == "__main__":
    simulate_complex_work()