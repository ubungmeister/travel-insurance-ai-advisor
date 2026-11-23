---
name: project-context
description: Use when planning, implementing, refactoring, debugging or reviewing AI Advisor code, or updating its engineering guidance.
---

# Project context

Consult maintained project knowledge before choosing an architecture, pattern or dependency.

1. Read the repository's `AGENTS.md`, then [the knowledge index](../../../docs/knowledge/index.md).
2. Follow the index to the relevant guides and decisions; inspect affected code and current package files. Read only the topics needed for this task.
3. Distinguish observed dependencies, approved preferences, optional references and proposals. Approval does not mean final verification passed. Trainerlog examples are pinned references, not permission to copy its stack or auth approach.
4. Name the applicable local rule/decision and scope before planning a change. Keep the relevant Superpowers workflow for execution.
5. At wrap-up, follow the index's learning rules: merge reusable findings with sources and verification limits. New inferences remain proposed until approved; no reusable finding means no knowledge update.

Example: a chat-state task reads the frontend guides and D-002 before deciding which state belongs in a query versus tab storage. A blocked test is recorded as pending, never as passing.
