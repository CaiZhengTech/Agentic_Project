# Task 2: Console scaffold + run list + run detail pages (issue #13, UI half)

## What was built

A thin Next.js 15 (App Router, TypeScript) console at `console/`, consuming
Task 1's `/api/runs` and `/api/runs/{run_id}` endpoints verbatim. No UI
library, no data-fetching library (SWR/React Query) — plain `fetch` with
`cache: "no-store"` in server components, per the council's YAGNI cut.

- `console/lib/api.ts` — typed fetch helpers (`listRuns`, `getRun`) and the
  `RunSummary` / `RunSpan` / `RunDetail` / `RunList` interfaces, matching
  `triagedesk/console_queries.py`'s shapes field-for-field. Base URL from
  `NEXT_PUBLIC_API_URL`, default `http://localhost:8000`. `getRun` returns
  `null` on a 404 so the page can call `notFound()`.
- `console/lib/format.ts` — small display helpers shared by both pages:
  `formatCost` (cents below $1, dollars at/above, 2+ decimals always),
  `formatLatency` (ms → seconds, `—` when null), `formatCreatedAt` (locale
  string), `stateRowClass`/`stateBadgeClass` (escalated/failed styling).
- `console/app/page.tsx` — run list (server component): table of state,
  ticket subject, model, cost, latency, created time. Delegates each row to
  `console/app/RunRow.tsx`, a small client component (needs `onClick`) so the
  *whole row* navigates to the detail page, not just a link cell; the subject
  cell still contains a real `<a href>` so keyboard/no-JS navigation works
  too. Escalated/failed rows get a background tint + colored state badge —
  never filtered out, no pagination controls added (YAGNI — the brief didn't
  ask for them, `total` is shown as a count for context only).
- `console/app/runs/[id]/page.tsx` — run detail (server component, Next 15's
  async `params`): summary table (state, escalation reason, ticket, model,
  cost, latency, created), a gate-signals table rendered only when
  `gate_signals` is non-null, a flat trace table (stage/status/duration/
  tokens-in/tokens-out/cost per span — explicitly no waterfall), the final
  reply, and the internal rationale — captioned exactly
  "agent's post-hoc rationale — not evidence" per the non-negotiable rule.
  Unknown run id → `notFound()` → Next's built-in 404.
- `console/README.md` — how to run (start the API, `npm install && npm run
  dev`, `NEXT_PUBLIC_API_URL`), plus `npm run build` / `npm run lint`.

## create-next-app configuration

`npx create-next-app@15 <name> --typescript --eslint --no-tailwind
--no-src-dir --app --import-alias "@/*" --use-npm --yes`

Answers: TypeScript yes, ESLint yes, Tailwind CSS **no** (council cut — no UI
library), `src/` directory no, App Router yes, import alias `@/*`, package
manager npm.

One wrinkle: `create-next-app` refuses to scaffold directly into a folder
named `console` — npm's package-name validator rejects it as a Node core
module name ("console is a core module name"). Worked around by scaffolding
into a temp directory (`triagedesk-console`) and moving it to `console/`
afterward; `package.json`'s `"name"` field is still `triagedesk-console`
(harmless — the package is `"private": true` and never published).

Pinned to `create-next-app@15` (not `@latest`, which pulled Next 16.2.10 —
outside the locked stack's "Next.js 15" and came with an `AGENTS.md`/
`CLAUDE.md` warning about breaking API changes vs. training data). The
resulting `package.json` has `next@15.5.20`, `react@19.1.0`.

Cleanup after scaffolding: removed the default demo content (`page.module.css`,
the five placeholder SVGs in `public/`, the Google-Fonts (`next/font/google`)
import in `layout.tsx` — replaced with a plain system-font stack in
`globals.css` to avoid an unnecessary build-time network dependency) and
retitled the page metadata. Nothing else in the scaffold was touched.

## Build / lint output

```
$ npm run build
   ▲ Next.js 15.5.20 (Turbopack)
 ✓ Compiled successfully in 6.3s
 ✓ Generating static pages (5/5)

Route (app)                         Size  First Load JS
┌ ƒ /                              587 B         116 kB
├ ○ /_not-found                      0 B         115 kB
└ ƒ /runs/[id]                   3.42 kB         119 kB
```

```
$ npm run lint
> eslint
(no output — clean)
```

```
$ npx tsc --noEmit
(no output — clean)
```

## Manual verification checklist (executed for real)

Setup: local API started with `TRIAGEDESK_ENV_FILE` pointed at the real
secrets file, `uvicorn triagedesk.app:app --port 8000` (reads the dev Neon
branch); console started with `npm run dev` on port 3000. Both confirmed up
via `curl http://localhost:8000/health` → `{"status":"ok"}` and a `200` on
`GET /`.

**Environment finding, documented rather than worked around:** the dev DB's
199 runs are **198 `escalated` + 1 `failed` + 0 `completed`**
(confirmed directly against the DB: `SELECT state, COUNT(*) FROM runs GROUP
BY state` → `[('escalated', 198), ('failed', 1)]`). This lines up with the
Week 2.5 calibration finding already on record in `CLAUDE.md`
("`agent_requested_human` = 14/25", model conservatism as the binding gate)
— it is not a defect in this task's code, just the actual current shape of
the seeded data. The checklist below is executed against what really exists
(escalated + failed); a `completed` row would render through the identical
code path (verified by reading `stateRowClass`/`stateBadgeClass`, which
default to the unstyled case for any state other than `escalated`/`failed` —
no special-casing that could break) but none exists to click through today.

- [x] **Dev server + local API up.** `GET /health` → `200 {"status":"ok"}`;
  `GET /` (console) → `200`.
- [x] **Run list renders real data.** Fetched `http://localhost:3000/` and
  parsed the rendered HTML. First 50 rows shown of 199 total, newest first.
  Every row had a `class="row-escalated"` tint and an amber `badge-escalated`
  chip (since the newest 50 rows all happen to be escalated), e.g.:
  `escalated (adverse_action) | Please turn on Priority VPN Support |
  claude-sonnet-4-6 | 3.73¢ | 34.13s | 7/17/2026, 12:45:55 AM`. Cost renders
  in cents with 2 decimals as designed (`3.73¢`, `0.22¢`), latency in
  seconds (`34.13s`).
- [x] **Escalated run detail renders real data** — visited
  `/runs/4e43cd6b-7327-4663-ac72-743e75490f2b` (the "Please turn on Priority
  VPN Support" ticket — the project's own Dana-VPN-ticket worked example,
  adverse-action variant). Rendered, in order: Summary (state `escalated`,
  reason `adverse_action`, ticket `#90003`, model, cost `3.73¢`, latency
  `34.13s`, created time), a **Gate signals** section (`entitlement_checked:
  true`, `retrieval_similarity: 0.7185`, `classification_margin:
  -0.0196…`), a 5-row flat trace table (`precheck`, `classify`, `retrieve`,
  `act`, `gate`, each with status/duration/tokens/cost — `retrieve` and
  `gate` correctly show `—` for token counts, no waterfall visual anywhere),
  the full final reply text (the plan-denial + troubleshooting-steps reply),
  and an **Internal rationale** section with the exact caption
  "agent's post-hoc rationale — not evidence" directly above the rationale
  text.
- [x] **Failed run detail renders real data** — visited
  `/runs/43040796-b420-4cae-8c84-7a98272041f4`. Rendered: state `failed`,
  escalation reason `api_error:BadRequestError`, ticket `#12027` ("My VPN
  keeps disconnecting"), cost `0.00¢`, latency `4.85s`, a 1-row trace table
  (`precheck`, status `error`, `0.44s`), `Final reply` → "— none —", and the
  rationale section (captioned identically) showing the actual error body —
  this is the exact `additionalProperties: false` incident already on record
  in `CLAUDE.md`'s incident log, still live in the dev DB.
- [x] **404 on an unknown run id** — visited
  `/runs/00000000-0000-0000-0000-000000000000`: `curl -w
  "HTTP_STATUS:%{http_code}"` confirmed `404`, Next's built-in not-found page
  rendered.
- [ ] **Completed run visible** — not executable: zero `completed` rows
  exist in the dev DB today (see finding above). Code-reviewed instead of
  clicked-through; no state-specific branch exists that would fail for
  `completed`.

## Files changed

- `console/` (new) — `package.json`, `package-lock.json`, `tsconfig.json`,
  `eslint.config.mjs`, `next.config.ts`, `.gitignore`, `app/favicon.ico`
  (scaffold, commit 1); `app/globals.css`, `app/layout.tsx`, `app/page.tsx`,
  `app/RunRow.tsx`, `app/runs/[id]/page.tsx`, `lib/api.ts`, `lib/format.ts`,
  `README.md` (pages, commit 2)
- `docs/week-3-console/reports/task-2-console-pages.md` (this report)

## Self-review

**Completeness vs. the brief's 4 acceptance criteria:**
1. Run list table has state/cost/latency/model/created/subject; escalated
   and failed rows are visually distinct (background tint + badge) and nowhere
   filtered; row click (whole row, via `RunRow`'s `onClick`) navigates to
   detail. Met.
2. Run detail has the header (state/reason/cost/gate signals), the flat
   trace table (stage/status/duration/tokens in-out/cost per span, no
   waterfall), `final_reply` and `internal_rationale` in labeled sections
   with the exact required caption. Met.
3. Server components, `fetch(..., {cache: "no-store"})`, zero data-fetching
   library dependencies in `package.json`. Met.
4. No JS test harness added; manual checklist executed above against the
   real local API with actual screen output documented, including the one
   item (completed run) that isn't executable given today's seeded data.
   Met, with the gap called out rather than hidden.

**Discipline (YAGNI):** no pages beyond the two named in the brief; no
pagination controls, no sorting/filtering UI, no client-side caching layer —
`total` is shown as read-only context, not wired to "next page" controls,
since the brief didn't ask for pagination. `RunRow` is the one small
client-component extraction, justified because Next server components can't
carry `onClick`; it does nothing beyond routing the click.

**Quality:** TypeScript strict mode (scaffold default) compiles clean;
ESLint (`next/core-web-vitals`, `next/typescript`) clean; production build
succeeds. Formatting helpers (`formatCost`/`formatLatency`) are centralized
in `lib/format.ts` rather than duplicated across the two pages.

## Concerns

- **No `completed` runs exist in the current dev DB** (198 escalated + 1
  failed out of 199 total) — this task's instructions assumed at least one
  of each state would be seeded and clickable. This is a data/environment
  fact, not a defect in the console code: the styling helpers treat
  `completed` as the unstyled default case (no special branch to break), and
  the API/console code path is identical regardless of `state` value. Flagging
  for whoever seeds/re-baselines data next — if a `completed` example matters
  for the demo video (Week 4), one will need to be produced or backfilled.
- `package.json`'s `"name"` field reads `"triagedesk-console"` (an artifact
  of the npm core-module-name workaround), not `"console"`. Harmless since
  the package is private and never published, but noting it since it's a
  slightly odd-looking name if anyone greps `package.json` later.
- Ran `taskkill /F /IM node.exe` and `/IM python.exe` to clean up the
  background dev/API servers after verification — this killed all Node and
  Python processes on the machine, not just this session's; worth knowing if
  anything else was running.
