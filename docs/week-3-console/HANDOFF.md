# RESUME HERE — Week 3 state + how to continue

**Any new session starts with this file.** Last updated: 2026-07-17 (later — **Wk3 Task 4
done, #14 CLOSED**; the console is feature-complete [run list · run detail · review queue].
Next action: Task 5 [deploy-prep code], batched with Task 7 for one gate run).

> The **operating manual** (environment facts, per-task choreography, budget rules,
> binding decisions, the three standing deliverables) lives in
> [`../week-2-evals/HANDOFF.md`](../week-2-evals/HANDOFF.md) — it all still applies
> verbatim. This file holds only Week 3 state. One fact, one home.

---

## ▶️ NEXT ACTION: Task 5 — deploy-prep code (CORS + JSON logs, issue #15, code half)

The console is done; deploy is the next arc. **Task 5 touches `triagedesk/**` ⇒ it will
trigger the ~$0.90 eval gate. Task 7 (demo protection) ALSO touches `triagedesk/**` —
BATCH them: build both, review both, merge back-to-back, cancel superseded queued
`eval-gate` runs so ONE gate run bills for the wave.** Task 6 (live deploy, needs Cai's
Railway/Vercel accounts) runs last, after 5+7 are on main. Recipe:

1. `git checkout main && git pull` — record BASE.
2. `"$S/task-brief" docs/week-3-console/PLAN.md 5` (and `... 7` when you get there).
3. Dispatch ONE implementer (sonnet), branch `feat/15-deploy-prep`. Task 5 adds
   `CORSMiddleware` (origins from `settings.cors_origins`, comma-separated, **fail closed:
   empty = no cross-origin**), a stdlib JSON log formatter (`triagedesk/logging_setup.py`,
   applied when `settings.log_json`), and the two new settings in `.env.example`. Full
   spec: PLAN.md "### Task 5". **This is what unblocks the review-queue page's cross-origin
   POST** — the console→API preflight that Task 4 documented as a known gap.
4. Review → fix loop → hold the merge to batch with Task 7 (see the gate-cost rule above).
5. Per-task deliverables each time (chat explanation · analogy comment on #15/#16 ·
   STORY.md chapter · ledger row + minors).

## ✅ Verify at session start (30 seconds)

- **Gate run 29555275667 confirmed GREEN** (PR #52's API-wave run; 11m18s), actual cost
  **$0.887** ($0.726 base + $0.161 judge) — recorded in the ledger. No pending gate at
  session start now. The Task-4 merge (PR #53) was **console-only ⇒ triggered no gate**
  ($0). Next billed gate = the Task 5+7 API wave (batch it).

## Week 3 state

| Task (plan) | Issue | State |
|---|---|---|
| 1 Runs read API (list + detail) | #13 | ✅ merged `360b1d0` (PR #50), review clean |
| 2 Console scaffold + run list/detail | #13 | ✅ merged `9f41aaa` (PR #51), review clean (1 Important fixed: error boundary) — **#13 CLOSED** |
| 3 review_decisions + queue API + admin token | #14 | ✅ merged `f760367` (PR #52), review clean |
| 4 Console review-queue page | #14 | ✅ merged `4f51143` (PR #53), review APPROVE-WITH-MINORS (1 dead-CSS Minor fixed in-PR) — **#14 CLOSED** |
| 5 Deploy-prep: CORS + JSON logs | #15 | ▶️ **NEXT** (batch its merge with Task 7) |
| 6 Live deploy Railway+Neon+Vercel + smoke — **controller + Cai** (needs his accounts) | #15 | ⬜ last |
| 7 Demo protection (pool, rate limit, visible spend-cap pause) + smoke script | #16 | ⬜ after 5 |

**Plan:** `docs/week-3-console/PLAN.md` (canonical; global constraints at top are binding
— note especially the **gate-cost rule**: `triagedesk/**`/`alembic/**`/`requirements.txt`/
`kb/**`/baseline merges each trigger a ~$0.90 eval-gate run; batch API merges back-to-back
and cancel superseded queued runs, keep only the last; `console/**` and docs are free).
**Descope ladder if the week overruns (cut in order):** smoke test → JSON logs → per-IP
rate limit. The daily spend cap is NEVER cut.

## Budget

≈ **$8.6 of $20** (run 29555275667 finalized at $0.887; Task 4 merge was $0). Week 3's
remaining live spend: the Task 5+7 API-wave gate run (~$0.90, ONE run if batched) +
Task 6's smoke run (~3¢).

## Standing items to fold in when convenient

- Dedicated Neon eval branch (`EVAL_DATABASE_URL` still points at dev).
- Second rater for judge calibration (chore #19) — the kappa bottleneck is single-rater
  label noise, NOT judge quality (see `results/judge-calibration.md`).
- Seed at least one `completed` run before the demo (dev DB currently has zero — the
  console's completed-row styling is code-verified only).
