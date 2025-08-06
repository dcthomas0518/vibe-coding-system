#!/usr/bin/env python3
"""
OS-004: Intelligent Context Management System
Maintains peak cognitive performance through intelligent reboots
"""

import json
import time
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from pathlib import Path
import re

class ContextManager:
    """Maintains peak performance through intelligent reboots"""
    
    # From CLAUDE.md thresholds
    OPTIMAL_LIMIT = 40_000   # Peak performance
    WARNING_LIMIT = 80_000   # Brain fog risk
    CRITICAL_LIMIT = 100_000 # Must reboot soon
    EMERGENCY_LIMIT = 150_000 # Forced reboot
    
    # Token estimation (rough approximation)
    CHARS_PER_TOKEN = 4  # Conservative estimate
    
    def __init__(self, member_name: str):
        """Initialize context manager for a triumvirate member"""
        self.member_name = member_name
        self.token_count = 0
        self.work_status = 'idle'
        self.work_complexity = 'simple'
        self.session_start = datetime.now()
        self.last_checkpoint = datetime.now()
        
        # State persistence
        self.state_file = Path(f"~/vibe-coding-system/state/{member_name}_context_state.json").expanduser()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Work tracking
        self.current_work = {
            'task': None,
            'started_at': None,
            'complexity': 'simple',
            'status': 'idle',
            'protected': False,
            'natural_breakpoints': []
        }
        
        # Initialize from saved state if exists
        self._load_state()
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count from text"""
        if not text:
            return 0
        
        # More accurate estimation based on content type
        # Code tends to have more tokens per character
        code_patterns = r'```|def |class |import |function |const |let |var '
        is_code_heavy = bool(re.search(code_patterns, text))
        
        if is_code_heavy:
            chars_per_token = 3.5
        else:
            chars_per_token = self.CHARS_PER_TOKEN
            
        return int(len(text) / chars_per_token)
    
    def update_token_count(self, text: str, work_context: Optional[Dict] = None):
        """Update running token count and check thresholds"""
        tokens = self.estimate_tokens(text)
        self.token_count += tokens
        
        if work_context:
            self.current_work.update(work_context)
        
        # Check thresholds
        self._check_performance_thresholds()
        
        return self.token_count
    
    def mark_work_status(self, status: str, complexity: str = None):
        """Mark current work status and complexity"""
        self.work_status = status
        if complexity:
            self.work_complexity = complexity
            self.current_work['complexity'] = complexity
        
        self.current_work['status'] = status
        
        # Update protected status based on complexity
        if complexity in ['complex', 'critical']:
            self.current_work['protected'] = True
        elif status in ['completed', 'idle']:
            self.current_work['protected'] = False
            
        # Track natural breakpoints
        if status in ['completed', 'tested', 'delivered']:
            self.current_work['natural_breakpoints'].append({
                'time': datetime.now().isoformat(),
                'status': status,
                'tokens': self.token_count
            })
    
    def is_natural_breakpoint(self) -> bool:
        """Check if we're at a natural breakpoint for reboot"""
        natural_statuses = ['completed', 'tested', 'delivered', 'idle']
        
        # Check explicit status
        if self.work_status in natural_statuses:
            return True
            
        # Check if we just finished something
        if self.current_work['natural_breakpoints']:
            last_breakpoint = self.current_work['natural_breakpoints'][-1]
            time_since = datetime.now() - datetime.fromisoformat(last_breakpoint['time'])
            if time_since.seconds < 60:  # Within last minute
                return True
                
        return False
    
    def evaluate_reboot_decision(self, current_work: Optional[Dict] = None) -> Dict[str, any]:
        """Evaluate whether reboot is needed based on multiple factors"""
        if current_work:
            self.current_work.update(current_work)
            
        decision = {
            'need_reboot': False,
            'urgency': 'none',
            'reason': None,
            'can_interrupt': True,
            'tokens': self.token_count,
            'performance_status': self._get_performance_status()
        }
        
        # Emergency threshold - must reboot
        if self.token_count > self.EMERGENCY_LIMIT:
            decision.update({
                'need_reboot': True,
                'urgency': 'emergency',
                'reason': 'Emergency token limit exceeded',
                'can_interrupt': True  # Override protection
            })
            return decision
            
        # Critical threshold
        if self.token_count > self.CRITICAL_LIMIT:
            decision.update({
                'need_reboot': True,
                'urgency': 'critical',
                'reason': 'Critical token threshold - brain fog imminent',
                'can_interrupt': not self.current_work['protected']
            })
            return decision
            
        # Warning threshold
        if self.token_count > self.WARNING_LIMIT:
            if self.is_natural_breakpoint():
                decision.update({
                    'need_reboot': True,
                    'urgency': 'high',
                    'reason': 'Warning threshold at natural breakpoint',
                    'can_interrupt': True
                })
            else:
                decision.update({
                    'need_reboot': True,
                    'urgency': 'moderate',
                    'reason': 'Warning threshold - wait for breakpoint',
                    'can_interrupt': False
                })
            return decision
            
        # Optimal threshold exceeded
        if self.token_count > self.OPTIMAL_LIMIT:
            if self.is_natural_breakpoint() and self.work_complexity != 'critical':
                decision.update({
                    'need_reboot': True,
                    'urgency': 'routine',
                    'reason': 'Routine maintenance for peak performance',
                    'can_interrupt': True
                })
                
        return decision
    
    def _get_performance_status(self) -> str:
        """Get human-readable performance status"""
        if self.token_count < self.OPTIMAL_LIMIT:
            return "✨ Peak Performance"
        elif self.token_count < self.WARNING_LIMIT:
            return "⚡ Good Performance"
        elif self.token_count < self.CRITICAL_LIMIT:
            return "⚠️ Degraded Performance"
        elif self.token_count < self.EMERGENCY_LIMIT:
            return "🔴 Critical - Brain Fog Risk"
        else:
            return "🚨 Emergency - Must Reboot"
    
    def _check_performance_thresholds(self):
        """Internal threshold checking with notifications"""
        status = self._get_performance_status()
        
        # Log significant transitions
        if self.token_count == self.OPTIMAL_LIMIT:
            print(f"📊 Context: Crossed optimal threshold ({self.OPTIMAL_LIMIT} tokens)")
        elif self.token_count == self.WARNING_LIMIT:
            print(f"⚠️ Context: Warning threshold reached ({self.WARNING_LIMIT} tokens)")
        elif self.token_count == self.CRITICAL_LIMIT:
            print(f"🔴 Context: CRITICAL threshold reached ({self.CRITICAL_LIMIT} tokens)")
    
    def graceful_reboot(self, reason: str) -> Dict[str, any]:
        """Initiate graceful reboot with state preservation"""
        print(f"\n🔄 INITIATING GRACEFUL REBOOT")
        print(f"Reason: {reason}")
        print(f"Current tokens: {self.token_count:,}")
        print(f"Performance: {self._get_performance_status()}")
        
        # Save current state
        state = self.save_session_state(reason, self.current_work)
        
        # Generate Dale-friendly message
        dale_message = self._generate_dale_message(reason)
        
        return {
            'success': True,
            'state_saved': state,
            'dale_message': dale_message,
            'next_steps': [
                "Type: 'OS shutdown'",
                "Type: 'OS boot up'",
                "Work resumes automatically"
            ]
        }
    
    def _generate_dale_message(self, reason: str) -> str:
        """Generate Dale-friendly reboot message"""
        if 'emergency' in reason.lower():
            icon = "🚨"
            header = "EMERGENCY MAINTENANCE REQUIRED"
        elif 'critical' in reason.lower():
            icon = "🔴"
            header = "CRITICAL MAINTENANCE NEEDED"
        else:
            icon = "✅"
            header = "ROUTINE MAINTENANCE - Perfect timing!"
            
        message = f"""
{icon} {header}
Tokens: {self.token_count:,} (Optimal: <40K for peak performance)

DALE: MAINTENANCE NEEDED
1. Type: 'OS shutdown'
2. Type: 'OS boot up'  
3. Work resumes automatically

This maintains peak performance - like a pit stop in F1! 🏎️
"""
        return message
    
    def save_session_state(self, reason: str, work_item: Dict) -> Dict[str, any]:
        """Save session state for resumption"""
        state = {
            'member': self.member_name,
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'token_count': self.token_count,
            'work_status': self.work_status,
            'work_complexity': self.work_complexity,
            'current_work': work_item,
            'session_duration': (datetime.now() - self.session_start).seconds,
            'performance_status': self._get_performance_status()
        }
        
        # Save to file
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
            
        # Also save to triumvirate communication system
        self._notify_triumvirate(state)
        
        return state
    
    def check_resume_state(self) -> Optional[Dict]:
        """Check for saved state from previous session"""
        if not self.state_file.exists():
            return None
            
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                
            # Check if state is recent (within 24 hours)
            saved_time = datetime.fromisoformat(state['timestamp'])
            if (datetime.now() - saved_time).days < 1:
                return state
                
        except Exception as e:
            print(f"⚠️ Could not load saved state: {e}")
            
        return None
    
    def restore_work_state(self, state: Dict):
        """Restore work state from saved session"""
        self.token_count = state.get('token_count', 0)
        self.work_status = state.get('work_status', 'idle')
        self.work_complexity = state.get('work_complexity', 'simple')
        self.current_work = state.get('current_work', self.current_work)
        
        print(f"✅ Restored context state:")
        print(f"  - Tokens: {self.token_count:,}")
        print(f"  - Work: {self.current_work.get('task', 'None')}")
        print(f"  - Status: {self.work_status}")
        print(f"  - Performance: {self._get_performance_status()}")
    
    def _load_state(self):
        """Load state on initialization"""
        state = self.check_resume_state()
        if state:
            print(f"🔄 Found saved context state from {state['timestamp']}")
            self.restore_work_state(state)
    
    def _notify_triumvirate(self, state: Dict):
        """Notify triumvirate of reboot via OS-003"""
        try:
            from triumvirate import Triumvirate
            tri = Triumvirate(self.member_name)
            
            tri.notify_members({
                'type': 'context_reboot',
                'member': self.member_name,
                'state': state,
                'priority': 'normal'
            })
        except:
            # Triumvirate not available yet, skip
            pass
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report"""
        decision = self.evaluate_reboot_decision()
        
        return {
            'member': self.member_name,
            'tokens': self.token_count,
            'performance': self._get_performance_status(),
            'work_status': self.work_status,
            'work_complexity': self.work_complexity,
            'protected': self.current_work['protected'],
            'natural_breakpoint': self.is_natural_breakpoint(),
            'reboot_decision': decision,
            'session_duration': (datetime.now() - self.session_start).seconds // 60  # minutes
        }


# Quick test/demo
if __name__ == "__main__":
    print("🧪 Testing Context Manager...")
    
    cm = ContextManager('pompey')
    
    # Simulate work
    cm.mark_work_status('implementing', 'complex')
    cm.update_token_count("A" * 150_000)  # ~37.5K tokens
    
    print("\n📊 Status Report:")
    report = cm.get_status_report()
    for key, value in report.items():
        print(f"  {key}: {value}")
    
    # Check reboot decision
    decision = cm.evaluate_reboot_decision()
    print(f"\n🤔 Reboot Decision: {decision}")
    
    # Complete work
    cm.mark_work_status('completed')
    decision = cm.evaluate_reboot_decision()
    print(f"\n✅ After completion: {decision}")