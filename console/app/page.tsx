import Link from "next/link";
import { listRuns } from "@/lib/api";
import { formatCost } from "@/lib/format";

export const metadata = {
  title: "TriageDesk — glass-box ticket triage",
};

const stateGlyph: Record<string, string> = {
  escalated: "⚠",
  failed: "✕",
  completed: "✓",
};

export default async function LandingPage() {
  const { runs, total } = await listRuns(3, 0);

  return (
    <main>
      <section className="hero">
        <p className="eyebrow boot boot-1">
          Glass-box ticket triage — every decision leaves evidence
        </p>
        <h1 className="boot boot-2">The AI never sends bad news on its own.</h1>
        <p className="hero-sub boot boot-3">
          An agent that triages support tickets — wrapped in evidence, cost
          caps, and human review. Every run below is real and traced end to
          end.
        </p>
        <div className="stats">
          <div className="stat stat-amber boot boot-4">
            <div className="stat-value">5/5</div>
            <div className="stat-label">Adversarial catch</div>
          </div>
          <div className="stat stat-green boot boot-5">
            <div className="stat-value">1.00</div>
            <div className="stat-label">Escalation recall</div>
          </div>
          <div className="stat boot boot-6">
            <div className="stat-value">2.9¢</div>
            <div className="stat-label">Avg cost / run</div>
          </div>
          <div className="stat boot boot-7">
            <div className="stat-value">0</div>
            <div className="stat-label">Unsafe auto-sends</div>
          </div>
        </div>
        <div className="ctas boot boot-8">
          <Link className="btn btn-primary" href="/demo">
            ▶ Run a live ticket
          </Link>
          <Link className="btn" href="/runs">
            Open the recorder
          </Link>
        </div>
      </section>

      <section className="ticker">
        <p className="eyebrow boot boot-9">Latest — {total} runs on record</p>
        {runs.map((run, i) => (
          <Link
            key={run.id}
            href={`/runs/${run.id}`}
            className={`ticker-row boot boot-${10 + i} ${run.state}`}
          >
            <span>{run.ticket_subject}</span>
            <span className={`ticker-state ${run.state}`}>
              {stateGlyph[run.state] ?? "·"} {run.state}
              {run.escalation_reason ? ` · ${run.escalation_reason}` : ""} ·{" "}
              {formatCost(run.total_cost_usd)}
            </span>
          </Link>
        ))}
      </section>
    </main>
  );
}
