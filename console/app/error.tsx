"use client";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main>
      <h1>Can&apos;t reach the TriageDesk API</h1>
      <p className="muted">
        The run data couldn&apos;t be loaded — check that the API is up and{" "}
        <code>NEXT_PUBLIC_API_URL</code> is correct.
      </p>
      <div
        className="panel panel-pad error-text"
        style={{ borderColor: "var(--red)", overflowX: "auto" }}
      >
        <code>{error.message}</code>
      </div>
      <button onClick={reset}>Try again</button>
    </main>
  );
}
