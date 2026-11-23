---
description: Run the independent senior architecture-aware review before a PR
agent: senior-reviewer
subagent: true
---

Review the intended PR changes as an independent senior code and architecture reviewer.

Optional comparison base (branch or commit): `$ARGUMENTS`. If empty, use a base only when repository state makes it unambiguous; otherwise ask or report the exact assumption before judging the diff.

Inspect the intended staged, unstaged, and untracked changes, then read relevant files, tests, callers, and neighboring implementations. Follow the review standards and report format in your agent instructions, `AGENTS.md`, and the relevant project knowledge guides. Separate evidence-backed actionable defects from optional architecture/component suggestions. Do not edit files. State tests or checks that were not run; this review does not replace them.
