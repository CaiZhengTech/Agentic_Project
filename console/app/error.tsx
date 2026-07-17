"use client";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main style={{ padding: "2rem", maxWidth: 1100, margin: "0 auto" }}>
      <h1>Can&apos;t reach the TriageDesk API</h1>
      <p style={{ color: "var(--muted)" }}>
        The run data couldn&apos;t be loaded — check that the API is up and{" "}
        <code style={{ backgroundColor: "transparent", padding: 0 }}>
          NEXT_PUBLIC_API_URL
        </code>{" "}
        is correct.
      </p>
      <div
        style={{
          backgroundColor: "var(--failed-bg)",
          border: `1px solid var(--failed-border)`,
          borderRadius: "4px",
          padding: "1rem",
          marginBottom: "1rem",
          fontFamily: "monospace",
          fontSize: "0.9rem",
          color: "var(--foreground)",
          overflowX: "auto",
        }}
      >
        <code>{error.message}</code>
      </div>
      <button
        onClick={reset}
        style={{
          padding: "0.5rem 1rem",
          fontSize: "1rem",
          border: `1px solid var(--border)`,
          borderRadius: "4px",
          backgroundColor: "transparent",
          color: "var(--foreground)",
          cursor: "pointer",
        }}
      >
        Try again
      </button>
    </main>
  );
}
