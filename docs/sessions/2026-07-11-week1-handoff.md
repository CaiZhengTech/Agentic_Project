# Session Handoff — 2026-07-11 (Week 1 execution, Tasks 1–5)

**Read this first when resuming.** It records everything done and decided in the 2026-07-10/11
sessions so work continues without re-derivation. Detailed per-task record lives in
`.superpowers/sdd/progress.md` (git-ignored scratch — survives locally, not on GitHub).

## Where things stand

**Executing the Week 1 plan** (`docs/superpowers/plans/2026-07-10-week1-pipeline-skeleton.md`)
via superpowers subagent-driven development: fresh implementer subagent per task → independent
reviewer per task → fix loops → controller merges. **5 of 9 tasks complete.**

| Task | Issue | State |
|---|---|---|
| 1 Scaffolding + CI | #1 | ✅ merged (PR #20 → `9ccf497`), issue closed + closeout comment |
| 2 DB models + Alembic | #2 | ✅ merged (PR #21 → `67d6f3b`), issue closed + closeout comment |
| 3 Ticket ingest | #2 | ✅ same PR; **11,922 EN tickets live in Neon dev DB** (provably exact) |
| 4 Tracing layer | #3 | ✅ merged (PR #22 → `3fa3a70`), issue closed + closeout comment |
| 5 Schemas + LLM client | #4 | ✅ approved; **UNMERGED on `feat/04-precheck-classify` (PR #23 open)** — issue #4 spans Tasks 5+6; merge after Task 6 |
| 6 Prompts + precheck/classify | #4 | ⏭ NEXT — dispatch onto `feat/04-precheck-classify` |
| 7 KB docs + embeddings + retrieve | #5 | pending (KB authoring has a 2h timebox, no TDD ceremony) |
| 8 Tools + act loop | #6 | pending — **gated by the live-SDK spike (see council verdict)** |
| 9 Centroids + gate + runner + CLI + E2E | #7 | pending — Week 1 kill-criterion checkpoint |

**Environment (all verified live):** Neon dev+test branches (Postgres 18.4, pgvector, migrations
applied to both), Voyage key (1024-dim confirmed), Anthropic key, `TEST_DATABASE_URL` set as
GitHub Actions secret, `.venv` on **Python 3.13** (plan re-pinned from 3.12 — machine has 3.13/3.14
only). Issue #19 (friend labeling favor) closed — ask sent; labels optional, merge under #11 if
they arrive.

## Decisions made today (binding)

1. **Pipeline model switched: Opus 4.8 → `claude-sonnet-4-6` at effort high** (Cai's call).
   Effort defaults to high on 4.6; act loop additionally sets `output_config={"effort":"high"}` +
   `thinking={"type":"adaptive"}`; structured calls stay plain. Pricing $3/$15 (cache 3.75/0.30).
   Side effects: per-run cost comfortably under the $0.10 cap; Week-2 judge can run temp 0 on the
   same model (Sonnet 4.6 accepts `temperature` — the old Opus conflict is RESOLVED).
2. **Per-issue closeout comments** are now standing process (saved to memory:
   `issue-closeout-comments`): at every issue close, post what-was-built / how-it-went /
   decisions / next. Issues #1–#3 backfilled.
3. **Plans get reconciliation notes when review supersedes plan code** (see plan's Task 5
   `llm.py` block).

## THE incident of the day (drives tomorrow's first moves)

**Task 5's `structured_call` was plan-code with 4 green mocked tests and was provably broken
against the real SDK:** the repair/refusal path was unreachable (`messages.parse()` raises
`ValidationError` internally before returning), the repair turn stacked two consecutive `user`
messages (API 400), and `output_format=` is deprecated. A reviewer caught it by reading the
installed SDK's source (`anthropic==0.116.0`). Redesigned (commit `8e3e55e`): `messages.create` +
`output_config={"format": {"type": "json_schema", "schema": ...}}` + self-validation via
`schema.model_validate_json`; real validation errors fed into the repair prompt; exceptions
(`RepairFailedError`, `LLMRefusalError`) share a `StructuredCallError` base carrying `.responses`.
Re-review verified every shape against the installed SDK. **Root cause: code + tests written from
API memory; fakes simulated a state the real SDK never produces.**

## Council verdict (llm-council ran today on "green-light Tasks 6–9?")

Unanimous: don't pause, but **de-risk Task 8 before writing it** — the act loop codes against
more unverified SDK surface (tool_use, `pause_turn`, thinking blocks) and currently nothing makes
a live API call until Task 9, which is also the kill-criterion gate. Peer review sharpened the
prescription. **Adopted next actions, in order:**

1. **Task 6 now** on `feat/04-precheck-classify` — brief amended to also fix `config.py`:
   drop the hardcoded Windows secrets-path default (publishes the username in a public repo);
   path comes only from `TRIAGEDESK_ENV_FILE` env var. Cai must set that env var locally
   (`setx TRIAGEDESK_ENV_FILE "C:\Users\Wonton Soup\.secrets\credentials.env"`). Merge PR #23
   after review → closes #4 (+ closeout comment).
2. **Task 7** normally (KB docs 2h timebox + embeddings + retrieve) → closes #5.
3. **Before Task 8: the live-SDK spike** (controller runs it, ~$0.05, throwaway script):
   a **multi-turn tool_use exchange** against the installed SDK, deliberately provoking the
   stop reasons the loop branches on (tool_use, max_tokens; pause_turn if cheaply reachable);
   print raw response objects AND `usage` fields; **commit captured shapes as a test fixture**
   (e.g. `tests/fixtures/`) and amend Task 8's dispatch so mocks are built from the fixture,
   not from the plan's imagined shapes.
4. **Task 8** (act loop) → closes #6. **Task 9** (gate/runner/CLI + Dana E2E + adverse-action
   E2E) → closes #7 = Week 1 checkpoint; fire `how-we-got-here` after.
5. **Final whole-branch review** (most capable model) gets an added mandate: sweep Tasks 1–4
   for the same latent bug class (green mocks over unverified SDK assumptions), plus triage the
   deferred minors ledger.
6. **Add to plan's Global Constraints:** standing rule — *new SDK surface → live smoke +
   committed fixture before coding against it.*

## Deferred minors (ledgered, for the final review — do NOT fix mid-sprint)

- starlette/httpx deprecation warning in test output (pin compatible versions eventually)
- ingest loop: no rollback/close guard; CSV opened without `newline=""`; `--limit 0` falsy edge
- tracing: no exactly-at-cap test (`>` semantics); `record_llm_usage` could raise bare
  `AttributeError` on a response lacking `.model`/`.usage`
- Task 2 implementer report cited ruff violations that don't match the committed migration (doc nit)

## How to resume tomorrow

1. Read this doc + `.superpowers/sdd/progress.md`; `git log --oneline -10` to confirm state
   (main at `8a02453`+, `feat/04-precheck-classify` at `8e3e55e`, PR #23 open).
2. Confirm Cai has set `TRIAGEDESK_ENV_FILE` (or fold the setx step into Task 6's manual notes).
3. Dispatch Task 6 per item 1 above (subagent-driven; brief via `scripts/task-brief PLAN 6`;
   base commit = `8e3e55e` on the feature branch). Continue the loop.
