# Hardening Task 3 report — thresholds, judge-v2 backfill, re-baseline (controller-only, live) (Refs #45)

Executed 2026-07-16/17 by the controller per `HARDENING-PLAN.md` Task 3. Tasks 1–2 were
already merged (PRs #46, #47 — see their reports in this folder).

## 1. Threshold re-derivation ($0 → PR #48, `f112e29`)

Full derivation record: [`threshold-derivation.md`](threshold-derivation.md) — held-out
pool only (hold-out rule), `MARGIN_THRESHOLD` 0.02 → 0.0 (semantic zero),
`SIM_THRESHOLD` 0.45 re-grounded (~36th percentile held-out), leakage audit included.
Key honest finding: the gate signals carry **no reply-quality information** on held-out
data — quality assurance is carried by the structural rules, thresholds are
defense-in-depth on classification/retrieval evidence.

## 2. Judge-v2 re-backfill ($0.35, append-only)

- The 41 judged+human-labeled rows (golden `b58804d6` 19 + pool `3231c41d` 22) were
  **copied** into a fresh batch `eval_run_id = 69b3fa3d-e83e-46cf-b9bb-8c157ec3e74b`
  with judge/human columns cleared — v1 rows untouched (append-only evidence rule).
  Task 2's `eval_run_id` scoping makes the two batches cleanly separable forever.
- `triagedesk-evals judge --eval-run 69b3fa3d…` re-judged all 41 with the tool-evidence
  judge (`JUDGE_PROMPT_VERSION = 2`): **18 pass / 10 fail / 13 needs_review**, $0.3471
  (above the plan's ~15¢ estimate: 41 replies vs the 19-reply estimate base, plus the
  account-facts block lengthens the prompt).
- **Preview kappa** (v2 verdicts vs the v1-era human labels on the same replies — the
  judge is the only variable): raw agreement **0.512 → 0.634**, unweighted kappa
  **0.279 → 0.418**, weighted **0.551**, bootstrap 95% CI **(0.213, 0.607)**. Recorded
  in `results/judge-calibration.md`, clearly versioned. The OFFICIAL v2 kappa uses
  Cai's fresh blind pass on `judge_labels_v2.csv` (exported from the batch, 41 rows,
  verdicts withheld).

## 3. The live re-baselining run + validation (PR #49, `31b7f25`)

- The re-baselining run happened **as the push-triggered gate run of PR #48's merge**
  (workflow 29544082755, `eval_run d429d547`) — the first run under new thresholds +
  pinned temperature + reason-aware metrics + judge v2. Numbers: recall 1.00,
  precision 0.88, catch 1.00 (design-intent), **strict 0.60**, escalate 1.00, routing
  0.286, 2.96¢/run pipeline, judge $0.16, p50 34.7s, p95 46.5s. GREEN against the old
  baseline.
- `results/eval-baseline.json` re-derived from that run: new floors
  `adversarial_catch_rate_strict ≥ 0.60`, `adversarial_escalate_rate ≥ 1.00`; existing
  floors unchanged (observed behavior stable — model conservatism + receipt rule still
  bind, as the derivation predicted). Merged as PR #49; the push-triggered gate run
  validated the new baseline live (green).

## Deviations / incidents

1. **Three unplanned gate runs (~$2.7):** merging PRs #46/#47/#48 each push-triggered
   the eval gate (they touch `triagedesk/**` — the paths filter working as designed,
   but the plan budgeted ONE live run). Silver lining: PR #48's run WAS the planned
   re-baselining run, and the earlier two are free-in-hindsight regression evidence
   that the metric changes (run 1) and judge/temp changes (run 2) didn't move
   deterministic behavior. **Lesson (ledger):** batch eval-path merges within a session.
2. **Backfill cost $0.35 vs ~15¢ planned** (reason above; within budget).
3. The plan's "re-judge all judged replies" was implemented append-only (copy batch)
   rather than nulling v1 verdicts in place — preserves paid-for evidence and is
   exactly what Task 2's run-scoping was built for.

## Spend this session

| Item | Cost |
|---|---|
| Gate run — PR #46 merge (auto) | $0.905 |
| Gate run — PR #47 merge (auto) | $0.886 |
| Gate run — PR #48 merge (= the re-baselining run) | $0.900 |
| Judge-v2 backfill (41 replies) | $0.347 |
| Gate run — PR #49 merge (baseline validation) | ~$0.90 |
| **Session total** | **≈ $3.94** |

Project total ≈ **$7.7 of $20**.
