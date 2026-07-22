# RESUME HERE — Week 4 state + how to continue

**Any new session starts with this file.** Last updated: 2026-07-21 — **#56
and #58 both CLOSED, merged to `main`, deployed and verified live.**
Console: https://triage-desk-xi.vercel.app · API:
https://agenticproject-production.up.railway.app.

> The **operating manual** (environment facts, per-task choreography, budget
> rules, binding decisions) lives in
> [`../week-2-evals/HANDOFF.md`](../week-2-evals/HANDOFF.md) — still applies
> verbatim. Week 3 deploy facts: [`../week-3-console/HANDOFF.md`](../week-3-console/HANDOFF.md).
> This file holds only Week 4 state.

---

## 🚨 NEXT ACTION (before anything else): the eval-gate is writing into PROD

**Confirmed finding, not a guess.** The eval-gate CI job (`.github/workflows/eval.yml`)
reads `DATABASE_URL` from the `EVAL_DATABASE_URL` GitHub secret. The Week 3
HANDOFF recorded that secret as pointing at the **dev** Neon branch. It no
longer does — on the 2026-07-20 eval-gate run (triggered by merging PR #59),
**25 golden-set eval runs landed in the production database**, the same one
the public console reads from.

**Evidence:** the eval-gate log shows `n_cases: 25`, `cost_total: $0.719022`,
`judge_cost_total: $0.160035`, running 16:12:32–16:25:49 UTC on 2026-07-20.
Querying prod's `/api/runs` for that exact window returns **exactly 25 rows**,
timestamped 16:12:35–16:25:06, ticket subjects matching the golden set (VPN
disconnect, dedicated IP, security incident, etc.) — not real demo-pool
traffic. The count and window match too precisely to be coincidence.

**Likely cause:** the `EVAL_DATABASE_URL` secret was probably repointed at
prod during the Week 3 Task 6 deploy session (2026-07-18), when Railway's own
`DATABASE_URL` was being configured against the new `prod` Neon branch — an
easy secret-name mixup during a live joint session, never caught because no
eval-gate ran between then and the 2026-07-20 merge (PR #57 was `console/**`
only, $0 gate, no eval-gate trigger).

**Impact:**
- Every future eval-gate run pollutes the "glass-box" run history a
  recruiter can browse with synthetic golden-set runs, indistinguishable
  from real demo traffic without checking the ticket subject against the
  known 25-case set.
- Cost isolation is also gone: eval-gate spend and demo spend are now the
  same ledger. The demo's $1/day cap and the eval-gate's $1 cost-cap could
  in theory interact (not yet observed, but untested).
- This is an **infra/secrets change** — I did not touch it. Fixing it means
  creating (or re-verifying) a dedicated Neon eval branch and updating the
  `EVAL_DATABASE_URL` GitHub secret to point at it, which needs your Neon
  dashboard access.

**Also caused by a separate, second mechanism:** this session's own local
verification runs (for #58's live-progress feature and its follow-up polish)
were run with a local `uvicorn` pointed at prod's `DATABASE_URL` too — my
mistake, confirmed by matching run ids between local and prod `/api/runs`.
That's `TRIAGEDESK_ENV_FILE` / local env, unrelated to the CI secret, but it
added more non-demo runs to prod's history this week. See the correction
note in `reports/task-live-progress.md`.

**Suggested fix (do first, before more eval-gate runs):**
1. Confirm/create a dedicated Neon **eval** branch (separate from `dev` and
   `prod` — the Week 3 HANDOFF already flagged wanting this, now it's urgent
   rather than a nice-to-have).
2. Point the `EVAL_DATABASE_URL` GitHub secret at it; re-run migrations there.
3. When testing locally against a real API, always set
   `DATABASE_URL`/`TRIAGEDESK_ENV_FILE` explicitly to a non-prod branch and
   verify with one `curl .../api/runs?limit=1` id-match check before trusting
   "local" isolation, the way this session should have.
4. The 25 golden-set runs already in prod are real, harmless data (nothing
   sent to a real customer, no cost breach) — leaving them is fine; flagging
   this so a future session doesn't mistake them for demo-pool activity when
   reading run history.

---

## Week 4 progress

| Item | Issue | State |
|---|---|---|
| Console redesign — flight-recorder identity, dark-only, cockpit-stack landing | #56 | ✅ merged `b66aa78` (PR #57, squash) — **CLOSED**, `console/**`-only, $0 gate |
| Live run progress — demo watches the pipeline execute; backend moved to `BackgroundTasks` | #58 | ✅ merged `cb69291` (PR #59, squash) — **CLOSED**, touches `triagedesk/**` ⇒ eval-gate fired, **PASSED**, $0.879 |
| Post-merge polish (not separately issued, same PR #59 branch before merge) | — | ✅ typed-headline rotation bugfix + dynamic height, one-stage-at-a-time lifecycle pulse (was trailing), expandable run/review cards, page transitions, Home nav, GitHub repo links, readable agent-reply prose (`white-space: pre-wrap` + bold) |
| Demo video | #17 | not started |
| Case study + `results/` + final README | #18 | not started |

**Deferred, tracked verbally (not yet an issue):** seed one demo-pool ticket
that's genuinely auto-resolvable (KB-answerable, no denial), to prove the
gate *can* auto-resolve rather than always escalating — every current
demo-pool ticket is deliberately adverse-action-shaped by design, so 100%
escalation there is correct behavior, not a defect. Open as an issue before
acting on it (council/golden-set discipline applies — no hand-tuning the
gate).

## 🌐 Live deployment facts (re-verified 2026-07-21, after PR #59 merge)

| Thing | Value |
|---|---|
| Console | https://triage-desk-xi.vercel.app — confirmed serving the new build (`/runs`, `/demo` 200; landing markup includes the new "Lifecycle" panel + GitHub source link) |
| API | https://agenticproject-production.up.railway.app — `GET /api/runs` and `GET /api/demo/pool` both 200 |
| CI on `main` | `ci` ✅ success · `eval-gate` ✅ success (PASSED, $0.879) — both on merge commit `cb69291` |
| DB | Neon `prod` branch — **also currently receiving eval-gate golden-set runs, see finding above** |

## Budget

Week-3 close was **≈$9.6 of $20**. Since then:
- PR #57 (#56): $0 (console/docs-only, no gate).
- PR #59 (#58) eval-gate: **$0.879** (`$0.719022` eval + `$0.160035` judge),
  confirmed from the CI log, gate **PASSED**.
- Demo-pool verification runs this session (mislabeled "dev branch" in the
  task report — see correction): **8 runs, $0.3007 exact** (queried from
  prod `/api/runs`, 2026-07-19T08:29 through 2026-07-20T19:59, the 25
  golden-set runs excluded by timestamp window).
- **Running total: $9.6 + $0.879 + $0.3007 ≈ $10.78 of $20.** The 25
  golden-set eval runs' $0.879 is already counted via the eval-gate line —
  don't double-count it if re-deriving from prod's raw run list.

## ✅ Verify at session start (30 seconds)

- `curl https://agenticproject-production.up.railway.app/api/runs?limit=1` →
  200 with a run. If down, check Railway deployments (failed pre-deploy
  migration is the usual cause after a schema change — none happened this
  week, so unlikely).
- `gh run list --branch main --limit 2` → both `ci` and `eval-gate` (if
  triggered) should read `success`.
- Read the eval-gate finding above before running any eval-path merge again.
