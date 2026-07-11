from types import SimpleNamespace

from tests.conftest import integration
from tests.unit.test_precheck_classify import FakeTracer
from triagedesk.models import EMBED_DIMS, KbDoc
from triagedesk.pipeline import retrieve


def unit_vec(hot: int) -> list[float]:
    v = [0.0] * EMBED_DIMS
    v[hot] = 1.0
    return v


@integration
def test_top_k_by_cosine_similarity(test_db, monkeypatch):
    test_db.add_all([
        KbDoc(slug="vpn", title="VPN", content="vpn doc", embedding=unit_vec(0)),
        KbDoc(slug="billing", title="Billing", content="billing doc", embedding=unit_vec(1)),
        KbDoc(slug="email", title="Email", content="email doc", embedding=unit_vec(2)),
        KbDoc(slug="sales", title="Sales", content="sales doc", embedding=unit_vec(3)),
    ])
    test_db.commit()

    # query points almost exactly at the vpn doc
    q = [0.0] * EMBED_DIMS
    q[0], q[1] = 0.9, 0.1
    monkeypatch.setattr(retrieve, "embed_query", lambda text: q)

    ticket = SimpleNamespace(id=1, subject="vpn drops", body="vpn keeps dropping")
    result = retrieve.run_retrieve(ticket, FakeTracer(), test_db)

    assert len(result.docs) == 3
    assert result.docs[0].slug == "vpn"
    assert result.top_similarity > 0.9
    assert result.query_embedding == q
