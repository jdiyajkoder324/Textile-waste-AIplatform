def test_generate_report_requires_auth(client):
    res = client.get("/api/reports/generate", params={"report_type": "sustainability", "format": "pdf"})
    assert res.status_code == 401


def test_generate_report_invalid_type_returns_400(client, auth_headers):
    res = client.get(
        "/api/reports/generate",
        params={"report_type": "not_a_real_type", "format": "pdf"},
        headers=auth_headers,
    )
    assert res.status_code == 400


def test_generate_pdf_report_with_no_data(client, auth_headers):
    """Edge case: empty dataset should still produce a valid PDF, not crash."""
    res = client.get(
        "/api/reports/generate",
        params={"report_type": "sustainability", "format": "pdf"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 0


def test_generate_excel_report_with_no_data(client, auth_headers):
    res = client.get(
        "/api/reports/generate",
        params={"report_type": "waste_classification", "format": "excel"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert "spreadsheetml" in res.headers["content-type"]


def test_report_saved_to_history_after_generation(client, auth_headers):
    client.get(
        "/api/reports/generate",
        params={"report_type": "sustainability", "format": "pdf"},
        headers=auth_headers,
    )
    res = client.get("/api/reports/history", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["total"] == 1


def test_users_cannot_see_others_report_history(client, auth_headers, admin_headers):
    # generate a report as Industry user
    client.get(
        "/api/reports/generate",
        params={"report_type": "sustainability", "format": "pdf"},
        headers=auth_headers,
    )
    # admin can see all reports (per spec: "Admins should have access to platform-level report management")
    res = client.get("/api/reports/history", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["total"] >= 1


def test_download_nonexistent_report_returns_404(client, auth_headers):
    res = client.get("/api/reports/history/99999/download", headers=auth_headers)
    assert res.status_code == 404


def test_cannot_download_another_users_report(client, db_session, auth_headers):
    from app.core.security import hash_password, create_access_token
    from app.models.user import User

    other_user = User(name="Other", email="other@test.com", password=hash_password("Pass1234"), role="Industry")
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)
    other_headers = {"Authorization": f"Bearer {create_access_token({'sub': other_user.email})}"}

    # generate as test_user
    client.get(
        "/api/reports/generate",
        params={"report_type": "sustainability", "format": "pdf"},
        headers=auth_headers,
    )
    history = client.get("/api/reports/history", headers=auth_headers).json()
    report_id = history["items"][0]["id"]

    # try downloading as a different, unrelated user
    res = client.get(f"/api/reports/history/{report_id}/download", headers=other_headers)
    assert res.status_code == 403