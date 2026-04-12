from __future__ import annotations

from tests.conftest import login


def test_login_required_for_dashboard(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_successful_login(client):
    response = login(client, "owner")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_invalid_login(client):
    response = login(client, "owner", "bad-password")
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data
