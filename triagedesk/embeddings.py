"""Voyage AI embeddings. One embedding per ticket, reused by retrieve + gate."""

import voyageai

from triagedesk.config import settings
from triagedesk.models import EMBED_DIMS

EMBED_MODEL = "voyage-3.5-lite"

_client: voyageai.Client | None = None


def _vo() -> voyageai.Client:
    global _client
    if _client is None:
        _client = voyageai.Client(api_key=settings.voyage_api_key or None)
    return _client


def embed_documents(texts: list[str]) -> list[list[float]]:
    return _vo().embed(
        texts, model=EMBED_MODEL, input_type="document", output_dimension=EMBED_DIMS
    ).embeddings


def embed_query(text: str) -> list[float]:
    return _vo().embed(
        [text], model=EMBED_MODEL, input_type="query", output_dimension=EMBED_DIMS
    ).embeddings[0]
