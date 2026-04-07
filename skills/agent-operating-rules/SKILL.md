---
name: agent-operating-rules
description: Shared operating rules for repository inspection, Serena-first code understanding, and skill selection.
---

## 1. Serena-First Repository Understanding
- When Serena MCP is available, agents MUST use it for repository exploration, file reads, symbol lookup, and code understanding before relying on internal assumptions.
- Agents MAY skip Serena only when the task is purely conceptual or Serena is explicitly unavailable or failing.
- If Serena is available, it SHOULD be the default first step for repository-aware work.

## 2. Read Before Acting
- Before planning, implementing, testing, or reviewing, agents MUST inspect the smallest amount of repository context needed to act safely.
- Agents SHOULD start from explicitly provided files, symbols, or paths and expand only when needed.
- Agents MUST NOT guess repository structure, hidden behavior, or project conventions without repository evidence.

## 3. Source-of-Truth Inspection
- Before making design or placement decisions, agents MUST inspect 2-3 similar implementations when such examples exist.
- Agents SHOULD preserve the repository's established naming, layout, and local patterns unless those patterns clearly violate stronger architectural rules.
- If multiple valid patterns exist and the choice would materially affect the design, agents MUST ask one targeted question; otherwise they SHOULD choose the most consistent option and proceed.

## 4. Skill Loading Workflow
- Before continuing with a repository-aware task, agents MUST determine which reusable skills apply and load them.
- Agents working on code or architecture decisions MUST always load `architectural-guidelines`.
- Agents MUST additionally load stack-specific skills when the target repository clearly matches them.
- If a required skill cannot be loaded, agents SHOULD continue with best effort and explicitly note the limitation.

## 5. Stack Detection Rules
- Treat the project as Go when Go files, `go.mod`, or a Go service/package structure are present.
- Treat the project as Next.js when `next` is present in `package.json`, `next.config.*` exists, or the repository clearly uses `app/` or `pages/` routing conventions.
- If multiple stacks are clearly present, agents SHOULD load all relevant skills for the area they are touching.
- If the stack is unclear, agents MUST inspect the repository first and then decide.

## 6. Minimal Relevant Context
- Agents MUST prefer minimal, relevant context first over broad repository scans.
- Agents SHOULD expand exploration only when needed to preserve correctness, contract safety, architectural consistency, or verification confidence.

## 7. Ambiguity Handling
- Agents MUST NOT invent requirements or silently choose behavior that lacks repository or user support.
- When ambiguity materially affects correctness, contracts, or design, agents MUST stop and ask concise, decision-enabling questions.
