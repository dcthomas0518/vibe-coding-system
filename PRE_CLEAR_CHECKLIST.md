# PRE-CLEAR CHECKLIST for CTO

**CRITICAL**: This checklist MUST be completed IN ORDER before ANY context clear. Skip NO steps.

## 🚨 IMMEDIATE CHECKS (Do These First!)

### 1. Check for Active Subagents
```bash
# Run this command to check if any subagents are still working
ps aux | grep -E "(architect|dev-lead|backend-dev|frontend-dev|data-engineer|devops|qa-engineer|security|perf-engineer|tech-writer)" || echo "No active subagents found"
```

**STOP if any subagents are active!** Wait for completion or document incomplete work.

### 2. Verify Current Working Directory
```bash
# Check where you are
pwd

# If in a project directory, note the project name
# Project name: ________________
```

## 📝 DOCUMENTATION UPDATES (Required)

### 3. Update CURRENT_CONTEXT.md
```bash
# Open and update the current context file
cat ~/CURRENT_CONTEXT.md

# Update with:
# - Active project(s) and their status
# - Last completed tasks
# - Next priorities
# - Any blockers or decisions pending
# - References to relevant project files
```

**Template for CURRENT_CONTEXT.md update:**
```markdown
# Current Context - [DATE]

## Active Projects
- **Project Name**: [project-directory-name]
  - Status: [In Progress/Blocked/Testing/etc]
  - Last Activity: [What was just completed]
  - Next Priority: [What should be done next]
  - See: [project-directory]/PROJECT_CONTEXT.md

## Pending Decisions
- [List any decisions waiting for Dale]

## Blockers
- [List any technical blockers]

## Session Handoff Notes
- [Any special context the next session needs]
```

### 4. Update Project-Specific Files (If in a project)
```bash
# Navigate to project directory if not already there
cd /home/dthomas_unix/[project-name]/

# Update SESSIONS_LOG.md
echo "## Session End - $(date '+%Y-%m-%d %H:%M')" >> SESSIONS_LOG.md
echo "### Completed:" >> SESSIONS_LOG.md
echo "- [List completed SP-XXX items]" >> SESSIONS_LOG.md
echo "### In Progress:" >> SESSIONS_LOG.md
echo "- [List incomplete SP-XXX items with status]" >> SESSIONS_LOG.md
echo "### Next Session Priorities:" >> SESSIONS_LOG.md
echo "- [List next priorities]" >> SESSIONS_LOG.md
echo "" >> SESSIONS_LOG.md

# Verify the update
tail -20 SESSIONS_LOG.md
```

### 5. Update TECHNICAL_CONTEXT.md (If architectural decisions were made)
```bash
# Only if new technical decisions were made
cat TECHNICAL_CONTEXT.md
# Add any new architectural decisions, API changes, or design patterns established
```

## 🔍 VERIFICATION STEPS

### 6. Git Status Check
```bash
# Check for uncommitted changes
git status

# If changes exist, either:
# a) Commit them with proper SP-XXX reference
# b) Document why they're not being committed in CURRENT_CONTEXT.md
```

### 7. Test Status Verification
```bash
# Run tests if any code was modified
# Document results in SESSIONS_LOG.md
npm test 2>/dev/null || python -m pytest 2>/dev/null || echo "No standard test suite found"
```

### 8. Sprint Progress Check
```bash
# Review sprint velocity and progress
grep -A 10 "Sprint Goal" SESSIONS_LOG.md | tail -20
```

## 📊 FINAL SUMMARY PREPARATION

### 9. Create Clear Summary for Dale
Prepare this message for Dale:

```
Ready to clear context. Summary:

**Completed Today:**
- [Feature/Task 1] ✓
- [Feature/Task 2] ✓

**In Progress:**
- [Task]: [XX]% complete, [status]

**Ready for Testing:**
- [Feature name] - [how to test]

**Next Priorities:**
1. [Priority 1]
2. [Priority 2]

**Blockers:** [None/List any]

All work has been saved and documented. Safe to clear.
```

### 10. Final Verification Commands
```bash
# Run ALL of these before confirming clear is safe:

# 1. Verify CURRENT_CONTEXT.md was updated
ls -la ~/CURRENT_CONTEXT.md && echo "✓ Current context file exists"

# 2. Verify project documentation is current (if in project)
ls -la SESSIONS_LOG.md PROJECT_CONTEXT.md TECHNICAL_CONTEXT.md 2>/dev/null || echo "Not in project directory"

# 3. Check no critical processes running
ps aux | grep -v grep | grep -E "(npm|node|python|pytest|cargo)" || echo "✓ No active processes"

# 4. Verify git status is clean or documented
git status --porcelain | wc -l

# 5. Final token count check
echo "Current context size: [Check Claude UI for token count]"
echo "Is it under 80K tokens? [YES/NO]"
```

## ✅ CLEARANCE CHECKLIST

Before confirming clear is safe, verify ALL items are checked:

- [ ] No active subagents running
- [ ] CURRENT_CONTEXT.md updated with handoff notes
- [ ] SESSIONS_LOG.md updated (if in project)
- [ ] Git status clean or documented
- [ ] Tests passing or issues documented
- [ ] Sprint progress tracked
- [ ] Clear summary prepared for Dale
- [ ] All verification commands run successfully
- [ ] Token count checked (<80K preferred)
- [ ] Dale has approved the clear

## 🚦 CLEAR DECISION

**Only proceed with clear if ALL checks pass!**

If ANY check fails:
1. Document the issue in CURRENT_CONTEXT.md
2. Inform Dale of the risk
3. Get explicit approval before proceeding

---

**Remember**: This checklist protects work continuity. Never skip steps to save time.

Last Updated: 2025-08-03
Version: 1.0