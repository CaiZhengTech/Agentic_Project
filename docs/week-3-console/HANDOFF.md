# RESUME HERE — Week 3 state + how to continue

**Any new session starts with this file.** Last updated: 2026-07-17 (session ended by
Cai's request after Wk3 Task 3; Task 4 deliberately NOT started).

> The **operating manual** (environment facts, per-task choreography, budget rules,
> binding decisions, the three standing deliverables) lives in
> [`../week-2-evals/HANDOFF.md`](../week-2-evals/HANDOFF.md) — it all still applies
> verbatim. This file holds only Week 3 state. One fact, one home.

---

## ▶️ NEXT ACTION: dispatch Task 4 — the console review-queue page (issue #14, UI half)

Everything it needs is ready and merged:

1. `git checkout main && git pull` — record BASE.
2. Regenerate the brief: `"$S/task-brief" docs/week-3-console/PLAN.md 4` (S = the
   subagent-driven-development scripts dir; see the operating manual).
3. Dispatch ONE implementer (sonnet), branch `feat/14-review-queue-page`. Context the
   brief can't know, carry it in the dispatch:
   - Task 3's API is merged: `GET /api/review-queue` → `{items: [run-summary fields +
     internal_rationale + final_reply], total}` (oldest first); `POST /api/review/{run_id}`
     body `{"decision": "approve"|"reject", "note": str}` + header `X-Admin-Token` →
     201 / **401 wrong token / 503 token unset (fail closed) / 409 already reviewed /
     404 / 422**.
   - Console conventions from Tasks 2: plain CSS via `globals.css` variables,
     `lib/api.ts` typed fetch helpers (`NEXT_PUBLIC_API_URL`, localhost:8000 default),
     server components + one narrow client component where interaction demands it,
     root `error.tsx` already exists. NO new dependencies.
   - Local API for manual verification: `export TRIAGEDESK_ENV_FILE=…` then
     `.venv/Scripts/python -m uvicorn triagedesk.app:app --port 8000`; set `ADMIN_TOKEN`
     in the env for the happy path AND unset it once to see the 503. Dev DB has ~198
     escalated runs to fill the queue. **A row that was decided must disappear** —
     verify live, and note the DB write it creates is permanent (fine — it's the dev DB
     and the table exists there via the merged migration).
   - Review-queue POST must only ever be issued from rows the queue returned (the API
     doesn't re-check run state — Task 3 review minor, in the ledger).
4. Review (reviewer gets the brief + report + review-package diff + the same binding
   constraints), fix loop if needed, merge — **console/** only ⇒ NO eval-gate cost.
5. Deliverables in the same breath (Cai's standing rule, re-confirmed 2026-07-17: after
   EVERY task, immediately — never batched): chat explanation · analogy comment on #14
   → **then CLOSE #14** (both halves done) · STORY.md chapter · ledger row + minors.

## ✅ Verify at session start (30 seconds)

- Eval-gate run **29555275667** (triggered by PR #52's merge — the session's one billed
  API-wave run, expected ~$0.90) was `in_progress` when the session ended. Confirm it
  went **green**: `gh run view 29555275667`. If red, STOP and diagnose before Task 4
  (a red here means the review-queue migration or API change moved a guarded number —
  unlikely but the gate exists for exactly this). Then record its actual cost (from the
  run log's `cost_total` + `judge_cost_total`) in the ledger budget table (placeholder
  row says "~$0.90 pending").

## Week 3 state

| Task (plan) | Issue | State |
|---|---|---|
| 1 Runs read API (list + detail) | #13 | ✅ merged `360b1d0` (PR #50), review clean |
| 2 Console scaffold + run list/detail | #13 | ✅ merged `9f41aaa` (PR #51), review clean (1 Important fixed: error boundary) — **#13 CLOSED** |
| 3 review_decisions + queue API + admin token | #14 | ✅ merged `f760367` (PR #52), review clean |
| 4 Console review-queue page | #14 | ▶️ **NEXT** (brief regenerates from PLAN.md Task 4) |
| 5 Deploy-prep: CORS + JSON logs | #15 | ⬜ after Task 4 |
| 6 Live deploy Railway+Neon+Vercel + smoke — **controller + Cai** (needs his accounts) | #15 | ⬜ last |
| 7 Demo protection (pool, rate limit, visible spend-cap pause) + smoke script | #16 | ⬜ after 5 |

**Plan:** `docs/week-3-console/PLAN.md` (canonical; global constraints at top are binding
— note especially the **gate-cost rule**: `triagedesk/**`/`alembic/**`/`requirements.txt`/
`kb/**`/baseline merges each trigger a ~$0.90 eval-gate run; batch API merges back-to-back
and cancel superseded queued runs, keep only the last; `console/**` and docs are free).
**Descope ladder if the week overruns (cut in order):** smoke test → JSON logs → per-IP
rate limit. The daily spend cap is NEVER cut.

## Budget

≈ **$8.6 of $20** after this session (see the ledger's table; the pending item is run
29555275667's actual cost). Week 3's remaining live spend: Task 6's smoke run (~3¢) +
Task 5/7 API-wave gate run (~$0.90) + demo-protection gate run if merged separately
(avoid — batch 5+7).

## Standing items to fold in when convenient

- Dedicated Neon eval branch (`EVAL_DATABASE_URL` still points at dev).
- Second rater for judge calibration (chore #19) — the kappa bottleneck is single-rater
  label noise, NOT judge quality (see `results/judge-calibration.md`).
- Seed at least one `completed` run before the demo (dev DB currently has zero — the
  console's completed-row styling is code-verified only).
