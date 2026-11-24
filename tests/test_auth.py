def test_register_and_login(client):
    res = client.post("/api/auth/register", json={"username": "Neha", "password": "nehapass123"})
    assert res.status_code == 201
    assert res.json()["username"] == "neha" and res.json()["role"] == "user"

    login = client.post("/api/auth/login", data={"username": "neha", "password": "nehapass123"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["username"] == "neha"


def test_duplicate_username_rejected(client):
    body = {"username": "dup_user", "password": "password123"}
    assert client.post("/api/auth/register", json=body).status_code == 201
    assert client.post("/api/auth/register", json=body).status_code == 409


def test_register_validation(client):
    assert client.post("/api/auth/register", json={"username": "ab", "password": "password123"}).status_code == 422
    assert client.post("/api/auth/register", json={"username": "valid_name", "password": "short"}).status_code == 422
    assert client.post("/api/auth/register", json={"username": "bad name!", "password": "password123"}).status_code == 422


def test_wrong_password(client, user_headers):
    res = client.post("/api/auth/login", data={"username": "asha", "password": "nope-nope-nope"})
    assert res.status_code == 401


def test_protected_routes_need_token(client):
    assert client.get("/api/tasks").status_code == 401
    assert client.get("/api/items").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_health_and_index(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/").status_code == 200
