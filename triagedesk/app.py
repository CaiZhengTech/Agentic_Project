import uuid
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from triagedesk.config import settings
from triagedesk.console_queries import get_run_detail, list_review_queue, list_runs
from triagedesk.db import get_db
from triagedesk.logging_setup import configure_json_logging
from triagedesk.models import ReviewDecision, Run, Ticket

app = FastAPI(title="TriageDesk")

if settings.log_json:
    configure_json_logging()

# CORS is fail-closed: an empty cors_origins means NO cross-origin access, so the
# cleanest way to express that is to not register the middleware at all rather than
# add it with an empty allow_origins list. No wildcard is ever used. The console's
# requests are JSON POSTs carrying a custom auth header, so the preflight needs both
# that header and Content-Type explicitly allowed.
_cors_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if _cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["X-Admin-Token", "Content-Type"],
    )


class ReviewDecisionIn(BaseModel):
    decision: Literal["approve", "reject"]
    note: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int, db: Session = Depends(get_db)) -> dict:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="ticket not found")
    return {
        "id": ticket.id,
        "subject": ticket.subject,
        "body": ticket.body,
        "queue": ticket.queue,
        "language": ticket.language,
        "source": ticket.source,
    }


@app.get("/api/runs")
def api_list_runs(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)) -> dict:
    return list_runs(db, limit=limit, offset=offset)


@app.get("/api/runs/{run_id}")
def api_get_run(run_id: uuid.UUID, db: Session = Depends(get_db)) -> dict:
    detail = get_run_detail(db, run_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="run not found")
    return detail


@app.get("/api/review-queue")
def api_review_queue(db: Session = Depends(get_db)) -> dict:
    return list_review_queue(db)


@app.post("/api/review/{run_id}", status_code=201)
def api_post_review(
    run_id: uuid.UUID,
    body: ReviewDecisionIn,
    x_admin_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    # Fail closed: an unset admin token must never mean open, regardless of
    # what header the caller sends.
    if not settings.admin_token:
        raise HTTPException(status_code=503, detail="admin token not configured")
    if x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="invalid admin token")

    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")

    existing = db.execute(
        select(ReviewDecision).where(ReviewDecision.run_id == run_id)
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=409, detail="run already has a decision")

    decision = ReviewDecision(run_id=run_id, decision=body.decision, note=body.note)
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return {"id": decision.id}
