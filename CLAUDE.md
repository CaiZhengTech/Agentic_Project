# TriageDesk — Project CLAUDE.md

AI support-ticket triage agent with a "glass-box" ops console. Portfolio project targeting
Northeast US (NYC/Boston) new-grad SWE roles, fall 2026 cycle. The differentiator is NOT the
agent — it's the eval/observability/trust discipline around it (market research: eval design
is the #1 hiring signal; plain RAG demos are a yellow flag).

## Status (updated 2026-07-11)

**Week 1 implementation IN PROGRESS — 5 of 9 plan tasks done.**
**→ RESUME HERE: read `docs/sessions/2026-07-11-week1-handoff.md`** (full state, decisions,
council verdict, and the exact next dispatch). Per-task detail: `.superpowers/sdd/progress.md`.

- **Week 1 plan committed:** `docs/superpowers/plans/2026-07-10-week1-pipeline-skeleton.md`
  (9 tasks covering issues #1–#7; executed via superpowers:subagent-driven-development)
- **Done + merged:** issues #1 (scaffolding+CI), #2 (DB layer + 11,922 tickets ingested),
  #3 (tracing layer). Issue #19 (friend favor) closed. Each closed issue carries a
  closeout comment (standing preference — keep doing this).
- **In flight:** issue #4 half-done — Task 5 (schemas + LLM client) approved on
  `feat/04-precheck-classify` (PR #23 OPEN); Task 6 lands on the same branch, then merge.
- **Model decision (2026-07-11, supersedes spec's Opus mention):** pipeline pinned to
  `claude-sonnet-4-6`, effort high; adaptive thinking in the act loop only. Judge can run
  temp 0 on the same model (old conflict resolved).
- **Key incident:** plan's `structured_call` was broken against the real SDK despite green
  mocked tests; redesigned + SDK-verified. Council verdict (5 advisors + peer review):
  continue, but Task 8 is GATED on a live-SDK spike whose responses get committed as test
  fixtures. Details + adopted action list in the handoff doc.

**Spec remains the design record:** `docs/superpowers/specs/2026-07-10-triagedesk-design.md`.

## Development process (issue-driven — follow this)

- **Issues = tracking layer** (lean: goal, acceptance criteria, deps). **Plan docs =
  canonical layer** (code-level detail, `docs/superpowers/plans/`, one per week).
  If they ever conflict, update the issue to match the plan.
- Work order = the number in the issue title. Per issue: branch → TDD → PR referencing
  the issue → disciplined self-review via the PR checklist → merge closes it.
- Non-code issues (KB doc authoring, the friend favor) get NO branch/PR/TDD ceremony.
- superpowers discipline throughout; fire `how-we-got-here` after backend/AI-ML/infra work.

### Issue explanation format (Cai's chosen learning style — keep using it)
Every issue has a collapsible `<details>` "🧠 Understanding this issue" section with fixed
template: In one sentence (for anyone) / Where it sits (ASCII diagram + YOU ARE HERE) /
Problem / Analogy / One ticket's journey / What breaks without it (disaster story) /
Jargon glossary / Feeds into. **The recurring worked example is "Dana's VPN ticket"**
("My VPN keeps disconnecting — client demo at 3pm"; adverse-action variant: Dana requests
a premium feature her plan excludes). Reuse Dana in all future explanations, docs, demo,
and case study — continuity is the point. Full preference saved in session memory
(`explanation-format-preference`).

## Locked stack (do not relitigate)
- Python / FastAPI / SQLAlchemy 2.0 / Alembic
- Postgres on Neon free tier, pgvector extension (NO separate vector DB)
- Hand-written agent loop on the Anthropic SDK — deliberately NO LangChain (interview story)
- Thin Next.js console on Vercel; API on Railway via Nixpacks (NO Docker anywhere —
  Windows/WSL2 friction; integration tests hit a Neon test branch, locally and in CI)
- GitHub Actions CI; Kaggle "Customer IT Support" dataset (Tobias Bueck); ~15 authored KB
  docs, whole-doc embeddings, k=3, no chunking/tuning

## Architecture (summary — spec is the full record)
Pipeline: pre-check → classify → retrieve (pgvector) → act loop (tools:
`lookup_account_status`, `check_entitlement`) → multi-signal confidence gate →
auto-resolve / escalate to human review queue. Run states: `completed | escalated |
failed` (loop exhaustion = escalated with reason `agent_incomplete`). Failed runs are
simply visible in the console — no dead-letter workflow. Traces use OTel GenAI semantic
conventions (`gen_ai.*`) stored in hand-rolled Postgres tables. 7 tables: tickets, runs,
spans, kb_docs, eval_cases, eval_results, review_decisions.

## Non-negotiable design rules
- **Adverse-action rule:** the agent never autonomously delivers a customer-facing denial;
  those always route to the review queue. Internal rationale is always logged (trace =
  evidence, LLM rationale = post-hoc context, never ground truth).
- **Fail closed on cost:** per-run cap ~$0.10; if cost can't be computed, treat as breach
  → escalate.
- **Gate never uses LLM self-reported confidence** — retrieval similarity + classification
  margin only (validated by the Wk2 calibration table before adding signals).
- **Evals-first.** Judge: pinned model, temp 0, pass/fail/`needs_review`, calibrated vs
  ~40–50 human labels (Cohen's kappa).
- Retries: 429/5xx, backoff, max 3 / 60s. Pydantic + ONE repair re-prompt. Tool errors:
  once, then escalate.

## Checkpoints and kill criteria (set while calm — not negotiable mid-project)
- **End of Wk1 (issue #7):** one ticket end-to-end through all 5 stages, however crude.
  If not green → spend Wk4 buffer hours immediately; NEVER compress Wk2.
- **End of Wk2 (issue #12):** CI eval gate green, or console is cut to one read-only page.
- **Wk3 descope ladder (cut in order):** post-deploy smoke test → JSON logs → per-IP rate
  limit. The daily spend cap is never cut.
- Everything deliberately cut (contract tests, nightly evals, Docker, cached demo
  fallback, waterfall visuals, real OTel export) gets one "what I'd add in production"
  paragraph in the case study — do not quietly add these back.

## 4-week plan (part-time, ~45–50h total — top of budget)
- **Wk1 (issues 01–07):** scaffolding+CI → DB+ingest → tracing layer → pre-check+classify
  → KB+retrieve → act loop → gate+CLI dump. Error handling built INLINE (one-touch rule).
- **Wk2 (issues 08–12):** golden set (25, 5 adversarial) → deterministic harness +
  calibration table → judge → kappa calibration → CI eval gate.
- **Wk3 (issues 13–16):** console run list/detail → review queue → deploy
  (Railway+Neon+Vercel) → demo protection (seeded pool, rate limit, visible spend-cap pause).
- **Wk4 (issues 17–18):** demo video → case study + `results/` folder + final README
  (adversarial catch rate as standalone headline number).

## Working conventions (this project)
- Secrets: `C:\Users\Wonton Soup\.secrets\credentials.env` only; `.gitignore` already
  covers `.env*`; `.env.example` documents required vars. Verify coverage before commits.
- Durable learnings → vault raw source (`raw/YYYY-MM-DD-<slug>.md`) → SCREEN → INGEST.
- Scope discipline: the design survived four council rounds that hunted over-engineering.
  Before adding anything, check it against the hour budget, the ladders, and the cuts list.
