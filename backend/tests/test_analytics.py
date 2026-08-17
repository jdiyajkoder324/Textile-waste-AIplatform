def test_sustainability_dashboard_requires_auth(client):
    res = client.get("/api/analytics/sustainability")
    assert res.status_code == 401


def test_sustainability_dashboard_empty_state(client, auth_headers):
    """Edge case: no data yet — should return zeros, not crash."""
    res = client.get("/api/analytics/sustainability", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["overall_sustainability_score"] == 0.0
    assert body["rating_distribution"] == {}


def test_recycler_dashboard_forbidden_for_industry_role(client, auth_headers):
    """Industry role should NOT access the Recycler-only dashboard."""
    res = client.get("/api/analytics/recycler", headers=auth_headers)
    assert res.status_code == 403


def test_admin_dashboard_forbidden_for_non_admin(client, auth_headers):
    res = client.get("/api/analytics/admin", headers=auth_headers)
    assert res.status_code == 403


def test_admin_dashboard_accessible_for_admin(client, admin_headers):
    res = client.get("/api/analytics/admin", headers=admin_headers)
    assert res.status_code == 200
    assert "total_users" in res.json()


def test_manufacturer_dashboard_scoped_to_own_user(client, auth_headers):
    res = client.get("/api/analytics/manufacturer", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["total_production_waste_kg"] == 0.0


def test_analytics_invalid_date_range_handled_gracefully(client, auth_headers):
    """Edge case: end_date before start_date shouldn't 500."""
    res = client.get(
        "/api/analytics/sustainability",
        params={"start_date": "2026-12-31", "end_date": "2026-01-01"},
        headers=auth_headers,
    )
    assert res.status_code == 200  # empty result set, not an error