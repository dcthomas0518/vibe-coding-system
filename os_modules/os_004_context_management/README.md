# OS-004: Intelligent Context Management System

## Overview

OS-004 implements intelligent context management to maintain peak cognitive performance for Pompey and all 22 specialist sub-agents. Unlike simple token counting, this system understands work complexity and finds natural breakpoints for maintenance.

## Key Features

### 🧠 Intelligent Token Tracking
- **Optimal**: <40K tokens (peak performance)
- **Warning**: 40-80K tokens (monitor closely)
- **Critical**: >80K tokens (brain fog risk)
- **Emergency**: >100K tokens (must reboot)

### 🎯 Smart Reboot Decisions
- Protects complex work from interruption
- Identifies natural breakpoints (SPEC completion, tests passing, etc.)
- Considers work complexity (simple/normal/complex/critical)
- Provides Dale-friendly notifications

### 🤖 Sub-Agent Protection
All 22 specialists are protected:
- Technical: architect, dev-lead, backend-dev, frontend-dev, etc.
- Financial: capital-allocator, unit-economist, investment-analyst, value-auditor
- Creative: video-producer, copywriter, thumbnail-designer, etc.

### 💾 State Preservation
- Saves work context before reboot
- Integrates with OS-003 triumvirate communication
- Automatic resumption on next boot
- Zero lost progress

## Usage

### Basic Integration

```python
from context_manager import ContextManager

# Initialize on boot
context_mgr = ContextManager('pompey')

# Check for previous session
resume_state = context_mgr.check_resume_state()
if resume_state:
    context_mgr.restore_work_state(resume_state)

# During work
context_mgr.mark_work_status('implementing', 'complex')
context_mgr.update_token_count(text)

# Check if reboot needed
decision = context_mgr.evaluate_reboot_decision()
if decision['need_reboot'] and decision['can_interrupt']:
    context_mgr.graceful_reboot(decision['reason'])
```

### Sub-Agent Protection

```python
from subagent_wrapper import SubAgentRegistry

# Create registry
registry = SubAgentRegistry(context_mgr)

# Get wrapper for specific agent
architect = registry.get_wrapper('architect')
architect.start_task("Design architecture", "complex")

# Track usage
architect.track(response_text)

# Check if handoff needed
if architect._needs_handoff():
    architect.request_handoff()
```

## Boot Integration

Already integrated with `claude_session_init.py`:
1. Automatically checks for saved state
2. Restores context if available
3. Reports performance status
4. Ready for intelligent management

## Dale's Experience

When reboot is needed:
```
✅ Work completed - Perfect time for reboot!
Tokens: 52,000 (Optimal: <40K for peak performance)

DALE: ROUTINE MAINTENANCE NEEDED
1. Type: 'OS shutdown'
2. Type: 'OS boot up'
3. Work resumes automatically

This maintains peak performance - like a pit stop in F1! 🏎️
```

## Testing

Run the test suite to see all features:
```bash
cd ~/vibe-coding-system/os_modules/os_004_context_management
python3 test_context_management.py
```

## Architecture

```
ContextManager (Core)
├── TokenTracker
├── BreakpointDetector
├── WorkComplexityTracker
├── StatePreserver
└── RebootDecisionEngine

SubAgentRegistry
└── SubAgentContextWrapper (×22)
    ├── architect
    ├── dev-lead
    ├── frontend-dev
    └── ... (19 more)
```

## Success Metrics

- ✅ 95%+ time in optimal performance range
- ✅ Zero brain fog incidents
- ✅ No critical work interruptions
- ✅ 100% work resumption success
- ✅ All 22 specialists protected

## Future Enhancements

- Machine learning for better token estimation
- Predictive reboot scheduling
- Cross-triumvirate coordination
- Performance analytics dashboard

---

*"Peak performance through intelligent management. No brain fog. No degraded thinking. Just pure, sharp execution."*