"""Embed kb/*.md whole-doc into kb_docs (upsert by slug). Run after editing docs."""

from pathlib import Path

from triagedesk.db import SessionLocal
from triagedesk.embeddings import embed_documents
from triagedesk.models import KbDoc

KB_DIR = Path("kb")


def main() -> None:
    paths = sorted(KB_DIR.glob("*.md"))
    if not paths:
        raise SystemExit("no kb/*.md files found")
    contents = [p.read_text(encoding="utf-8") for p in paths]
    vectors = embed_documents(contents)

    session = SessionLocal()
    for path, content, vec in zip(paths, contents, vectors, strict=True):
        slug = path.stem
        title = content.splitlines()[0].lstrip("# ").strip()
        doc = session.query(KbDoc).filter_by(slug=slug).one_or_none()
        if doc is None:
            doc = KbDoc(slug=slug)
            session.add(doc)
        doc.title, doc.content, doc.embedding = title, content, vec
    session.commit()
    session.close()
    print(f"Embedded {len(paths)} docs.")


if __name__ == "__main__":
    main()
