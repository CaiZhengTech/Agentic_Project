# Hardening Task 2 — Calibration scoping, weighted kappa, kappa CI, judge tool-evidence, pinned temperature, golden view

Branch: `feat/45-calibration-judge-hardening` off `main` (`2edaed8`). Refs #45.

## What was implemented

### 1. `eval_run_id` scoping (`triagedesk/evals/calibration.py`)

`export_labels`, `compute_kappa_report`, and `import_labels` all accept an optional
`eval_run_id` keyword. A new `_judged_rows(session, eval_run_id=None)` helper is the single
scoping point for both export and the kappa report:

- Explicit `eval_run_id` → only rows from that one suite execution.
- Default (`None`) → `_scope_to_latest_per_case`: keeps only the highest-`id` (most recent)
  judged row per `case_id`, by max-by-id rather than "last one wins while iterating" (correct
  regardless of input order).

This stops CI reruns from duplicating rows in the blind-labeling export or mixing
non-independent repeats (the same ticket judged twice) into kappa's sample.

`export_labels` gained `include_labeled: bool = False` — rows that already carry a
`human_label` are excluded by default (re-exporting them would let a label get silently
blanked/re-emitted); `--include-labeled` on the CLI opts back in.

`import_labels` gained the same `eval_run_id` parameter for validation: when given, any CSV
row whose `result_id` belongs to a *different* eval_run raises `ValueError` rather than
silently mislabeling a superseded/unrelated row.

CLI (`triagedesk/evals/cli.py`): `label-export`/`label-import`/`calibrate` all gained
`--eval-run`; `label-export` gained `--include-labeled`.

### 2. Weighted kappa + CI (`triagedesk/evals/kappa.py`)

- `cohens_kappa_linear_weighted(labels_a, labels_b, ordering=("fail","needs_review","pass"))`
  — hand-rolled linear-weighted Cohen's kappa for the ordinal fail/needs_review/pass scale.
  `1 - (weighted observed disagreement) / (weighted expected disagreement)`, weight
  `w(i,j) = |i-j|/(k-1)`. Same degenerate contract as `cohens_kappa`: NaN (never a crash) on
  empty input or when expected disagreement is forced to 0.
- `bootstrap_kappa_ci(labels_a, labels_b, n_boot=2000, seed=0)` — percentile bootstrap 95% CI
  over unweighted `cohens_kappa`, using `random.Random(seed)` (not global `random` state) for
  determinism. Degenerate resamples (kappa NaN) are dropped from the percentile calculation.

`compute_kappa_report` now returns `kappa_weighted` and `kappa_ci` alongside the existing
keys, computed together with (and None for the same reason as) `kappa` when undefined.
`cli.py`'s `_render_calibration_md` prints all three, clearly labeled, plus a new
"Judge prompt version" header line.

### 3. Judge tool-evidence (`triagedesk/evals/judge.py`)

Root cause (Week 2 calibration, kappa 0.279): the judge only ever saw the KB, so it graded
7/7 genuine tool-derived facts (from the agent's own `lookup_account_status`/
`check_entitlement` calls) as invented.

- `judge_reply` gained `account_context: str | None = None`, rendered as a
  `<account_facts>...</account_facts>` block when given, omitted entirely when `None` (no
  stray empty tag).
- `judge_run` builds `account_context` deterministically via new `_account_facts_block(ticket)`:
  `customer_ref_for(ticket)` → `lookup_account_status(ref)` + plan entitlements from
  `PLAN_ENTITLEMENTS` — the exact same simulated-CRM inputs the agent's real tools read.
  Returns `None` (not a crash) when the ticket can't resolve a `customer_ref` (missing `id`,
  or an unknown seed account) — existing `judge_run` fixtures/tests predate this and have no
  ticket `id`, so they continue to see no account_facts block, unaffected.
- Judge rubric line changed: "must come from the KB articles below" →
  "must come from the KB articles or the verified account facts below"; system prompt tells
  the judge these facts are agent-tool-derived ground truth, not claims to verify.
- New module constant `JUDGE_PROMPT_VERSION = "2"`, printed in the calibration report header
  so pre/post-fix kappas can never be conflated.

### 4. Pinned temperature (`triagedesk/pipeline/precheck.py`, `classify.py`)

Both now pass `temperature=0` to `structured_call` (deterministic classification calls, no
sampling noise beneath eval-gate floors). The act loop (`triagedesk/pipeline/act.py`)
deliberately does **not** pin temperature — one-line comment added at its `messages.create`
call explaining adaptive thinking is the intended source of variation there.

Existing-test adjustment (controller resolution #3): `tests/unit/test_llm_repair.py`'s
`test_first_try_success` had a `"temperature" not in kwargs` assertion against the generic
`structured_call` (called directly, not through precheck/classify) — retargeted: that
assertion moved to `tests/unit/test_act_loop.py` (the correct place to assert "no pinned
temperature" now that precheck/classify do pin it), with an explanatory comment left in
`test_llm_repair.py` pointing at where the pinned/unpinned behavior is now actually tested.

### 5. `eval_results_golden` view

New Alembic revision `b2a3edf4a55a` (`alembic/versions/b2a3edf4a55a_eval_results_golden_view.py`,
`down_revision = 868d4d9166da`): creates view `eval_results_golden` = `eval_results` JOIN
`eval_cases` filtered `kind <> 'calibration'`, exposing every `eval_results` column plus
`kind`, `expected_outcome`, `adversarial_kind`. Downgrade drops the view. Documented in
`docs/00-spec/DATA-SCHEMA.md` (new subsection) as the **only sanctioned read path** for golden
metrics from non-Python consumers (Week 3's console).

## Testing

Full suite: `.venv/Scripts/python -m pytest -q` → **187 passed** (159 pre-existing + 28 new/
retargeted), 1 pre-existing unrelated warning (starlette/httpx deprecation). `ruff check .` →
all checks passed (one auto-fixed import-order issue in the new integration test file).

### TDD evidence per criterion

**(a) eval_run_id scoping — two judged rows, same case_id, different eval_run_id → latest only**

RED:
```
$ .venv/Scripts/python -m pytest -q tests/unit/test_calibration.py
FAILED ...test_export_uses_only_latest_row_per_case_when_ci_reran_the_suite
FAILED ...test_report_uses_only_latest_row_per_case_when_ci_reran_the_suite
FAILED ...test_export_scopes_to_an_explicit_eval_run_id
FAILED ...test_report_scopes_to_an_explicit_eval_run_id
11 failed, 19 passed
```
(export_labels/compute_kappa_report took no `eval_run_id` kwarg yet → `TypeError`.)

GREEN: same command → `30 passed`.

**(b) labeled rows excluded from re-export by default**

RED: `test_export_excludes_already_labeled_rows_by_default`,
`test_export_includes_labeled_rows_when_include_labeled_passed` failed in the same batch above
(`export_labels() got an unexpected keyword argument 'include_labeled'`).

GREEN: same `30 passed` run above.

**(c) weighted kappa hand-checked value**

RED:
```
$ .venv/Scripts/python -m pytest -q tests/unit/test_kappa.py
ImportError: cannot import name 'bootstrap_kappa_ci' from 'triagedesk.evals.kappa'
1 error during collection
```
Hand computation (see `test_linear_weighted_kappa_hand_checked_value` docstring): 3-category
ordinal example, n=4, joint counts (0,0)=1 (0,1)=1 (1,1)=1 (2,2)=1; observed weighted
disagreement = 0.125, expected = 0.4375 → weighted kappa = 1 − 0.125/0.4375 = **0.714**.
Unweighted kappa on the same data = (0.75 − 0.3125)/(1 − 0.3125) = **0.636** — different value,
proving the weighting isn't a no-op.

GREEN: `.venv/Scripts/python -m pytest -q tests/unit/test_kappa.py` → `16 passed`.

**(d) bootstrap CI deterministic for fixed seed, contains the point estimate**

RED: same collection error as (c) (`bootstrap_kappa_ci` didn't exist).

GREEN: `test_bootstrap_kappa_ci_deterministic_for_fixed_seed` (same seed → identical tuple)
and `test_bootstrap_kappa_ci_contains_point_estimate` (`lo <= cohens_kappa(...) <= hi`) both
pass in the 16-passed run above.

**(e) judge prompt includes `<account_facts>` when context passed, omits when None**

RED:
```
$ .venv/Scripts/python -m pytest -q tests/unit/test_judge.py
FAILED ...test_judge_reply_prompt_includes_account_facts_block_when_context_given
  TypeError: judge_reply() got an unexpected keyword argument 'account_context'
FAILED ...test_judge_run_builds_account_facts_deterministically_from_the_simulated_crm
  AssertionError: assert '<account_facts>' in '<ticket>...' (block never rendered)
FAILED ...test_judge_prompt_version_is_bumped_for_the_tool_evidence_fix
  ImportError: cannot import name 'JUDGE_PROMPT_VERSION'
3 failed, 9 passed
```

GREEN: `.venv/Scripts/python -m pytest -q tests/unit/test_judge.py` → `12 passed`.

**(f) precheck/classify carry temperature=0; act loop retargeted**

RED:
```
$ .venv/Scripts/python -m pytest -q tests/unit/test_precheck_classify.py
FAILED test_precheck_pins_temperature_zero — KeyError: 'temperature'
FAILED test_classify_pins_temperature_zero — KeyError: 'temperature'
2 failed, 4 passed
```

GREEN: `.venv/Scripts/python -m pytest -q tests/unit/test_precheck_classify.py
tests/unit/test_act_loop.py tests/unit/test_llm_repair.py` → `20 passed`.

**(g) migration upgrade/downgrade round-trip**

Integration-marked (`@integration`, skipif `not settings.test_database_url`). The shared Neon
test branch was reachable in this environment, so this ran live end-to-end rather than being
skipped (DDL only — CREATE/DROP VIEW, no Anthropic/Voyage calls, consistent with every other
integration test in this repo that reads/writes rows on the same branch).

Pre-flight check confirming the migration genuinely wasn't applied yet (RED evidence outside
pytest, since the test's own first action is the upgrade):
```
$ alembic current
868d4d9166da
```
(one revision behind `b2a3edf4a55a`, i.e. the view did not exist).

First run surfaced a real bug: after `command.downgrade`, `_view_exists(test_db)` still
returned `True` — the long-lived `test_db` ORM session's open transaction hadn't refreshed
its catalog snapshot after DDL committed on alembic's separate connection. Fixed by calling
`test_db.commit()` (ends the session's current transaction; nothing pending) between each
alembic step and the next check.

GREEN:
```
$ .venv/Scripts/python -m pytest -q tests/integration/test_eval_results_golden_view.py -v
tests\integration\test_eval_results_golden_view.py . [100%]
1 passed in 2.94s
```
Post-check confirming the branch was left at head with the view intact:
```
$ alembic current
b2a3edf4a55a (head)
```
Manually verified the view's column list and that it queries cleanly:
```
['id','eval_run_id','case_id','run_id','predicted_queue','predicted_outcome',
 'escalation_reason','cost_usd','latency_ms','retrieval_similarity',
 'classification_margin','routing_correct','outcome_correct','judge_verdict',
 'judge_reason','judge_rule_triggered','human_label','created_at','kind',
 'expected_outcome','adversarial_kind']
SELECT count(*) FROM eval_results_golden -> 0  (empty test branch, expected)
```

### Full suite (after all criteria implemented)
```
$ .venv/Scripts/python -m pytest -q
........................................................................ [ 38%]
........................................................................ [ 77%]
...........................................                              [100%]
187 passed, 1 warning in 21.43s
$ .venv/Scripts/python -m ruff check .
All checks passed!
```

## Files changed

- `triagedesk/evals/calibration.py` — scoping (`_judged_rows`, `_scope_to_latest_per_case`),
  `include_labeled`, `import_labels` eval_run_id validation, weighted kappa + CI in the report.
- `triagedesk/evals/kappa.py` — `cohens_kappa_linear_weighted`, `bootstrap_kappa_ci`.
- `triagedesk/evals/judge.py` — `account_context`, `_account_facts_block`,
  `JUDGE_PROMPT_VERSION`, rubric wording.
- `triagedesk/evals/cli.py` — `--eval-run` / `--include-labeled` flags, calibration markdown
  now includes weighted kappa, CI, and judge prompt version.
- `triagedesk/pipeline/precheck.py`, `triagedesk/pipeline/classify.py` — `temperature=0`.
- `triagedesk/pipeline/act.py` — one-line comment (no pinned temperature, by design).
- `alembic/versions/b2a3edf4a55a_eval_results_golden_view.py` — new migration.
- `docs/00-spec/DATA-SCHEMA.md` — new `eval_results_golden` subsection.
- Tests extended: `tests/unit/test_kappa.py`, `tests/unit/test_calibration.py`,
  `tests/unit/test_judge.py`, `tests/unit/test_precheck_classify.py`,
  `tests/unit/test_act_loop.py`, `tests/unit/test_llm_repair.py`.
- New: `tests/integration/test_eval_results_golden_view.py`.

## Self-review findings

- **Fixture change flagged, not hidden:** `test_calibration.py`'s `make_result` default
  `case_id` changed from a shared `1` to `id_` (each row its own case by default) — required
  once scoping groups by `case_id`; documented inline in the fixture. Verified it doesn't
  change any pre-existing assertion (none of the old tests checked `case_id` values).
- **Real bug caught and fixed during (g):** the ORM-session-snapshot issue described above —
  not a pre-existing bug, an artifact of the test's own design; fixed in the test, not the
  migration.
- Nothing added beyond the 5 acceptance criteria and the controller's binding resolutions
  (no CLI flags beyond what criterion 1 explicitly named; no schema changes beyond the one
  view; `results/eval-baseline.json` and `results/judge-calibration.md` untouched — the
  latter stays in its pre-fix form since no live `calibrate` run was performed here, per the
  $0 budget).
- Degenerate/edge cases: empty label lists and single-category-both-raters samples verified
  to return `None`/NaN (never crash) for kappa, weighted kappa, and the CI alike.
- Test output is pristine — no new warnings.
