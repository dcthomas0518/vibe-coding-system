#!/usr/bin/env python3
"""
OS-004: Sub-Agent Context Protection
Keeps all 22 specialists at peak performance
"""

from typing import Dict, Optional, List
from datetime import datetime
from context_manager import ContextManager


class SubAgentContextWrapper:
    """Protects all 22 specialists from brain fog"""
    
    # All protected specialists
    PROTECTED_AGENTS = [
        # Technical specialists (10)
        'architect', 'dev-lead', 'backend-dev', 'frontend-dev',
        'data-engineer', 'devops', 'qa-engineer', 'security',
        'perf-engineer', 'tech-writer',
        
        # Financial specialists (4)
        'capital-allocator', 'unit-economist', 
        'investment-analyst', 'value-auditor',
        
        # Creative specialists (8)
        'video-producer', 'copywriter', 'thumbnail-designer',
        'audience-analyst', 'growth-hacker', 'brand-strategist',
        'campaign-manager', 'movement-builder'
    ]
    
    def __init__(self, agent_name: str, parent_manager: ContextManager):
        """Initialize wrapper for a specific sub-agent"""
        self.agent_name = agent_name
        self.parent_manager = parent_manager
        self.local_tokens = 0
        self.task_start = None
        self.current_task = None
        
        # Agent-specific thresholds (lower than main)
        self.AGENT_OPTIMAL = 20_000
        self.AGENT_WARNING = 30_000
        self.AGENT_CRITICAL = 40_000
    
    def track(self, text: str) -> Dict[str, any]:
        """Track tokens for this sub-agent"""
        tokens = self.parent_manager.estimate_tokens(text)
        self.local_tokens += tokens
        
        # Also update parent
        self.parent_manager.update_token_count(text, {
            'sub_agent': self.agent_name,
            'sub_task': self.current_task
        })
        
        # Check if handoff needed
        status = self._check_agent_performance()
        
        return {
            'agent': self.agent_name,
            'local_tokens': self.local_tokens,
            'total_tokens': self.parent_manager.token_count,
            'status': status,
            'needs_handoff': self._needs_handoff()
        }
    
    def start_task(self, task_description: str, complexity: str = 'normal'):
        """Mark start of a sub-agent task"""
        self.task_start = datetime.now()
        self.current_task = task_description
        self.local_tokens = 0  # Reset for new task
        
        # Notify parent
        self.parent_manager.mark_work_status('sub_agent_active', complexity)
        
        print(f"🤖 {self.agent_name}: Starting task - {task_description}")
        print(f"   Complexity: {complexity}")
        print(f"   Parent tokens: {self.parent_manager.token_count:,}")
    
    def complete_task(self, result: Optional[str] = None):
        """Mark task completion"""
        duration = (datetime.now() - self.task_start).seconds if self.task_start else 0
        
        print(f"✅ {self.agent_name}: Task completed")
        print(f"   Duration: {duration}s")
        print(f"   Tokens used: {self.local_tokens:,}")
        
        # This is a natural breakpoint
        self.parent_manager.mark_work_status('sub_agent_complete')
        
        # Reset
        self.current_task = None
        self.task_start = None
        
        return {
            'agent': self.agent_name,
            'task': self.current_task,
            'duration': duration,
            'tokens_used': self.local_tokens,
            'result': result
        }
    
    def request_handoff(self) -> Dict[str, any]:
        """Request handoff to fresh context"""
        print(f"🔄 {self.agent_name}: Requesting handoff")
        print(f"   Reason: Approaching token limit")
        print(f"   Local tokens: {self.local_tokens:,}")
        
        handoff_data = {
            'agent': self.agent_name,
            'task': self.current_task,
            'tokens': self.local_tokens,
            'timestamp': datetime.now().isoformat(),
            'parent_tokens': self.parent_manager.token_count
        }
        
        # Save state for continuation
        self.parent_manager.save_session_state(
            f"Sub-agent {self.agent_name} handoff requested",
            handoff_data
        )
        
        return handoff_data
    
    def _check_agent_performance(self) -> str:
        """Check sub-agent performance status"""
        if self.local_tokens < self.AGENT_OPTIMAL:
            return "✨ Peak Performance"
        elif self.local_tokens < self.AGENT_WARNING:
            return "⚡ Good Performance"
        elif self.local_tokens < self.AGENT_CRITICAL:
            return "⚠️ Degraded - Consider handoff"
        else:
            return "🔴 Critical - Handoff needed"
    
    def _needs_handoff(self) -> bool:
        """Determine if handoff is needed"""
        # Local limit exceeded
        if self.local_tokens > self.AGENT_WARNING:
            return True
            
        # Parent approaching limits
        parent_decision = self.parent_manager.evaluate_reboot_decision()
        if parent_decision['urgency'] in ['critical', 'emergency']:
            return True
            
        return False
    
    def get_agent_status(self) -> Dict[str, any]:
        """Get comprehensive agent status"""
        return {
            'agent': self.agent_name,
            'active': self.current_task is not None,
            'current_task': self.current_task,
            'local_tokens': self.local_tokens,
            'performance': self._check_agent_performance(),
            'needs_handoff': self._needs_handoff(),
            'parent_tokens': self.parent_manager.token_count,
            'parent_performance': self.parent_manager._get_performance_status()
        }


class SubAgentRegistry:
    """Registry for all sub-agent wrappers"""
    
    def __init__(self, parent_manager: ContextManager):
        self.parent_manager = parent_manager
        self.agents = {}
        
        # Initialize all 22 agents
        for agent in SubAgentContextWrapper.PROTECTED_AGENTS:
            self.agents[agent] = SubAgentContextWrapper(agent, parent_manager)
    
    def get_wrapper(self, agent_name: str) -> SubAgentContextWrapper:
        """Get wrapper for specific agent"""
        if agent_name not in self.agents:
            # Create on demand for any new agents
            self.agents[agent_name] = SubAgentContextWrapper(agent_name, self.parent_manager)
        
        return self.agents[agent_name]
    
    def get_all_status(self) -> List[Dict]:
        """Get status of all agents"""
        return [
            wrapper.get_agent_status() 
            for wrapper in self.agents.values()
        ]
    
    def get_active_agents(self) -> List[str]:
        """Get list of currently active agents"""
        return [
            name for name, wrapper in self.agents.items()
            if wrapper.current_task is not None
        ]
    
    def check_handoffs_needed(self) -> List[Dict]:
        """Check which agents need handoff"""
        handoffs = []
        for name, wrapper in self.agents.items():
            if wrapper._needs_handoff() and wrapper.current_task:
                handoffs.append({
                    'agent': name,
                    'task': wrapper.current_task,
                    'tokens': wrapper.local_tokens,
                    'reason': wrapper._check_agent_performance()
                })
        
        return handoffs


# Integration helper
def wrap_subagent_task(context_manager: ContextManager, agent_name: str, 
                       task: str, complexity: str = 'normal'):
    """Helper to wrap a sub-agent task with context protection"""
    registry = SubAgentRegistry(context_manager)
    wrapper = registry.get_wrapper(agent_name)
    
    # Start tracking
    wrapper.start_task(task, complexity)
    
    return wrapper


# Quick test/demo
if __name__ == "__main__":
    print("🧪 Testing Sub-Agent Protection...")
    
    # Create parent manager
    cm = ContextManager('pompey')
    
    # Create registry
    registry = SubAgentRegistry(cm)
    
    # Simulate architect work
    architect = registry.get_wrapper('architect')
    architect.start_task("Design OS-005 architecture", "complex")
    
    # Simulate token usage
    for i in range(5):
        result = architect.track("A" * 20_000)  # ~5K tokens each
        print(f"\n📊 Iteration {i+1}: {result}")
    
    # Check all agents
    print("\n🤖 All Agent Status:")
    for status in registry.get_all_status()[:5]:  # First 5
        if status['active'] or status['local_tokens'] > 0:
            print(f"  {status['agent']}: {status['performance']} ({status['local_tokens']} tokens)")
    
    # Complete task
    architect.complete_task("Architecture design complete")
    
    # Check handoffs
    handoffs = registry.check_handoffs_needed()
    if handoffs:
        print(f"\n🔄 Handoffs needed: {len(handoffs)}")