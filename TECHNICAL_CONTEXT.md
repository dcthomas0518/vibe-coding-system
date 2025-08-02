# Technical Context

## Vibe Coding System Architecture - Consolidated Design

### System Overview
Single Claude Code instance orchestrating specialized sub-agents for all development roles.

### Architecture Principles
1. **Context Isolation**: Each sub-agent operates in fresh context
2. **Role Clarity**: Strict separation of concerns via specialized agents
3. **Aggressive Context Management**: Clear after every major task
4. **User-Obsessed Design**: PM behavior drives all technical decisions

### Sub-Agent Architecture
```yaml
~/.claude/agents/
├── system-architect.yml    # Architecture design
├── scrum-master.yml       # Sprint planning
├── cc-developer.yml       # Implementation
├── qa-reviewer.yml        # Quality assurance
├── security-auditor.yml   # Security scanning
├── test-automator.yml     # Test creation
├── performance-engineer.yml # Optimization
└── ux-analyst.yml         # UX analysis
```

### Communication Flow
1. PM → CD (main thread) → Specialized sub-agents
2. Sub-agents return structured results to CD
3. CD synthesizes and reports to PM in business language

### Feedback System Architecture
```
/feedback/
├── from_desktop/    # Desktop writes observations
│   ├── LIVE_UX_FEEDBACK.md
│   ├── SESSION_INSIGHTS.md
│   └── FRICTION_LOG.md
├── to_desktop/      # CC writes instructions
│   ├── ARTIFACT_UPDATES.md
│   ├── UX_EXPERIMENTS.md
│   └── OBSERVATION_REQUESTS.md
```

### Performance Optimizations
- Main thread maintains <40K tokens
- Sub-agents handle implementation details
- Parallel execution for independent tasks
- Model selection based on task complexity

### Security Model
- Desktop: Read/write to /feedback/ only
- Sub-agents: Isolated execution environments
- No cross-contamination between projects
- Git checkpoints enforce atomic changes

---