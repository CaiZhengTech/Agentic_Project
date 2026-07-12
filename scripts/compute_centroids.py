"""Per-queue centroid embeddings from labeled Kaggle tickets (up to 100/queue).

The gate's classification margin = sim(ticket, predicted queue centroid) minus
the best sim to any OTHER centroid — an external signal, not LLM self-report.
Output is committed (triagedesk/data/queue_centroids.json) so runs and tests
are deterministic and CI never calls Voyage.
"""

import json
import time
from pathlib import Path

from triagedesk.db import SessionLocal
from triagedesk.embeddings import embed_documents
from triagedesk.models import Ticket
from triagedesk.schemas import QUEUES

PER_QUEUE = 100
OUT = Path("triagedesk/data/queue_centroids.json")
# Voyage free tier (no payment method on file) caps at 3 RPM / 10K TPM. A
# batch of 100 real ticket texts (~10K tokens) trips the TPM cap on its own,
# so batches are kept well under that, paced to stay under the RPM cap too.
SUB_BATCH = 25
REQUEST_PAUSE_SECONDS = 21


def normalize(v: list[float]) -> list[float]:
    norm = sum(x * x for x in v) ** 0.5
    return [x / norm for x in v]


def main() -> None:
    session = SessionLocal()
    # Resumable: free-tier pacing makes a full run ~15 min, so each finished
    # queue is written immediately and skipped on re-run.
    centroids: dict[str, list[float]] = (
        json.loads(OUT.read_text()) if OUT.exists() else {}
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    for queue in QUEUES:
        if queue in centroids:
            print(f"{queue}: already computed, skipping", flush=True)
            continue
        tickets = (
            session.query(Ticket)
            .filter_by(queue=queue, language="en", source="kaggle")
            .limit(PER_QUEUE)
            .all()
        )
        texts = [f"{t.subject}\n{t.body}" for t in tickets]
        vectors = []
        for i in range(0, len(texts), SUB_BATCH):
            vectors += embed_documents(texts[i:i + SUB_BATCH])
            time.sleep(REQUEST_PAUSE_SECONDS)  # respect free-tier 3 RPM / 10K TPM
        dims = len(vectors[0])
        mean = [sum(v[d] for v in vectors) / len(vectors) for d in range(dims)]
        centroids[queue] = normalize(mean)
        OUT.write_text(json.dumps(centroids))
        print(f"{queue}: {len(vectors)} tickets", flush=True)
    session.close()
    print(f"Wrote {OUT} ({len(centroids)}/{len(QUEUES)} queues)")


if __name__ == "__main__":
    main()
