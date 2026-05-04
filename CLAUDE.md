# Claude Agentic Framework

Drop-in framework for optimized Claude Code workflows with specialized commands and reusable skills.

## Quick Reference

```bash
# Add your project's key commands here
# npm run build | pytest | cargo test | go test ./...
```

## Core Principles

These seven principles distill every rule, skill, and standard in this framework. Follow them and everything else follows.

### 1. Understand First
Read before writing; grep before creating; verify APIs via docs before assuming training data is current.

### 2. Prove It Works
Write tests first, run quality gates (tests, linter, types, build) before every commit, and add a regression test for every bug fix.

### 3. Keep It Safe
No secrets in code, validate all input, use parameterized queries, apply least privilege, and flag vulnerabilities immediately.

### 4. Keep It Simple
Single responsibility, no premature abstraction, delete dead code, avoid `any` types, fix warnings before committing.

### 5. Don't Repeat Yourself
Check `.claude/skills/` before generating ad-hoc solutions; maintain a single source of truth for business logic.

### 6. Ship It
Work on a branch, commit iteratively, and push to remote — work isn't done until `git push` succeeds.

### 7. Leave a Trail
Artifacts in `./artifacts/`, track work with Beads (`bd` CLI), document decisions in ADRs, name things clearly.

Full details in `.claude/rules/` (auto-loaded).

## Tech Stack

Defined in `.claude/rules/tech-strategy.md` — auto-loaded for every session.

## Workflow

**Branching**: Always branch from `main`. Never commit directly to `main`.

**Planning flow**: PR-FAQ → PRD → ADR → Design Spec → Plan → Implementation Beads

**Artifacts**: All planning docs stored in `./artifacts/`:

| Type | Pattern | Example |
|------|---------|---------|
| Vision | `pr_faq_[feature].md` | `pr_faq_user_auth.md` |
| Requirements | `prd_[feature].md` | `prd_user_auth.md` |
| Architecture | `adr_[topic].md` | `adr_database_choice.md` |
| System Design | `system_design_[component].md` | `system_design_api.md` |
| Design | `design_spec_[component].md` | `design_spec_login_form.md` |
| Roadmap | `roadmap_[project].md` | `roadmap_mvp.md` |
| Plan | `plan_[task].md` | `plan_api_refactor.md` |
| Security Audit | `security_audit_[date].md` | `security_audit_2025-01.md` |
| Post-Mortem | `postmortem_[incident-id].md` | `postmortem_inc-2025-001.md` |

**Beads** (issue tracking — CLI saves 98% tokens vs MCP):

```bash
bd create "Task"                        # Create
bd ready                                # Find unblocked work
bd show <id>                            # View details
bd update <id> --status in_progress     # Claim
bd close <id>                           # Complete
bd sync                                 # Sync with git
```

See `beads-workflow` skill for complete command reference.

## Working Directories

| Directory | Purpose | Lifecycle |
|-----------|---------|-----------|
| `./artifacts/` | Durable documents (plans, ADRs, PRDs, design specs) | Committed to repo |
| `./scratchpad/` | Ephemeral working notes, exploration output, draft content | Gitignored, disposable |

## Commands

| Command | Role | Use |
|---------|------|-----|
| `/architect` | Principal Architect | System design, ADRs |
| `/builder` | Software Engineer | Implementation, debugging, testing |
| `/qa-engineer` | QA Engineer | Test strategy, E2E, accessibility |
| `/security-auditor` | Security Auditor | Threat modeling, audits |
| `/ui-ux-designer` | UI/UX Designer | Interface design, a11y |
| `/code-check` | Codebase Auditor | SOLID, DRY, consistency audits |
| `/swarm-plan` | Planning Orchestrator | Parallel exploration, decomposition |
| `/swarm-execute` | Execution Orchestrator | Parallel workers, quality gates |
| `/swarm-review` | Adversarial Reviewer | Multi-perspective code review |
| `/swarm-research` | Research Orchestrator | Deep investigation, technology evaluation |

## MCP Tools

| Tool | Use For |
|------|---------|
| Sequential Thinking | Complex analysis, trade-off evaluation |
| Chrome DevTools | Browser testing, performance profiling |
| Context7 | Library documentation lookup |
| Filesystem | File system operations beyond workspace |

## Skills

Check `.claude/skills/` before ad-hoc generation. Skills are auto-suggested based on context via `.claude/skills/skill-rules.json`.
