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

## V2 System Architecture Update - August 3, 2025

### Transition to 10-Agent Specialist Model
Moving from 8 generalist agents to 10 deep specialists for A++ performance.

### Updated Architecture
```yaml
~/.claude/agents/
├── architect.md           # System design (created)
├── dev-lead.md           # Development leadership (created)  
├── frontend-dev.md       # UI/UX + artifacts (created)
├── backend-dev.md        # Server-side (pending)
├── qa-engineer.md        # Quality assurance (pending)
├── security.md           # Security specialist (pending)
├── data-engineer.md      # Data systems (pending)
├── devops.md            # Infrastructure (pending)
├── perf-engineer.md      # Performance (pending)
└── tech-writer.md        # Documentation (pending)
```

### Key Architectural Decisions
1. **CTO as Main Thread**: Claude Code main = CTO, not separate subagent
2. **Stateless Subagents**: Each starts fresh, no memory persistence
3. **Tool Specialization**: Each agent has specific tool access
4. **Frontend Owns Artifacts**: All UI/UAT artifacts via frontend-dev

### Infrastructure Components
```
~/scripts/token-monitor.sh     # Usage tracking (implemented)
~/.claude/mcp.json            # Playwright config (implemented)
~/claude-metrics/             # Usage metrics directory
```

### Delegation Patterns
```
CTO analyzes request
  → Parallel delegation to specialists
    → architect designs first
    → dev-lead implements per design
    → frontend-dev creates artifacts
    → qa-engineer validates
  → CTO synthesizes results
```

---