# Week 3 — Console + Deploy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:test-driven-development per
> code task. Each `### Task N:` section is self-contained (sliced by `task-brief`).
> Tasks 1–5 and 7 are code; Task 6 is controller+Cai (live deploy). API tests are $0
> (fixtures/fakes; FastAPI TestClient with dependency overrides). Console (Next.js)
> tasks carry NO JS test harness (deliberate council thinness) — they end with a manual
> verification checklist against the local API instead.

**Goal:** the glass-box ops console (run list → run detail → review queue), deployed
(Railway + Neon + Vercel) behind demo-abuse protection — issues #13–#16.

**Architecture:** the console is a THIN read layer. All data flows through the existing
FastAPI app (`triagedesk/app.py`) — the console never touches the DB. New API surface:
runs read endpoints, a review-queue write endpoint (admin token), and a guarded demo-run
endpoint. One new table (`review_decisions`, via Alembic). Next.js (App Router) lives in
`console/` at the repo root, plain `fetch`, no UI libraries.

**Tech Stack:** FastAPI (existing), SQLAlchemy 2.0, Alembic, Next.js 15 + TypeScript
(new, `console/`), Vercel + Railway (Nixpacks — NO Docker).

## Global Constraints (binding)

- All standing rules apply: adverse-action rule; gate invariants; fail-closed on cost;
  SDK-reality rule; schema changes ONLY via Alembic; read
  `docs/00-spec/DATA-SCHEMA.md` before ANY query (gotcha list is load-bearing here —
  naive `created_at` vs aware `finished_at`; predicted queue lives on the classify span).
- **$0 for implementers**: no Anthropic/Voyage calls, no live runs, no deploys. The
  demo-run endpoint is tested with a monkeypatched `run_ticket` fake.
- **Council cuts stay cut:** flat trace table (NO waterfall visuals); single shared
  admin token (NO auth system); NO Docker; NO free-text ticket entry anywhere in the
  console. Failed runs stay visible with their error reason — never filtered out.
- **⚠️ Gate-cost rule:** merges touching `triagedesk/**` auto-trigger the ~$0.90 eval
  gate. Controller batches those merges back-to-back and CANCELS superseded queued
  `eval-gate` runs (`gh run cancel`) so at most ONE gate run bills per merge batch.
  Console-only merges (`console/**`, docs) never trigger it.
- **Descope ladder if the week overruns (cut in order):** post-deploy smoke test →
  JSON logs → per-IP rate limit. The daily spend cap is NEVER cut.
- New settings go in `triagedesk/config.py::Settings` with safe defaults; document each
  in `.env.example` in the same task that adds it.

## File Structure (locked by this plan)

- `triagedesk/app.py` — stays the single FastAPI entrypoint; routes defined here
  (it is small; splitting into routers is NOT needed this week — YAGNI).
- `triagedesk/console_queries.py` — NEW: the SQLAlchemy read queries the API serves
  (list runs, run detail, review queue). Keeps `app.py` route-thin.
- `triagedesk/models.py` — gains `ReviewDecision`.
- `alembic/versions/<rev>_review_decisions.py` — the one migration.
- `triagedesk/demo.py` — NEW (Task 7): pool listing, rate limiter, daily-cap check.
- `scripts/smoke.py` — NEW (Task 5): post-deploy smoke script.
- `console/` — NEW Next.js app: `app/page.tsx` (run list), `app/runs/[id]/page.tsx`
  (run detail), `app/review/page.tsx` (queue), `lib/api.ts` (fetch helpers, reads
  `NEXT_PUBLIC_API_URL`).
- Tests: `tests/unit/test_console_api.py` (TestClient + overridden `get_db` with fakes),
  `tests/unit/test_demo_guards.py`, `tests/integration/test_review_decisions_migration.py`.

---

### Task 1: Runs read API — list + detail (issue #13, API half)

**Files:**
- Create: `triagedesk/console_queries.py`, `tests/unit/test_console_api.py`
- Modify: `triagedesk/app.py`

**Interfaces (produces — the console consumes these verbatim):**
- `GET /api/runs?limit=50&offset=0` →
  `{"runs": [{"id": str, "ticket_id": int, "ticket_subject": str, "state": str,
  "escalation_reason": str|null, "total_cost_usd": float, "latency_ms": float|null,
  "model": str, "created_at": str}], "total": int}` — newest first. `latency_ms` =
  `finished_at − created_at`; **normalize naive/aware before subtracting** (the
  documented tz gotcha — do it in `console_queries.py`, one helper, unit-tested);
  null while `state='running'` or if `finished_at` is null.
- `GET /api/runs/{run_id}` → run fields above + `"final_reply": str|null,
  "internal_rationale": str|null, "gate_signals": dict|null, "spans": [{"name": str,
  "status": str, "duration_ms": float|null, "input_tokens": int|null,
  "output_tokens": int|null, "cost_usd": float, "attributes": dict}]` — spans ordered
  by `started_at`; tokens read from `attributes` keys `gen_ai.usage.input_tokens` /
  `gen_ai.usage.output_tokens` (may be absent → null). 404 on unknown id; 422 on
  non-UUID id (FastAPI's UUID path param gives this for free — use `run_id: uuid.UUID`).

**Acceptance criteria (binding):**
1. Failed runs appear in the list with `escalation_reason`/error visible — no filter.
2. All reads go through `console_queries.py` functions taking a `Session` — no ORM
   queries inline in routes.
3. Tests use `app.dependency_overrides[get_db]` with an in-memory fake/stub session or
   SQLite-compatible subset — NO live DB. (Spans `attributes` is JSON — SQLAlchemy JSON
   works on SQLite; pgvector tables are NOT touched by these queries.)

**TDD steps:** failing tests first for: (a) list returns newest-first with computed
`latency_ms` and a failed run present with its reason; (b) tz normalization: naive
`created_at` + aware `finished_at` subtract without raising and give the right ms;
(c) detail 404 on missing; (d) detail spans ordered with token/cost fields extracted;
(e) list pagination (`total` independent of `limit`).

---

### Task 2: Console scaffold + run list + run detail pages (issue #13, UI half)

**Files:**
- Create: `console/` (Next.js 15 App Router, TypeScript, `create-next-app` defaults,
  no Tailwind prompt-answers documented in the report), `console/lib/api.ts`,
  `console/app/page.tsx`, `console/app/runs/[id]/page.tsx`, `console/README.md`
  (how to run: `npm run dev` + `NEXT_PUBLIC_API_URL`).

**Interfaces (consumes):** Task 1's two endpoints, verbatim shapes.

**Acceptance criteria (binding):**
1. Run list: table with state, cost (as ¢/$ with 2+ decimals), latency (s), model,
   created time, ticket subject; **failed/escalated rows visually distinct but NEVER
   hidden**; row click → detail page.
2. Run detail: run header (state, reason, cost, gate signals if present), the
   **flat trace table** (stage, status, duration, tokens in/out, cost per span — NO
   waterfall), `final_reply` and `internal_rationale` shown in labeled sections —
   rationale explicitly captioned "agent's post-hoc rationale — not evidence".
3. Server components with `fetch(no-store)` or client fetch — implementer's choice,
   but NO data library (no SWR/React Query — YAGNI).
4. No JS test harness. Task ends with a manual checklist in the report: dev server up,
   both pages render against local API with at least one completed, one escalated, one
   failed run visible (use seeded local data; document what was on screen).

---

### Task 3: `review_decisions` + review-queue API + admin token (issue #14, API half)

**Files:**
- Modify: `triagedesk/models.py`, `triagedesk/config.py` (+`admin_token: str = ""`),
  `triagedesk/app.py`, `triagedesk/console_queries.py`, `.env.example`
- Create: `alembic/versions/<rev>_review_decisions.py`,
  `tests/integration/test_review_decisions_migration.py`; extend
  `tests/unit/test_console_api.py`

**Interfaces (produces):**
- Model `ReviewDecision`: `id` int PK · `run_id` UUID FK→runs **unique** ·
  `decision` str(8) (`approve`|`reject`) · `note` text · `created_at` timestamp
  server-default. Migration upgrade creates table + downgrade drops it.
- `GET /api/review-queue` → `{"items": [{run fields as Task 1 list} +
  {"internal_rationale": str|null, "final_reply": str|null}], "total": int}` —
  runs with `state='escalated'` having NO ReviewDecision row, oldest first.
- `POST /api/review/{run_id}` body `{"decision": "approve"|"reject", "note": str}` +
  header `X-Admin-Token` → 201 `{"id": …}`; **401 when token missing/wrong; 503 when
  `settings.admin_token` is unset (fail closed — an empty configured token must never
  mean open)**; 409 if the run already has a decision; 404 unknown run; 422 bad
  decision value (Pydantic Literal).

**Acceptance criteria (binding):** the three auth behaviors above are each a test; the
queue excludes decided runs; adverse-action escalations (`escalation_reason` in
`adverse_action`, `no_entitlement_evidence`) appear in the queue like any escalation.

**TDD steps:** failing tests first for: (a) queue lists escalated-undecided only;
(b) POST persists and second POST → 409; (c) 401 wrong token; (d) 503 unset token;
(e) migration round-trip (integration-marked, skipped without TEST_DATABASE_URL —
follow `tests/integration/test_eval_results_golden_view.py` conventions).

---

### Task 4: Console review queue page (issue #14, UI half)

**Files:**
- Create: `console/app/review/page.tsx`; extend `console/lib/api.ts`

**Interfaces (consumes):** Task 3's endpoints. Admin token: a simple client-side text
field stored in `sessionStorage`, sent as `X-Admin-Token` (documented in the page UI as
"operator token"; council decision: no auth system).

**Acceptance criteria (binding):**
1. Each queue item shows: ticket subject, escalation reason, the draft `final_reply`,
   and `internal_rationale` — rationale captioned as post-hoc context, per Task 2's rule.
2. Approve/Reject buttons + required note field → POST; success removes the item;
   401 shows "invalid operator token" without clearing the queue; 409 shows "already
   reviewed" and refreshes the list.
3. Manual checklist in the report (local API + seeded escalated run: approve one,
   reject one, wrong-token path, all three observed and described).

---

### Task 5: Deploy-prep code — CORS + JSON logs (issue #15, code half)

**Files:**
- Modify: `triagedesk/app.py` (CORSMiddleware), `triagedesk/config.py`
  (+`cors_origins: str = ""` comma-separated, +`log_json: bool = False`),
  `.env.example`
- Create: `triagedesk/logging_setup.py` (JSON formatter: one-line
  `{"ts", "level", "logger", "msg"}` via stdlib `logging` — no new deps; applied in
  `app.py` startup when `settings.log_json`); extend
  `tests/unit/test_console_api.py` (CORS header test via TestClient preflight),
  create `tests/unit/test_logging_setup.py`

**Acceptance criteria (binding):** CORS allows ONLY configured origins (test: allowed
origin echoed, disallowed absent); empty `cors_origins` = no cross-origin access
(fail closed); JSON log lines parse as JSON (test captures a record through the
formatter).

---

### Task 6 (CONTROLLER + CAI — live): Deploy Railway + Neon + Vercel + smoke

Not for implementers. Sequence: (1) Cai creates/link Railway + Vercel projects (needs
his accounts; controller prepares exact env-var lists from `.env.example`); Railway:
Nixpacks from repo, start `uvicorn triagedesk.app:app --host 0.0.0.0 --port $PORT`,
release phase `alembic upgrade head`, env vars incl. `DATABASE_URL` (Neon prod branch —
decide dev vs new branch with Cai), `ADMIN_TOKEN`, `CORS_ORIGINS=<vercel url>`,
`LOG_JSON=1`; (2) Vercel: `console/` root, `NEXT_PUBLIC_API_URL=<railway url>`;
(3) `/health` live; (4) run `scripts/smoke.py` against prod (ONE live run ≈ 3¢);
(5) record everything in `docs/week-3-console/reports/task-6-deploy.md` + HANDOFF.
Descope ladder applies to the smoke step only per the council order.

---

### Task 7: Demo abuse protection (issue #16)

**Files:**
- Create: `triagedesk/demo.py`, `tests/unit/test_demo_guards.py`, `scripts/smoke.py`
- Modify: `triagedesk/app.py`, `triagedesk/config.py`
  (+`demo_daily_cap_usd: float = 1.00`, +`demo_rate_limit_per_hour: int = 5`),
  `.env.example`; extend `console/app/page.tsx` (or a `console/app/demo/page.tsx` —
  implementer's choice, report it) with the pool-picker UI + visible-pause banner.
- `scripts/smoke.py --base-url <url> --ticket-id <id>` (the Task-6 deploy check):
  POSTs `/api/demo/run`, polls `GET /api/runs/{id}` until terminal state, exits 0 iff
  state in `{completed, escalated}` AND `total_cost_usd > 0`, else 1 with the reason on
  stderr; prints run id + state + cost. Unit-tested with a monkeypatched HTTP layer
  (use whichever HTTP client `requirements.txt` already carries — add nothing new).

**Interfaces (produces):**
- `GET /api/demo/pool` → `{"tickets": [{"id": int, "subject": str}]}` — ONLY tickets
  with `source='demo'` (the seeded pool; NO free text anywhere).
- `POST /api/demo/run` body `{"ticket_id": int}` →
  - 404 if ticket not in the pool (pool-only rule — checked against `source='demo'`);
  - 429 `{"paused": false, "reason": "rate_limited"}` when the caller IP exceeded
    `demo_rate_limit_per_hour` (in-memory fixed-window dict keyed by
    `request.client.host`; single-instance limitation documented in a comment);
  - 402 `{"paused": true, "reason": "daily_budget_reached"}` when
    `SUM(runs.total_cost_usd) for runs created today (UTC)` + the $0.10 per-run cap
    would exceed `demo_daily_cap_usd` — **pre-check, fail closed, same shape as the
    suite cap; computed by a `console_queries.py`/`demo.py` DB query, no counter
    table**;
  - else dispatches the pipeline (`run_ticket`) and returns 202 `{"run_id": str}`.
- Console: pool dropdown + "Run" button → on 402 renders the banner **"Daily demo
  budget reached — watch the video instead"** (link placeholder for #17). NO cached
  replay of any kind (council: deception in miniature).

**Acceptance criteria (binding):** the four response branches above are each a unit
test with `run_ticket` monkeypatched (asserting it is NOT called on 404/429/402 —
"before spending" semantics); the daily-cap query is tz-explicit (UTC date window on
naive `created_at` — document the choice in a comment); rate-limit window resets are
tested by injecting a fake clock (pass `now` in, don't read `time.time()` inline).

---

## Merge/batching order (controller)

Task 1 → 3 → 5 → 7 all touch `triagedesk/**`: review each, then merge the accumulated
PRs back-to-back in ONE batch and cancel superseded queued gate runs (keep the last —
one ~$0.90 gate run for the whole API wave). Tasks 2 and 4 (`console/**` only) merge
freely at $0. Task 6 runs last, after everything is on `main`.
