# Project Knowledge Implementation Plan

**Goal:** Provide an AI Advisor-only engineering playbook that agents consult before development and maintain from approved preferences and verified lessons.
**Approved scope:** Six guides under `docs/knowledge/`, one OpenCode entry skill, and a small `AGENTS.md` startup gate. Seed trainerlog patterns as a pinned reference, not an instruction to adopt all its dependencies. No application/dependency/global configuration changes or automatic commits.

## Authoring checklist

### Baseline
- [x] Define retrieval scenarios: startup sources, technology status, reference provenance, and unverified-versus-approved design.
- [x] Run a fresh read-only agent without the entry skill.
- [x] Identify missing reference structure: baseline reported no local knowledge index, entry skill, pinned trainerlog guide or structured learning records. Existing package files establish dependencies but not optional/adopted guidance. The prior refactor plan DOES record approved design; do not accept the baseline's broader claim that no approved record exists.

### Create
- [x] Skill ID uses lowercase letters/hyphens; name and trigger-only description fit discovery requirements.
- [x] Keep the frequently loaded entry skill short; put technical detail in linked project guides.
- [x] Add a small example/output contract and topic-routing index.
- [x] Separate current dependencies, approved preferences, optional references and proposals.
- [x] Include scope/reason/source/verification status for decisions and lessons.
- [x] Avoid credentials, raw session dumps, or copying trainerlog auth/token storage.
- [x] Preserve the prior refactor's pending-verification status.
- [x] Run the same retrieval/application cases WITH the skill in a fresh agent.
- [x] Check the agent cites real sources and does not promote optional dependencies or unverified examples.

### Quality and verification
- [x] Check frontmatter, discovery path, all local links and pinned source links.
- [x] Check examples and guidance against current package files and existing approved decisions.
- [x] Test an update scenario: explicit user preference is approved; agent inference stays proposed; blocked checks are not passing evidence.
- [x] Close any gaps revealed by these checks before marking complete.
- [x] Report the exact guidance files changed and any unavailable runtime discovery/verification.

**Not applicable:** This is a reference/retrieval entry skill, not a new pressure-enforced engineering discipline; five-repetition wording experiments and rationalization tables are not needed. Existing Superpowers workflows remain responsible for TDD/debugging/review. No new diagrams or application architecture decisions are introduced. Publishing a skill or committing it is not authorized by this task.

**Reference snapshot:** trainerlog main resolves to `5d20a656b82a4f252f0bed8e2cd241d84f68bcc4`, checked on 2026-11-21.

## Verification results
- OpenCode discovered `project-context` after file creation; the native skill tool loaded the exact entry file successfully. No restart or global configuration change was needed.
- Fresh WITH-skill retrieval test correctly selected guides/decision IDs, optional dependency statuses, pinned source examples and pending refactor verification.
- Fresh maintenance test correctly merged an explicit preference into D-001, kept an agent-derived stack replacement proposed, and recorded blocked lint as pending. It found ambiguous Zustand wording; clarified it as selective availability, and a follow-up read confirmed consistency.
- All six pinned trainerlog source paths returned HTTP 200. Dedicated read/grep checks confirmed the six local guide files and their relative Markdown link targets. Skill metadata/base-path resolution were checked through native loading and file read.
- The automated Node link/metadata check could not run because the harness still cannot spawn PowerShell (`Access is denied`). That limitation remains; native discovery and agent/read-based checks are the verification used here, not a claimed automated lint/build result.
- L-003 is explicitly proposed, not silently approved: it records an observed test failure with final correction verification pending.
- Guidance-only changes: six knowledge guides, one skill, the AGENTS.md gate and this plan. Application/dependency files and the unfinished refactor were not modified by this task.
