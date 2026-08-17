def test_list_notifications_requires_auth(client):
    res = client.get("/api/notifications")
    assert res.status_code == 401


def test_list_notifications_empty_initially(client, auth_headers):
    res = client.get("/api/notifications", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["items"] == []
    assert body["unread_count"] == 0


def test_announcement_requires_admin(client, auth_headers):
    res = client.post("/api/notifications/announcements", json={
        "title": "Test", "message": "Hello", "priority": "medium",
    }, headers=auth_headers)
    assert res.status_code == 403


def test_admin_can_create_announcement(client, admin_headers):
    res = client.post("/api/notifications/announcements", json={
        "title": "Platform Update", "message": "New features live", "priority": "medium",
    }, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Platform Update"


def test_mark_read_nonexistent_notification_returns_404(client, auth_headers):
    res = client.patch("/api/notifications/99999/read", headers=auth_headers)
    assert res.status_code == 404


def test_alert_checks_requires_admin(client, auth_headers):
    res = client.post("/api/notifications/check-alerts", headers=auth_headers)
    assert res.status_code == 403


def test_alert_checks_runs_without_error_on_empty_data(client, admin_headers):
    """Edge case: no waste/sustainability data exists yet — must not crash."""
    res = client.post("/api/notifications/check-alerts", headers=admin_headers)
    assert res.status_code == 200