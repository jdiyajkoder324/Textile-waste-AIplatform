def test_register_creates_user(client):
    res = client.post("/user/register", json={
        "name": "New User", "email": "new@test.com", "password": "Pass1234", "role": "Industry",
    })
    assert res.status_code == 200
    assert res.json()["email"] == "new@test.com"


def test_register_duplicate_email_fails(client, test_user):
    res = client.post("/user/register", json={
        "name": "Dup", "email": test_user.email, "password": "Pass1234", "role": "Industry",
    })
    assert res.status_code == 400


def test_login_sends_otp(client, test_user):
    res = client.post("/user/login", json={"email": test_user.email, "password": "TestPass123"})
    assert res.status_code == 200
    body = res.json()
    assert "otp_session_id" in body
    assert "@" in body["email_hint"]


def test_login_wrong_password_fails(client, test_user):
    res = client.post("/user/login", json={"email": test_user.email, "password": "WrongPass"})
    assert res.status_code == 401


def test_me_requires_valid_token(client):
    res = client.get("/user/me")
    assert res.status_code == 401


def test_me_returns_user_with_valid_token(client, auth_headers):
    res = client.get("/user/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "industry@test.com"