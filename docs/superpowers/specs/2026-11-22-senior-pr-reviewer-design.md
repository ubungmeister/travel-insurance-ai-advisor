# Senior AI PR Reviewer — Design

**Status:** Approved by user; agent and command files added. Runtime discovery and smoke review remain unverified.

## Intent

Add a repeatable, second-opinion review before a PR. The reviewer should act like a senior engineer: inspect the change for concrete defects, then assess whether the changed design and component boundaries fit this project's architecture and whether a better pattern is warranted. Its review is advisory; the developer remains responsible for decisions and verification.

## Current context

- `AGENTS.md` already defines security, contract, database, integration, and test review priorities.
- `docs/knowledge/index.md` points to approved architecture, patterns, and decisions; those sources distinguish approved project choices from observed code and unapproved proposals.
- `.opencode/` currently contains the project-context skill, but no persistent OpenCode reviewer agent or review command.
- `.codex/agents/architecture-reviewer.toml` is for architecture-proposal review. This workflow should complement, not replace, the architecture approval/specialist process in `AGENTS.md`.
- The current session uses GPT-6 Luna. The available model list includes `github-copilot/claude-sonnet-5.5`, providing a different model family for the second opinion.

## Goals

- Provide a manual `/pr-review` command for a developer to run when a change is ready for PR review.
- Launch a dedicated read-only OpenCode subagent using the different Claude model.
- Require the reviewer to consult `AGENTS.md`, the knowledge index, relevant guides/decisions, and affected code/tests before judging the change.
- Review both **change correctness** (bugs, regressions, auth/ownership, contracts, data integrity, tests) and **design quality** (responsibility boundaries, component/hook composition, reuse, fit with approved patterns, and viable simpler alternatives).
- Make the two kinds of output distinct: actionable findings are evidence-backed and severity-ranked; architectural or pattern improvements are clearly marked as suggestions, with trade-offs, not asserted as project policy.
- Require file/line references where possible, describe the concrete scenario and impact, and say what could not be verified.
- Keep the final decision, code changes, and any knowledge-base updates with the human developer.

## Non-goals and safeguards

- No automatic GitHub review/check, merge gate, approval, or code edits in this first version.
- No replacing tests, lint, build, browser verification, or the project's specialist workflow for explicit architecture changes.
- No automatic rewriting of approved decisions based on the reviewer model's preferences. Suggestions remain proposals until the user accepts them.
- No generic style-only findings or claims that a change is "best" without connecting the recommendation to project constraints, evidence, and trade-offs.
- The reviewer must not claim tests passed unless it actually ran them and observed the result.

## Approaches considered

1. **Project-local manual reviewer agent and command — selected.** A named read-only subagent and `/pr-review` command provide a second model and repeatable project guidance with low integration overhead. A human invokes it before PR and decides what to do with findings.
2. **Automated GitHub PR reviewer.** More consistent enforcement, but adds CI/provider integration, credentials or billing/quota considerations, external code handling, and false-positive noise. Defer until the local workflow demonstrates value.
3. **Checklist-only documentation.** Lowest setup, but does not provide the requested independent model perspective. Not selected.

## Proposed implementation shape

- Add `.opencode/agents/senior-reviewer.md`, configured as a `subagent` on `github-copilot/claude-sonnet-5.5#high`. Its instructions prohibit edits and separate findings from design suggestions. It reviews the actual working changes plus relevant surrounding files, rather than evaluating an abstract notion of ideal architecture.
- Add `.opencode/commands/pr-review.md` to invoke that agent on the current change set, optionally with a base branch/commit. If the correct comparison range is ambiguous, the reviewer must state the assumption or ask instead of silently reviewing the wrong diff.
- Update `AGENTS.md` with the suggested pre-PR invocation and a reminder that review is advisory and does not replace verification. Reuse existing knowledge docs rather than duplicating their architecture rules into a second knowledge source.
- Use a stable report shape: (1) blocking/actionable findings with severity, location, evidence, scenario, and impact; (2) non-blocking architecture/pattern suggestions with rationale and trade-offs; (3) scope, assumptions, and checks not run. If no findings are substantiated, say so without calling the code proven or approved.

## Remaining calls for implementation

- The command should support an optional base reference; the reviewer should include staged, unstaged, and untracked changes when they are part of the intended PR.
- The reviewer should be read-only through its OpenCode edit permissions. Shell access needed to inspect Git diffs should be limited or permission-gated; it must never use commands to modify the working tree.
- Model availability and usage limits depend on the user's active provider/account. If the configured model is unavailable, the command should fail visibly rather than silently fall back to the primary model.

## Approval gate

After the user approves this design, create an implementation plan, then add the agent/command and the minimal `AGENTS.md` guidance. Verify agent/command discovery, selected model, read-only behavior, and the review output contract; clearly record any checks that cannot run.
