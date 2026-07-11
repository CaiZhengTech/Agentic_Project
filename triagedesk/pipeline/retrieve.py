from dataclasses import dataclass

from triagedesk.embeddings import EMBED_MODEL, embed_query
from triagedesk.models import KbDoc


@dataclass
class RetrievalResult:
    docs: list[KbDoc]
    top_similarity: float
    query_embedding: list[float]


K = 3


def run_retrieve(ticket, tracer, session) -> RetrievalResult:
    with tracer.span("retrieve") as span:
        query = f"{ticket.subject}\n{ticket.body}"
        q_vec = embed_query(query)

        distance = KbDoc.embedding.cosine_distance(q_vec)
        rows = (
            session.query(KbDoc, distance.label("distance"))
            .order_by(distance)
            .limit(K)
            .all()
        )
        docs = [row[0] for row in rows]
        sims = [round(1.0 - row[1], 4) for row in rows]

        tracer.set_attributes(
            span,
            **{
                "gen_ai.operation.name": "embeddings",
                "gen_ai.request.model": EMBED_MODEL,
                "retrieval.k": K,
                "retrieval.doc_slugs": [d.slug for d in docs],
                "retrieval.similarities": sims,
            },
        )
        return RetrievalResult(
            docs=docs,
            top_similarity=sims[0] if sims else 0.0,
            query_embedding=q_vec,
        )
