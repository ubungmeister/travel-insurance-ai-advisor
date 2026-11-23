# Chat Styling Separation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep chat JSX readable by moving its inline MUI `sx` styles to named, nearby files without changing the UI or behavior.

**Architecture:** Each affected component imports a co-located `*.styles.ts` module. Styles use MUI `SxProps<Theme>` or equivalent typed objects, retaining all original values and responsive and role-specific differences. Record the approved preference and reference in the frontend knowledge guide.

**Tech Stack:** React, TypeScript, MUI, Vite, Node test runner.

**Spec:** `docs/superpowers/specs/2026-11-23-chat-styling-separation-design.md`

## Global Constraints

- Application code changes stay under `frontend/`; no new dependencies, backend changes, or new worktree.
- Preserve every current MUI style value, breakpoint, theme token, layout and accessibility attribute.
- Preserve session provider, React Query, draft storage, send/retry behavior and API contracts.
- Preserve unrelated existing changes including the modified package files and `.codex` deletions.
- Do not commit unrelated files; do not claim browser or live-service verification without performing it.

## Review Focus

- Narrow and desktop layouts retain the grid, sidebar and scrolling rules: assert exact responsive style objects.
- User and assistant messages retain their distinct alignment and colors: assert both role variants.
- Long content and recovery or policy lists retain wrapping and scrolling limits: assert the extracted style values.
- Empty, selected and disabled history/policy states retain behavior: run the existing rendered-state tests.
- Composer, recovery, navigation and identity boundaries retain behavior: run the complete existing test suite.

## Task 1: Extract chat styles and document the preference

**Files:**
- Create: `frontend/src/pages/chat/ChatPage.styles.ts`.
- Create: `frontend/src/components/chat/ChatSession.styles.ts`, `ChatTranscript.styles.ts`, `ConversationHistory.styles.ts`, `ChatPolicyPanel.styles.ts`, `PolicyDetails.styles.ts` in the same directory.
- Modify: the matching six `.tsx` files, replacing inline `sx` objects with named imports while leaving semantic and behavioral props unchanged.
- Modify: `frontend/tests/chat-recovery.test.mjs` for focused checks and `docs/knowledge/frontend-patterns.md` for the preference and provenance.

**Interfaces:** Export typed named style objects from each style module; use explicit `userMessage` and `assistantMessage` variants for role-specific styles, selected by the component's existing `isUser` value. No public API or state interfaces change.

- [x] **Step 1: Prepare existing dependencies without altering user package edits.** MUI was present; no installation or package edits were necessary.
- [x] **Step 2: Add focused style tests.** The new style test failed before extraction because `ChatSession.styles.ts` did not exist, then passed after extraction. It checks responsive columns, scrolling, overflow and the message-role variants.
- [x] **Step 3: Extract styles.** Moved inline `sx` objects from the six components into typed co-located style modules without changing the existing behavior props.
- [x] **Step 4: Update knowledge.** Added the approved styling preference and pinned Trainerlog source to `docs/knowledge/frontend-patterns.md`, with verification limits.
- [x] **Step 5: Verify.** The focused test passed; `npm test` passed 40/40 with React renderer warnings; `npm run lint` passed. `npm run build` failed when Vite could not access an existing `dist` asset (ENOTEMPTY, then EPERM); `npm run build -- --outDir C:/Users/Artem/AppData/Local/Temp/opencode/chat-styling-build-20261123` passed with a chunk-size advisory. Browser and live-service flows were not verified.
- [x] **Step 6: Review changes.** Self-reviewed the diff, extracted style values and git status; the unrelated package edits and `.codex` deletions remain. No commit was made.
