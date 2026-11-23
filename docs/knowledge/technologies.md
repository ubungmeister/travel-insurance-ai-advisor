# Technology choices

**Purpose:** distinguish observed dependencies from approved defaults and optional references. This document is not an instruction to install tools or upgrade versions. Package and lock files remain authoritative; inventory below was reviewed on 2026-11-21.

## AI Advisor current stack

| Area | Current technology | Source / project preference |
| --- | --- | --- |
| Frontend | React 18, TypeScript, Vite 5 | `frontend/package.json`; retain the existing toolchain unless an upgrade is explicitly approved |
| Routing | React Router 7 | `frontend/package.json`, `frontend/src/app/router.tsx`; saved chat ID lives in the URL |
| Server state | TanStack React Query 5 | Declared dependency and approved server-state owner; final chat-refactor verification remains pending |
| Shared client state | Zustand 5 | Declared dependency used by auth; evaluate other shared-state needs selectively, not as a mandatory store or second server cache |
| Authentication | Supabase JS SDK; backend JWT validation | Existing code and approved account/ownership boundaries; do not replace with manual token storage copied from trainerlog |
| Frontend checks | ESLint, Prettier, TypeScript build, Node tests/React test renderer | `frontend/package.json`; tests are not live browser E2E |
| Backend | Python, FastAPI, Pydantic | `backend/requirements.txt`; do not copy trainerlog's Java backend |
| Persistence | SQLAlchemy, Alembic, PostgreSQL/psycopg | Existing backend; schema migrations and backend idempotency remain authoritative |
| Backend checks | pytest | Existing suite; SQLite unit/integration runs do not establish live PostgreSQL concurrency behavior |

Do not encode the current version inventory as a permanent preferred version. Check installed/locked versions, compatibility and current official documentation before an approved dependency change.

## Trainerlog reference stack

Pinned [package.json](https://github.com/ubungmeister/trainerlog/blob/5d20a656b82a4f252f0bed8e2cd241d84f68bcc4/frontend/package.json) at the architecture guide's snapshot. The shared concepts are React/TypeScript/Vite, Router, React Query and selective client stores—not its complete library list or exact versions.

| Reference technology | AI Advisor status | When to evaluate |
| --- | --- | --- |
| React Hook Form + Zod + resolvers | **Optional/reference**, not declared here | Complex forms with validation and field-state requirements; confirm need and adoption first |
| Tailwind, Radix/shadcn-style components | **Optional/reference** | A separately scoped UI/design-system decision |
| MUI and MUI date pickers | **Optional/reference** | Concrete UI needs and compatibility/licensing review; not a default parallel component system |
| React Toastify | **Optional/reference** | A consistent notification requirement, not a replacement for meaningful inline error/recovery states |
| date-fns, react-datepicker | **Optional/reference** | Actual date input/transformation needs; avoid multiple date-picker dependencies without a reason |
| Lucide, class utilities, avatars | **Optional/reference** | A feature needs them; no blanket baseline install |
| React 19 / Vite 6 versions in trainerlog | **Reference only** | An approved, tested upgrade plan—not automatic alignment |

## Before adopting or upgrading

1. Identify the concrete need and current project decision; check whether existing tools already solve it.
2. Compare fit, maintenance, compatibility, license, privacy and test impact.
3. State the recommendation and obtain approval for a new project default or stack change.
4. Update dependency files, relevant code/tests and [decisions](decisions.md) together; mark verification accurately.

Installed does not mean preferred for every task; used upstream does not mean adopted locally. Runtime and dev-only dependencies must be distinguished. Superpowers/OpenCode tooling is not an application dependency.
