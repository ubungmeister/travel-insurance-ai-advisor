# Senior AI PR Reviewer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reusable, architecture-aware, read-only AI reviewer that developers can invoke with `/pr-review` before sending a PR.

**Architecture:** Add one project-local OpenCode subagent on a different model family and one slash command that launches it on current changes. The reviewer consults existing project instructions/knowledge, inspects relevant diffs and neighboring implementation, and separates actionable findings from optional design suggestions. `AGENTS.md` documents the manual pre-PR step; no CI integration or new application dependency is introduced.

**Tech Stack:** OpenCode V2 Markdown agent and command definitions, Markdown project instructions.

**Spec:** `docs/superpowers/specs/2026-11-22-senior-pr-reviewer-design.md`

## Global Constraints

- Use `github-copilot/claude-sonnet-5.5#high` for a model-family difference from the current GPT-6 Luna session; do not silently fall back if unavailable.
- Reviewer is advisory and must not edit files or update approved knowledge/decisions.
- Preserve the existing architecture-specialist/approval workflow for explicit architecture changes.
- Keep tests, lint, build, and browser verification separate from model review.
- No automated GitHub PR checks, new dependencies, or application changes.

## Review Focus

- No base ref or ambiguous branch: ask or state the comparison assumption rather than reviewing the wrong change set.
- Staged, unstaged, and relevant untracked files: include all intended PR changes and do not silently omit one category.
- Approved decisions versus observed code: cite the project knowledge and do not present a proposal as established policy.
- Architecture suggestions versus defects: label optional improvements separately and provide rationale/trade-offs without blocking solely on taste.
- Reviewer model unavailable or shell permission denied: report the limitation; do not silently use the primary model or claim a completed review.

---

### Task 1: Add the senior reviewer agent

**Files:**
- Create: `.opencode/agents/senior-reviewer.md`

**Interfaces:**
- Produces agent ID `senior-reviewer`, mode `subagent`, model `github-copilot/claude-sonnet-5.5#high`.
- Instructions require reading `AGENTS.md`, `docs/knowledge/index.md`, and only the relevant topic guides; reviewing the actual change and surrounding code; reporting findings with location/evidence/impact; keeping architecture recommendations separate; and never editing.
- Deny OpenCode edit tools. Require approval for shell operations so Git inspection can be allowed by the user without granting unattended mutation capability.

- [x] Create the Markdown agent with V2 frontmatter and the reviewer contract from the spec.
- [x] Verify the model ID/variant and deny-edit / ask-before-shell permissions against the current OpenCode agent documentation.
- [x] Review the prompt against the five Review Focus cases; explicitly prohibit silent model fallback and style-only findings.

### Task 2: Add `/pr-review` and the pre-PR instruction

**Files:**
- Create: `.opencode/commands/pr-review.md`
- Modify: `AGENTS.md`

**Interfaces:**
- Command frontmatter selects `senior-reviewer` and `subagent: true`; `$ARGUMENTS` is the optional base branch/commit.
- Command asks for a review of the current change set, including staged/unstaged/untracked intended files, with ambiguity handling and the report shape from the spec.
- `AGENTS.md` recommends `/pr-review [base]` before PR submission after normal checks, requires the developer to assess findings, and keeps review advisory.

- [x] Create `.opencode/commands/pr-review.md` with a clear description, selected agent, background subagent mode, and explicit base argument.
- [x] Update `AGENTS.md` with the manual pre-PR workflow and safeguards; do not duplicate the full checklist already there.
- [x] Verify the command and agent IDs match exactly and the command does not use a shell block that bypasses tool permissions.

### Task 3: Verify discovery, model selection, and review behavior

**Files:**
- Verify: `.opencode/agents/senior-reviewer.md`, `.opencode/commands/pr-review.md`, `AGENTS.md`

**Interfaces:**
- User invocation: `/pr-review` or `/pr-review <base-branch-or-commit>`.
- The run should launch `senior-reviewer` as a child session on Claude Sonnet 5.5, inspect Git state/diff with permission, and return findings plus optional architecture suggestions without edits.

- [ ] Confirm OpenCode discovers `/pr-review` and `senior-reviewer` after config reload. Source files are present, but runtime discovery could not be exercised from this session.
- [ ] Run a read-only smoke review on an explicitly chosen current change set; verify model identity, report structure, and that edit permissions are denied. Do not include unrelated working-tree changes without confirming the review scope.
- [ ] Record any shell/model availability limits and confirm tests/lint/build remain separate checks.

## Plan self-review

- Design coverage: manual reviewer, separate model, project architecture/knowledge awareness, findings versus suggestions, no edits/auto-policy changes, and preserved specialist workflow are covered by Tasks 1–3.
- Scope is configuration and project workflow only; no application code or dependencies.
- Runtime review smoke test is permission- and scope-sensitive, so the exact change set must be confirmed before invocation.

## Execution record

- User confirmed implementation in the current checkout to preserve the existing uncommitted design/plan work.
- Before implementation, `/pr-review` was tried and reported as not found. The root cause was that only the design and plan had been created; there was no command file yet.
- Added `.opencode/agents/senior-reviewer.md`, `.opencode/commands/pr-review.md`, and the pre-PR note in `AGENTS.md`.
- Model and V2 agent/command/permission fields were checked against the current OpenCode documentation and model catalog. Runtime discovery/model identity/read-only smoke review remains pending because shell startup is blocked in this environment; this doesn't prove the user's OpenCode instance has reloaded the new files.
- `git status --short` and `git diff --check` could not run: PowerShell failed to spawn with `Access is denied (os error 5)`. Source reads and hidden-file glob confirmed both OpenCode Markdown files exist and their agent/command IDs match.
- First `/pr-review` smoke invocation launched the reviewer but did not inspect source: all Git shell attempts failed before command execution at `WindowsApps\\pwsh.exe` with `Access is denied (os error 5)`. The reviewer correctly reported `unable to complete`, not a clean review. Model identity, diff scope, and edit-denial runtime behavior remain unverified.
