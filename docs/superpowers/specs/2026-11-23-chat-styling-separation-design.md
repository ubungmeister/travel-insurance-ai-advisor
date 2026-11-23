# Chat styling separation

## Intent and scope

Keep the MUI chat components easy to read by moving their inline `sx` styling into named, nearby TypeScript style files. Apply this to the existing chat page and chat components, without changing their appearance, responsive layout, accessibility, behavior, state ownership, or APIs. Update the frontend knowledge patterns with the approved preference.

## Approaches

- **Selected:** co-located `*.styles.ts` modules containing named, MUI-compatible styles. This retains MUI theme tokens and responsive syntax without adding a styling library.
- **Alternative:** CSS modules and named classes, closer to Trainerlog's named CSS classes, but requiring translation of MUI theme and breakpoint values.

Trainerlog also uses inline Tailwind utilities; the selected approach adopts its named-class separation idea rather than claiming its whole UI uses separate styles. Reference: [Trainerlog `index.css` at `5d20a656`](https://github.com/ubungmeister/trainerlog/blob/5d20a656b82a4f252f0bed8e2cd241d84f68bcc4/frontend/src/index.css).

## Constraints

- Keep application changes under `frontend/`; no new dependencies or backend changes.
- Keep the shared MUI theme and the React Query, session provider, draft, recovery, and send safeguards intact.
- Preserve existing style values including breakpoints, theme tokens, message-role variants and overflow behavior.
- Preserve unrelated working-tree changes; do not make a new worktree or commit user changes.
- Verify with the existing frontend tests, lint, and build; report browser and environment limitations accurately.
