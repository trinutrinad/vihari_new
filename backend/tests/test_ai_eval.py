"""AI evaluation harness tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD, seed_all


def _admin_headers(client: TestClient) -> dict[str, str]:
    login = client.post(
        "/api/v1/auth/login",
        json={"email": DEMO_ADMIN_EMAIL, "password": DEMO_ADMIN_PASSWORD},
    )
    assert login.status_code == 200, login.text
    token = login.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_eval_cases_and_full_run(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    cases = client.get("/api/v1/ai/eval/cases")
    assert cases.status_code == 200
    catalog = cases.json()["data"]
    assert len(catalog) >= 6
    ids = {item["id"] for item in catalog}
    assert "rag-monsoon-pack" in ids
    assert "rag-refuse-unverified-fee" in ids

    unauth = client.post("/api/v1/ai/eval/run", json={})
    assert unauth.status_code == 401

    admin = _admin_headers(client)
    run = client.post("/api/v1/ai/eval/run", headers=admin, json={})
    assert run.status_code == 200, run.text
    body = run.json()["data"]
    assert body["total"] == len(catalog)
    assert body["passed"] + body["failed"] == body["total"]
    assert body["pass_rate"] >= 0.8
    assert body["metrics"]["by_kind"]
    failed = [item for item in body["results"] if not item["passed"]]
    assert failed == [], failed


def test_eval_subset_run(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    admin = _admin_headers(client)
    run = client.post(
        "/api/v1/ai/eval/run",
        headers=admin,
        json={"case_ids": ["chat-weekend-smoke", "planner-goa-smoke"]},
    )
    assert run.status_code == 200, run.text
    body = run.json()["data"]
    assert body["total"] == 2
    assert body["passed"] == 2
