# Week 2.5 — Post-Council Eval-Layer Hardening Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:test-driven-development per task.
> Each `### Task N:` section is self-contained (sliced by `task-brief`). Tasks 1–2 are code
> ($0, TDD); Task 3 is controller-only (analysis + the single live re-baselining run).

**Why this plan exists:** the 2026-07-14 llm-council bug hunt (verdict recorded in chat +
issue comment) found that the headline eval numbers are tautologies of total conservatism,
the adversarial catch metric never checks WHICH defense layer fired, the pipeline runs at
unpinned temperature beneath zero-slack baseline floors, and the calibration queries are
unscoped across suite reruns. Cai's decisions (2026-07-14): fix the judge's tool-blindness
NOW (he relabels this week) and bundle gate-threshold re-derivation into the same single
live re-baselining run.

## Global constraints (binding)

- All Week-2 binding rules apply (hold-out rule; fail-closed on cost; judge never ground
  truth; gate never uses LLM self-reported confidence; SDK-reality rule).
- **$0 for implementers.** No Anthropic/Voyage calls, no live runs, no workflow triggers.
  Unit tests = fixtures/fakes only. The controller performs every live step in Task 3.
- **Schema changes only via Alembic migration.** Read `docs/00-spec/DATA-SCHEMA.md` before
  any query — never guess column names.
- The committed `results/eval-baseline.json` is NOT updated by implementers — the
  controller re-derives it from the Task-3 live run.

---

### Task 1: Metric integrity — reason-aware catch, cap pre-check, cost clarity

**Acceptance criteria (binding):**
1. `adversarial_catch_rate` counts a case as caught **only if** `predicted_outcome ==
   "escalate"` AND the observed `escalation_reason` matches the case's
   `expected_escalation_reason`. Cases with no `expected_escalation_reason` (NULL) fall
   back to outcome-only matching. A secondary metric `adversarial_escalate_rate`
   (outcome-only, the old definition) is kept in the summary for continuity.
2. The suite cost cap becomes a **pre-check**: before dispatching each case, if
   `total_cost + PER_RUN_CAP` would exceed `cost_cap`, raise `SuiteCostExceeded` BEFORE
   spending (the cap is a ceiling, not a tripwire). Keep the existing post-hoc check as
   a backstop.
3. Cost clarity: `summarize()` additionally reports `judge_cost_total` (sum of judge call
   costs, currently only accumulated into the cap variable in `run_suite`), and the
   docstring/report language for `cost_per_run` states it is **pipeline-only** cost.

**Files:** modify `triagedesk/evals/metrics.py`, `triagedesk/evals/harness.py`
(CaseResult gains `escalation_reason` + `expected_escalation_reason` if not already
carried; judge cost threaded to summarize), tests in `tests/unit/test_metrics.py` /
`test_harness.py` (extend existing files, follow their fixture style).

**TDD steps:** failing tests first for: (a) adversarial case escalated for the WRONG
reason (e.g. expected `precheck_injection`, observed `agent_requested_human`) →
catch_rate excludes it but escalate_rate includes it; (b) NULL expected reason → outcome
fallback; (c) cap pre-check: 3 fake cases, cap set so case 3 would breach → suite stops
after case 2, `SuiteCostExceeded`, case 3 never dispatched; (d) `judge_cost_total`
surfaces in summary.

---

### Task 2: Calibration scoping, weighted kappa, kappa CI, judge tool-evidence, pinned temperature, golden view

**Acceptance criteria (binding):**
1. **eval_run_id scoping:** `export_labels`, `compute_kappa_report` (and `label-import`
   validation) accept an optional `eval_run_id`; default = **latest judged row per
   case_id** (deterministic: max `eval_run_id` by row id), so CI reruns can no longer
   duplicate rows in the export or mix non-independent repeats into kappa. `label-export`
   never blanks/re-emits rows that already carry a `human_label` unless `--include-labeled`
   is passed.
2. **Weighted kappa + CI:** `kappa.py` gains `cohens_kappa_linear_weighted(labels_a,
   labels_b, ordering=("fail","needs_review","pass"))` (hand-rolled, no scipy) and
   `bootstrap_kappa_ci(labels_a, labels_b, n_boot=2000, seed=0)` returning a (lo, hi)
   95% percentile interval using `random.Random(seed)` — deterministic. The calibrate
   report prints unweighted kappa, weighted kappa, and the CI, clearly labeled.
3. **Judge tool-evidence (the tool-blindness fix):** `judge_reply` gains an
   `account_context: str | None` block rendered into the prompt as
   `<account_facts>…</account_facts>` with an instruction that these are verified CRM/tool
   facts the agent legitimately used. `judge_run` builds it deterministically: the
   simulated CRM is pure — `customer_ref_for(ticket)` → `lookup_account_status(ref)` (and
   plan entitlements from `PLAN_ENTITLEMENTS`) reproduce exactly what the agent's tools
   returned. No new DB columns. The judge rubric line changes from "grounded in the KB
   articles" to "grounded in the KB articles or the verified account facts."
   **This creates a new judge version:** bump the judge prompt-version constant (grep for
   how judge identifies itself; add `JUDGE_PROMPT_VERSION = "2"` recorded in
   `judge_reason`? NO — keep simple: a module constant included in the calibration report
   header so pre/post-fix kappas are never conflated).
4. **Pinned temperature:** `precheck` and `classify` pass `temperature=0` through
   `structured_call` (the act loop stays default — it uses adaptive thinking by design;
   document this in a one-line comment). Existing tests asserting kwargs must be updated
   deliberately, not deleted.
5. **Golden view:** one Alembic migration creating the Postgres view
   `eval_results_golden` = `eval_results` JOIN `eval_cases` filtered
   `kind <> 'calibration'`, exposing the columns Week 3's console needs (result fields +
   `kind`, `expected_outcome`, `adversarial_kind`). Downgrade drops the view. Document the
   view in `docs/00-spec/DATA-SCHEMA.md` (one new subsection — it is the ONLY sanctioned
   read path for golden metrics from non-Python consumers).

**Files:** `triagedesk/evals/calibration.py`, `triagedesk/evals/kappa.py`,
`triagedesk/evals/judge.py`, `triagedesk/evals/cli.py`, `triagedesk/pipeline/precheck.py`,
`triagedesk/pipeline/classify.py`, new Alembic revision, `docs/00-spec/DATA-SCHEMA.md`,
tests: extend `test_kappa.py`, `test_calibration.py`, `test_judge.py`, pipeline tests.

**TDD steps:** failing tests first for: (a) two judged rows same case_id different
eval_run_id → export/report use only the latest; (b) labeled rows excluded from re-export
by default; (c) weighted kappa hand-checked value (compute one 2×2 example by hand in the
test comment); (d) bootstrap CI deterministic for fixed seed, contains the point estimate;
(e) judge prompt includes `<account_facts>` when context passed, omits block when None;
(f) precheck/classify calls carry `temperature=0` (adjust the existing
`"temperature" not in kwargs` test to target the act loop only); (g) migration
upgrade/downgrade round-trips (integration-marked, skipped without TEST_DATABASE_URL).

---

### Task 3 (CONTROLLER ONLY — live): threshold re-derivation + judge re-backfill + single re-baselining run

Not for implementers. Sequence: (1) re-derive gate thresholds from HELD-OUT data + the
Task-4 calibration table (never the golden 25); commit the new thresholds with the
derivation written into `docs/week-2-evals/reports/threshold-derivation.md`; (2) re-judge
all judged replies with the tool-evidence judge (`judge-backfill`, ~15¢) → fresh blind
`label-export` for Cai's relabel → new kappa (weighted + CI) in
`results/judge-calibration.md`, clearly versioned pre/post-fix; (3) ONE live suite run
(~$0.72–0.9) under pinned temperature + new metrics + new thresholds → re-derive
`results/eval-baseline.json` floors from it (regression-floor framing stays) → confirm
`eval-gate` green on main; (4) docs: PITCH reframing ("recall 1.0 under a deliberately
conservative config" → whatever the new truthful numbers are; catch rate described as
per-intended-layer), ledger, SESSION-LOG, HANDOFF.

## Deferred to the Week-3 backlog (recorded, not lost)

- Mid-suite resume / stuck-`running` reaper (council A2) — with the deploy task.
- `requirements.lock` for the eval workflow + model-ID snapshot verification (A4).
- Commit-SHA ↔ `eval_run_id` lineage (E5) — natural fit when the console displays runs.
- Eval-gate failure notification beyond GitHub's default actor email (E1).
- Second human rater for kappa (friend labels, chore #19) — merge if they arrive.
