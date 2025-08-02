# Vibe Coding Team Structure V2 - 10 Agent Model
*Generated: August 2, 2025*

## Architecture Overview

**Founder/PM (Dale)** → **CTO (Claude Code Main)** → **10 Specialist Subagents**

## CTO Role (Claude Code Main Thread)

### Consolidated Responsibilities from CD + CC Management:
- SPEC breakdown into SP-XXX requirements
- Sprint planning and velocity tracking
- Progress reporting in business terms
- Architectural decisions and reviews
- Quality gate enforcement
- AI Senate consultations
- Multi-project context management
- Model/thinking mode selection
- Team orchestration and delegation

### Key Principle
The CTO (main Claude Code) NEVER implements - always delegates to specialists.

## The 10 Specialist Subagents

### 1. **architect**
```yaml
---
name: architect
description: System architect for all design decisions
tools: Read, Grep, WebFetch
---
Responsibilities:
- System architecture diagrams
- API specifications
- Module boundaries
- Technology selection
- Never implements, only designs
```

### 2. **dev-lead**
```yaml
---
name: dev-lead
description: Development team lead ensuring code excellence
tools: Read, Write, Edit, MultiEdit, Bash, Task
---
Responsibilities:
- Implementation coordination
- Code quality (>90% coverage)
- Git discipline
- Bug fix management
- Effort estimation
```

### 3. **backend-dev**
```yaml
---
name: backend-dev
description: Server-side implementation specialist
tools: Read, Write, Edit, Bash, mcp__postgres
---
Focus: APIs, databases, business logic, integrations
```

### 4. **frontend-dev**
```yaml
---
name: frontend-dev
description: Frontend, UI/UX, artifacts, and visual implementation
tools: Read, Write, Edit, MultiEdit, mcp__playwright, WebFetch
---
Responsibilities:
- UI/UX design and implementation
- Artifact creation for PM UAT
- Responsive design
- Visual testing with Playwright
- Uses window.claude.complete()
```

### 5. **data-engineer**
```yaml
---
name: data-engineer
description: Data systems, analytics, and pipelines
tools: Read, Write, Bash, mcp__postgres, mcp__bigquery
---
Focus: Schema design, ETL, analytics, data lakes
```

### 6. **devops**
```yaml
---
name: devops
description: Infrastructure, deployment, monitoring
tools: Bash, Read, Write, mcp__kubernetes, mcp__terraform
---
Own: CI/CD, IaC, monitoring, scaling, deployment execution
```

### 7. **qa-engineer**
```yaml
---
name: qa-engineer
description: Quality assurance and testing specialist
tools: Read, Bash, mcp__playwright
---
Responsibilities:
- Test strategy and planning
- 90% coverage enforcement
- Performance testing
- UAT coordination
```

### 8. **security**
```yaml
---
name: security
description: Security, compliance, vulnerability management
tools: Read, Grep, Bash, WebFetch
---
Focus: Security reviews, OWASP compliance, pen testing
```

### 9. **perf-engineer**
```yaml
---
name: perf-engineer
description: Performance optimization specialist
tools: Read, Bash, Write, Grep
---
Focus: Latency, throughput, resource optimization
```

### 10. **tech-writer**
```yaml
---
name: tech-writer
description: Documentation and developer experience
tools: Read, Write, WebFetch
---
Own: API docs, README files, developer guides
```

## Communication Protocols

### Delegation Flow
```
PM Request → CTO Analysis → Task Breakdown → Parallel Delegation → Synthesis → PM Report
```

### Example Interaction
```
PM: "Build recipe search with dietary filters"

CTO: "I'll coordinate the team to deliver this..."
  → architect: Design search architecture
  → data-engineer: Design recipe schema
  → backend-dev: Implement search API
  → frontend-dev: Create search UI artifact
  → qa-engineer: Develop test strategy

CTO: "Recipe search ready for UAT:
- Elasticsearch architecture
- 45ms response time
- 94% test coverage
- Artifact ready for testing"
```

## Implementation Phases

### Phase 1: Core Team (Week 1)
1. Update CLAUDE.md with CTO role
2. Create architect subagent
3. Create dev-lead subagent
4. Create frontend-dev subagent
5. Test basic flow

### Phase 2: Quality & Security (Week 2)
1. Add qa-engineer
2. Add security
3. Add backend-dev
4. Refine delegation patterns

### Phase 3: Specialization (Week 3)
1. Add remaining specialists
2. Optimize parallel execution
3. Implement performance tracking

## Key Advantages

1. **Clean Interface** - PM only talks to CTO
2. **Deep Specialization** - Each agent masters their domain
3. **Parallel Execution** - Multiple agents work simultaneously
4. **Context Isolation** - No pollution between specialties
5. **Scalable Architecture** - Add/remove specialists as needed

## Success Metrics

- Sprint velocity improvement
- Reduced context switches
- Higher code quality (>95% coverage average)
- Faster feature delivery
- Clear accountability chain